import openai
import anthropic
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import datetime
import asyncio
import pandas as pd

from app.config import settings


class LLMService:
    def __init__(self, user_api_keys: Optional[Dict[str, str]] = None):
        """Initialize LLM service with user-specific API keys or fallback to system keys"""
        self.openai_client = None
        self.anthropic_client = None
        
        # Use user-specific API keys if provided, otherwise fallback to system keys
        openai_key = None
        anthropic_key = None
        
        if user_api_keys:
            openai_key = user_api_keys.get("openai_api_key")
            anthropic_key = user_api_keys.get("anthropic_api_key")
        
        # Fallback to system keys if user keys not available
        if not openai_key:
            openai_key = settings.openai_api_key
        if not anthropic_key:
            anthropic_key = settings.anthropic_api_key
        
        # Initialize clients
        if openai_key and self._is_valid_openai_key(openai_key):
            self.openai_client = openai.OpenAI(api_key=openai_key)
        
        if anthropic_key and self._is_valid_anthropic_key(anthropic_key):
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
    
    def _is_valid_openai_key(self, key: str) -> bool:
        """Check if OpenAI API key format is valid"""
        return (
            key and 
            key != "your-openai-api-key-here" and
            key.startswith("sk-") and
            len(key) > 20
        )
    
    def _is_valid_anthropic_key(self, key: str) -> bool:
        """Check if Anthropic API key format is valid"""
        return (
            key and 
            key != "your-anthropic-api-key-here" and
            key.startswith("sk-ant-") and
            len(key) > 20
        )
    
    def has_openai_client(self) -> bool:
        """Check if OpenAI client is available"""
        return self.openai_client is not None
    
    def has_anthropic_client(self) -> bool:
        """Check if Anthropic client is available"""
        return self.anthropic_client is not None
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models based on configured API keys"""
        available_models = []
        
        if self.has_openai_client():
            for model in settings.LLM_MODELS["openai"]["models"]:
                available_models.append({
                    **model,
                    "provider": "openai",
                    "available": True
                })
        
        if self.has_anthropic_client():
            for model in settings.LLM_MODELS["anthropic"]["models"]:
                available_models.append({
                    **model,
                    "provider": "anthropic", 
                    "available": True
                })
        
        return available_models
    
    def get_token_recommendations(self, chunk_size: int) -> Dict[str, int]:
        """Get token recommendations based on chunk size"""
        input_tokens = chunk_size // 4  # Rough estimation: 1 token ≈ 4 characters
        
        # Calculate recommended output tokens (1.5-2x input tokens for annotation tasks)
        min_tokens = max(100, input_tokens // 2)
        max_tokens_limit = min(4000, input_tokens * 3)
        default_tokens = min(2000, input_tokens * 2)
        
        return {
            "min_tokens": min_tokens,
            "max_tokens_limit": max_tokens_limit,
            "default_tokens": default_tokens,
            "input_tokens_estimate": input_tokens
        }
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 50) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks for processing"""
        if len(text) <= chunk_size:
            return [{"text": text, "start_char": 0, "end_char": len(text), "chunk_id": 0}]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                last_period = text.rfind('.', start, end)
                last_exclamation = text.rfind('!', start, end)
                last_question = text.rfind('?', start, end)
                
                best_break = max(last_period, last_exclamation, last_question)
                
                if best_break > start + chunk_size - 200:
                    end = best_break + 1
            
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "start_char": start,
                "end_char": end,
                "chunk_id": chunk_id
            })
            
            # Move start position with overlap
            start = end - overlap
            chunk_id += 1
        
        return chunks
    
    async def run_annotation_pipeline(
        self,
        text: str,
        tag_definitions: List[Dict[str, Any]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        chunk_size: int = 1000,
        overlap: int = 50
    ) -> Dict[str, Any]:
        """Run the complete annotation pipeline with chunking"""
        
        # Convert tag definitions to DataFrame format for prompt building
        tag_df = pd.DataFrame(tag_definitions)
        
        # Chunk the text
        chunks = self.chunk_text(text, chunk_size, overlap)
        
        all_entities = []
        total_input_tokens = 0
        total_output_tokens = 0
        chunk_results = []
        failed_chunks = 0
        
        for chunk in chunks:
            try:
                # Annotate chunk
                result = await self.annotate_text(
                    chunk["text"],
                    tag_df,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Adjust entity positions to global text positions
                chunk_entities = result.get("annotations", [])
                for entity in chunk_entities:
                    if "start_char" in entity and "end_char" in entity:
                        entity["start_char"] += chunk["start_char"]
                        entity["end_char"] += chunk["start_char"]
                        entity["chunk_id"] = chunk["chunk_id"]
                        all_entities.append(entity)
                
                total_input_tokens += result.get("input_tokens", 0)
                total_output_tokens += result.get("output_tokens", 0)
                
                chunk_results.append({
                    "chunk_id": chunk["chunk_id"],
                    "entities_found": len(chunk_entities),
                    "input_tokens": result.get("input_tokens", 0),
                    "output_tokens": result.get("output_tokens", 0)
                })
                
            except Exception as e:
                failed_chunks += 1
                error_msg = str(e)
                
                # Check for critical errors that should fail the entire pipeline
                if any(critical in error_msg.lower() for critical in [
                    "api key", "authentication", "unauthorized", "invalid_api_key",
                    "permission denied", "billing", "quota exceeded"
                ]):
                    print(f"💥 Critical error in chunk {chunk['chunk_id']}: {error_msg}")
                    raise Exception(f"Annotation failed due to API authentication/authorization issue: {error_msg}")
                
                chunk_results.append({
                    "chunk_id": chunk["chunk_id"],
                    "error": error_msg,
                    "entities_found": 0,
                    "input_tokens": 0,
                    "output_tokens": 0
                })
                
                print(f"⚠️  Chunk {chunk['chunk_id']} failed: {error_msg}")
        
        # If all chunks failed, this is a critical error
        if failed_chunks == len(chunks):
            raise Exception(f"All {len(chunks)} chunks failed during annotation. Last error: {chunk_results[-1].get('error', 'Unknown error') if chunk_results else 'No chunks processed'}")
        
        # Remove duplicate entities from overlapping chunks
        all_entities = self._remove_duplicate_entities(all_entities)
        
        # Validate and fix entity positions
        validated_entities = self._validate_entity_positions(text, all_entities)
        
        return {
            "entities": validated_entities,
            "statistics": {
                "total_entities": len(validated_entities),
                "chunks_processed": len(chunks),
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens
            },
            "chunk_results": chunk_results
        }
    
    async def annotate_text(
        self,
        text: str,
        tag_definitions: Dict[str, Any],
        model: str = "gpt-4",
        temperature: float = 0.1,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """Annotate text using specified LLM model"""
        
        if model.startswith("gpt"):
            return await self._annotate_with_openai(
                text, tag_definitions, model, temperature, max_tokens
            )
        elif model.startswith("claude"):
            return await self._annotate_with_claude(
                text, tag_definitions, model, temperature, max_tokens
            )
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    async def _annotate_with_openai(
        self,
        text: str,
        tag_definitions: Any,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Annotate using OpenAI GPT models"""
        
        if not self.openai_client:
            raise Exception("OpenAI client not initialized. Please check your API key configuration.")
        
        system_prompt = self._create_system_prompt(tag_definitions)
        user_prompt = self._create_user_prompt(text)
        
        print(f"🤖 Making OpenAI API call with model: {model}")
        print(f"📝 Text length: {len(text)} characters")
        print(f"🏷️  Tag definitions: {len(tag_definitions) if hasattr(tag_definitions, '__len__') else 'Unknown'}")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            print(f"✅ OpenAI response received: {len(result_text)} characters")
            
            try:
                annotations = json.loads(result_text)
                print(f"📊 Parsed annotations: {len(annotations.get('annotations', []))} entities")
            except json.JSONDecodeError as json_error:
                print(f"❌ JSON parsing error: {json_error}")
                print(f"🔍 Response content: {result_text[:500]}...")
                raise Exception(f"Failed to parse JSON response: {json_error}")
            
            return {
                "annotations": annotations.get("annotations", []),
                "confidence_scores": annotations.get("confidence_scores", {}),
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _annotate_with_claude(
        self,
        text: str,
        tag_definitions: Any,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Annotate using Anthropic Claude models"""
        
        system_prompt = self._create_system_prompt(tag_definitions)
        user_prompt = self._create_user_prompt(text)
        
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            result_text = response.content[0].text
            annotations = json.loads(result_text)
            
            # Claude provides token counts in usage
            input_tokens = response.usage.input_tokens if hasattr(response, 'usage') else len(system_prompt + user_prompt) // 4
            output_tokens = response.usage.output_tokens if hasattr(response, 'usage') else len(result_text) // 4
            
            return {
                "annotations": annotations.get("annotations", []),
                "confidence_scores": annotations.get("confidence_scores", {}),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }
            
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    def _create_system_prompt(self, tag_definitions: Any) -> str:
        """Create system prompt for annotation"""
        if isinstance(tag_definitions, pd.DataFrame):
            tag_df = tag_definitions
        else:
            tag_df = pd.DataFrame(tag_definitions)
        
        tag_section = self._format_tag_section(tag_df)
        
        return f"""You are a scientific named entity recognition (NER) expert. Extract entities that match the SEMANTIC MEANING of tag definitions, not the literal tag labels themselves.

STRICT RULES:
• Extract concrete examples of the categories, not the category names themselves
• Return valid JSON array format only
• Each entity must have: start_char, end_char, text, label
• Positions must be accurate character indices
• Only annotate text that clearly belongs to one of the defined categories

TAG DEFINITIONS:
{tag_section}

Return JSON array format:
{{"annotations": [{{"start_char": 0, "end_char": 10, "text": "example", "label": "TAG_NAME"}}]}}"""

    def _create_user_prompt(self, text: str) -> str:
        """Create user prompt with text to annotate"""
        return f"""TARGET TEXT:
{text}

Extract all entities that match the tag definitions. Return only valid JSON."""
    
    def _format_tag_section(self, tag_df: pd.DataFrame) -> str:
        """Format tag definitions for prompt"""
        tag_texts = []
        for _, row in tag_df.iterrows():
            tag_block = (
                f"TAG: {row['tag_name']}\n"
                f"Definition: {row['definition']}\n"
                f"Examples: {row['examples']}\n"
            )
            tag_texts.append(tag_block)
        return "\n".join(tag_texts)
    
    def _remove_duplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities from overlapping chunks"""
        unique_entities = []
        seen_entities = set()
        
        for entity in entities:
            # Create a unique key based on text and position
            key = (entity.get("text", ""), entity.get("start_char", 0), entity.get("end_char", 0), entity.get("label", ""))
            
            if key not in seen_entities:
                seen_entities.add(key)
                # Remove chunk_id from final entities
                clean_entity = {k: v for k, v in entity.items() if k != "chunk_id"}
                unique_entities.append(clean_entity)
        
        return unique_entities
    
    def _validate_entity_positions(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and fix entity positions"""
        validated_entities = []
        
        for entity in entities:
            try:
                start = entity.get("start_char", 0)
                end = entity.get("end_char", 0)
                expected_text = entity.get("text", "")
                
                # Check if positions are valid
                if start < 0 or end > len(text) or start >= end:
                    continue
                
                # Check if text matches
                actual_text = text[start:end]
                if actual_text == expected_text:
                    validated_entities.append(entity)
                else:
                    # Try to find correct position
                    corrected_entity = self._fix_entity_position(text, entity)
                    if corrected_entity:
                        validated_entities.append(corrected_entity)
                        
            except Exception:
                continue
        
        return validated_entities
    
    def _fix_entity_position(self, text: str, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to fix entity position by finding text in document"""
        expected_text = entity.get("text", "")
        if not expected_text:
            return None
        
        # Find all occurrences of the text
        start_pos = 0
        while True:
            pos = text.find(expected_text, start_pos)
            if pos == -1:
                break
            
            # Return first occurrence (could be improved with better matching)
            fixed_entity = entity.copy()
            fixed_entity["start_char"] = pos
            fixed_entity["end_char"] = pos + len(expected_text)
            return fixed_entity
        
        return None
    
    async def validate_annotation(
        self,
        text: str,
        annotations: List[Dict[str, Any]],
        tag_definitions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate existing annotations for quality and consistency"""
        
        validation_results = {
            "is_valid": True,
            "issues": [],
            "suggestions": []
        }
        
        # Check for overlapping annotations
        sorted_annotations = sorted(annotations, key=lambda x: x["start"])
        for i in range(len(sorted_annotations) - 1):
            current = sorted_annotations[i]
            next_ann = sorted_annotations[i + 1]
            
            if current["end"] > next_ann["start"]:
                validation_results["is_valid"] = False
                validation_results["issues"].append({
                    "type": "overlap",
                    "message": f"Overlapping annotations: '{current['text']}' and '{next_ann['text']}'"
                })
        
        # Check if annotated text matches positions
        for annotation in annotations:
            start, end = annotation["start"], annotation["end"]
            if start < 0 or end > len(text) or start >= end:
                validation_results["is_valid"] = False
                validation_results["issues"].append({
                    "type": "invalid_position",
                    "message": f"Invalid position for annotation: '{annotation['text']}'"
                })
                continue
            
            expected_text = text[start:end]
            if expected_text != annotation["text"]:
                validation_results["is_valid"] = False
                validation_results["issues"].append({
                    "type": "text_mismatch",
                    "message": f"Text mismatch: expected '{expected_text}', got '{annotation['text']}'"
                })
        
        # Check if tags are valid
        valid_tags = set(tag_definitions.keys())
        for annotation in annotations:
            if annotation["tag"] not in valid_tags:
                validation_results["is_valid"] = False
                validation_results["issues"].append({
                    "type": "invalid_tag",
                    "message": f"Invalid tag: '{annotation['tag']}'"
                })
        
        return validation_results
    
    async def evaluate_annotations_with_llm(
        self,
        annotations: List[Dict[str, Any]],
        tag_definitions: List[Dict[str, Any]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_tokens: int = 2000
    ) -> List[Dict[str, Any]]:
        """Evaluate annotations using LLM to suggest improvements"""
        
        # Convert tag definitions to DataFrame format
        tag_df = pd.DataFrame(tag_definitions)
        
        evaluation_results = []
        
        # Process annotations in batches
        batch_size = 10
        for i in range(0, len(annotations), batch_size):
            batch = annotations[i:i + batch_size]
            
            try:
                evaluation_prompt = self._create_evaluation_prompt(batch, tag_df)
                
                result = await self.annotate_text(
                    evaluation_prompt,
                    tag_df,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Parse evaluation results
                for j, annotation in enumerate(batch):
                    evaluation_results.append({
                        "entity_index": i + j,
                        "original_annotation": annotation,
                        "is_correct": True,  # Default assumption
                        "recommendation": "keep",
                        "reasoning": "Annotation appears correct",
                        "suggested_label": annotation.get("label", ""),
                        "confidence": 0.8
                    })
                    
            except Exception as e:
                # If evaluation fails, mark as uncertain
                for j, annotation in enumerate(batch):
                    evaluation_results.append({
                        "entity_index": i + j,
                        "original_annotation": annotation,
                        "is_correct": False,
                        "recommendation": "review",
                        "reasoning": f"Evaluation failed: {str(e)}",
                        "suggested_label": annotation.get("label", ""),
                        "confidence": 0.5
                    })
        
        return evaluation_results
    
    def _create_evaluation_prompt(self, annotations: List[Dict[str, Any]], tag_df: pd.DataFrame) -> str:
        """Create prompt for evaluating annotations"""
        
        tag_section = self._format_tag_section(tag_df)
        
        annotations_text = ""
        for i, ann in enumerate(annotations):
            annotations_text += f"{i+1}. Text: '{ann.get('text', '')}' | Label: {ann.get('label', '')} | Position: [{ann.get('start_char', 0)}:{ann.get('end_char', 0)}]\n"
        
        return f"""Evaluate the following annotations against the tag definitions. For each annotation, determine if it's correct, needs a different label, or should be deleted.

TAG DEFINITIONS:
{tag_section}

ANNOTATIONS TO EVALUATE:
{annotations_text}

For each annotation, respond with:
- CORRECT: if the annotation matches the tag definition
- CHANGE_LABEL: if the text should have a different label
- DELETE: if the annotation is incorrect

Provide reasoning for each decision."""
