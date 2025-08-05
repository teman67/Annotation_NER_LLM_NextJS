import openai
import anthropic
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime

from app.config import settings


class LLMService:
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        
        if settings.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    
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
        tag_definitions: Dict[str, Any],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Annotate using OpenAI GPT models"""
        
        system_prompt = self._create_system_prompt(tag_definitions)
        user_prompt = self._create_user_prompt(text)
        
        try:
            response = await openai.ChatCompletion.acreate(
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
            annotations = json.loads(result_text)
            
            return {
                "annotations": annotations["annotations"],
                "confidence_scores": annotations.get("confidence_scores", {}),
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _annotate_with_claude(
        self,
        text: str,
        tag_definitions: Dict[str, Any],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Annotate using Anthropic Claude models"""
        
        system_prompt = self._create_system_prompt(tag_definitions)
        user_prompt = self._create_user_prompt(text)
        
        try:
            response = await self.anthropic_client.messages.create(
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
            
            # Claude doesn't provide token counts in the same way
            estimated_input_tokens = len(system_prompt + user_prompt) // 4
            estimated_output_tokens = len(result_text) // 4
            
            return {
                "annotations": annotations["annotations"],
                "confidence_scores": annotations.get("confidence_scores", {}),
                "input_tokens": estimated_input_tokens,
                "output_tokens": estimated_output_tokens,
                "total_tokens": estimated_input_tokens + estimated_output_tokens
            }
            
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    def _create_system_prompt(self, tag_definitions: Dict[str, Any]) -> str:
        """Create system prompt for annotation task"""
        
        tags_description = ""
        for tag_name, tag_info in tag_definitions.items():
            examples_str = ", ".join(tag_info.get("examples", []))
            tags_description += f"- {tag_name}: {tag_info.get('description', '')}\\n"
            if examples_str:
                tags_description += f"  Examples: {examples_str}\\n"
        
        system_prompt = f"""You are an expert text annotator specializing in scientific and biomedical text analysis. Your task is to identify and annotate entities in the provided text according to the specified tag definitions.

Tag Definitions:
{tags_description}

Instructions:
1. Carefully read the input text
2. Identify all entities that match the tag definitions
3. For each entity, provide:
   - The exact text span
   - The start and end character positions
   - The assigned tag
   - A confidence score (0.0-1.0)
4. Return results in JSON format with the following structure:
   {{
     "annotations": [
       {{
         "text": "entity text",
         "start": start_position,
         "end": end_position,
         "tag": "TAG_NAME",
         "confidence": 0.95
       }}
     ],
     "confidence_scores": {{
       "overall": 0.90,
       "TAG_NAME": 0.85
     }}
   }}

Quality Guidelines:
- Be precise with character positions
- Only annotate entities you are confident about
- Avoid overlapping annotations
- Maintain consistency throughout the text
- Provide realistic confidence scores"""

        return system_prompt
    
    def _create_user_prompt(self, text: str) -> str:
        """Create user prompt with text to annotate"""
        return f"Please annotate the following text according to the tag definitions:\\n\\n{text}"
    
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
