from typing import Dict, List, Any
import re
from datetime import datetime

from app.services.llm_service import LLMService
from app.services.cost_calculator import CostCalculator


class FileProcessor:
    """Service for processing entire files for annotation"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.cost_calculator = CostCalculator()
    
    async def process_file(
        self,
        content: str,
        tagset: Dict[str, Any],
        model: str = "gpt-4",
        user_id: str = "",
        chunk_size: int = 2000,
        overlap: int = 200
    ) -> Dict[str, Any]:
        """Process entire file by chunking and annotating each chunk"""
        
        # Split content into manageable chunks
        chunks = self._split_into_chunks(content, chunk_size, overlap)
        
        all_annotations = []
        total_cost = 0.0
        total_tokens = 0
        processing_log = []
        
        # Process each chunk
        for i, chunk_info in enumerate(chunks):
            try:
                chunk_text = chunk_info["text"]
                chunk_offset = chunk_info["offset"]
                
                # Annotate chunk
                result = await self.llm_service.annotate_text(
                    text=chunk_text,
                    tag_definitions=tagset["tags"],
                    model=model
                )
                
                # Calculate cost for this chunk
                chunk_cost = self.cost_calculator.calculate_cost(
                    model=model,
                    input_tokens=result["input_tokens"],
                    output_tokens=result["output_tokens"]
                )
                
                # Adjust annotation positions to file coordinates
                adjusted_annotations = []
                for annotation in result["annotations"]:
                    adjusted_annotation = annotation.copy()
                    adjusted_annotation["start"] += chunk_offset
                    adjusted_annotation["end"] += chunk_offset
                    adjusted_annotations.append(adjusted_annotation)
                
                all_annotations.extend(adjusted_annotations)
                total_cost += chunk_cost
                total_tokens += result["total_tokens"]
                
                processing_log.append({
                    "chunk": i + 1,
                    "status": "success",
                    "annotations_found": len(adjusted_annotations),
                    "tokens_used": result["total_tokens"],
                    "cost": chunk_cost
                })
                
            except Exception as e:
                processing_log.append({
                    "chunk": i + 1,
                    "status": "error",
                    "error": str(e)
                })
        
        # Remove duplicate annotations from overlapping regions
        merged_annotations = self._merge_overlapping_annotations(all_annotations)
        
        return {
            "file_annotations": {
                "content": content,
                "annotations": merged_annotations,
                "tagset_id": tagset.get("id"),
                "model_used": model,
                "total_annotations": len(merged_annotations),
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "chunks_processed": len(chunks),
                "processing_log": processing_log,
                "created_at": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
        }
    
    def _split_into_chunks(
        self,
        content: str,
        chunk_size: int,
        overlap: int
    ) -> List[Dict[str, Any]]:
        """Split content into overlapping chunks"""
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            
            # Try to break at sentence boundaries for better context
            if end < len(content):
                # Look for sentence endings within the last 100 characters
                search_start = max(end - 100, start)
                sentence_endings = [
                    content.rfind('. ', search_start, end),
                    content.rfind('! ', search_start, end),
                    content.rfind('? ', search_start, end),
                    content.rfind('.\\n', search_start, end),
                    content.rfind('!\\n', search_start, end),
                    content.rfind('?\\n', search_start, end)
                ]
                
                best_break = max([pos for pos in sentence_endings if pos > search_start], default=-1)
                if best_break > -1:
                    end = best_break + 2  # Include the punctuation and space
            
            chunk_text = content[start:end]
            chunks.append({
                "text": chunk_text,
                "offset": start,
                "length": len(chunk_text)
            })
            
            # Move start position, accounting for overlap
            if end >= len(content):
                break
            start = max(end - overlap, start + 1)
        
        return chunks
    
    def _merge_overlapping_annotations(
        self,
        annotations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge duplicate annotations from overlapping chunks"""
        
        if not annotations:
            return []
        
        # Sort annotations by start position
        sorted_annotations = sorted(annotations, key=lambda x: (x["start"], x["end"]))
        merged = []
        
        for current in sorted_annotations:
            # Check if this annotation overlaps significantly with any existing merged annotation
            is_duplicate = False
            
            for existing in merged:
                # Calculate overlap
                overlap_start = max(current["start"], existing["start"])
                overlap_end = min(current["end"], existing["end"])
                
                if overlap_start < overlap_end:
                    overlap_length = overlap_end - overlap_start
                    current_length = current["end"] - current["start"]
                    existing_length = existing["end"] - existing["start"]
                    
                    # If overlap is significant (>80% of either annotation), consider it duplicate
                    overlap_ratio_current = overlap_length / current_length
                    overlap_ratio_existing = overlap_length / existing_length
                    
                    if (overlap_ratio_current > 0.8 or overlap_ratio_existing > 0.8) and \
                       current["tag"] == existing["tag"]:
                        is_duplicate = True
                        
                        # Keep the annotation with higher confidence
                        if current.get("confidence", 0) > existing.get("confidence", 0):
                            merged.remove(existing)
                            merged.append(current)
                        break
            
            if not is_duplicate:
                merged.append(current)
        
        return sorted(merged, key=lambda x: x["start"])
    
    async def process_batch_files(
        self,
        files: List[Dict[str, Any]],
        tagset: Dict[str, Any],
        model: str = "gpt-4",
        user_id: str = ""
    ) -> Dict[str, Any]:
        """Process multiple files in batch"""
        
        batch_results = []
        total_cost = 0.0
        total_annotations = 0
        
        for file_info in files:
            try:
                result = await self.process_file(
                    content=file_info["content"],
                    tagset=tagset,
                    model=model,
                    user_id=user_id
                )
                
                batch_results.append({
                    "file_id": file_info.get("id"),
                    "filename": file_info.get("filename"),
                    "status": "success",
                    "result": result["file_annotations"]
                })
                
                total_cost += result["file_annotations"]["total_cost"]
                total_annotations += result["file_annotations"]["total_annotations"]
                
            except Exception as e:
                batch_results.append({
                    "file_id": file_info.get("id"),
                    "filename": file_info.get("filename"),
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "batch_id": f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "files_processed": len(files),
            "total_cost": total_cost,
            "total_annotations": total_annotations,
            "results": batch_results,
            "created_at": datetime.utcnow().isoformat()
        }
