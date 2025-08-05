import json
import csv
from typing import Dict, List, Any
from datetime import datetime
import pandas as pd
from io import StringIO


class ExportService:
    """Service for exporting annotations in various formats"""
    
    async def export_annotation(
        self,
        annotation: Dict[str, Any],
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export single annotation in specified format"""
        
        if format.lower() == "json":
            return await self._export_json(annotation)
        elif format.lower() == "csv":
            return await self._export_csv([annotation])
        elif format.lower() == "excel":
            return await self._export_excel([annotation])
        elif format.lower() == "conll":
            return await self._export_conll(annotation)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def export_annotations(
        self,
        annotations: List[Dict[str, Any]],
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export multiple annotations in specified format"""
        
        if format.lower() == "json":
            return await self._export_json_batch(annotations)
        elif format.lower() == "csv":
            return await self._export_csv(annotations)
        elif format.lower() == "excel":
            return await self._export_excel(annotations)
        elif format.lower() == "conll":
            return await self._export_conll_batch(annotations)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def _export_json(self, annotation: Dict[str, Any]) -> Dict[str, Any]:
        """Export as JSON format"""
        
        export_data = {
            "annotation_id": annotation["id"],
            "text": annotation["text"],
            "annotations": annotation["annotations"],
            "model_used": annotation["model_used"],
            "confidence_scores": annotation.get("confidence_scores", {}),
            "created_at": annotation["created_at"],
            "export_timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "content": json.dumps(export_data, indent=2),
            "content_type": "application/json",
            "filename": f"annotation_{annotation['id']}.json"
        }
    
    async def _export_json_batch(self, annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export multiple annotations as JSON"""
        
        export_data = {
            "annotations": [],
            "metadata": {
                "total_count": len(annotations),
                "export_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        for annotation in annotations:
            export_data["annotations"].append({
                "annotation_id": annotation["id"],
                "text": annotation["text"],
                "annotations": annotation["annotations"],
                "model_used": annotation["model_used"],
                "confidence_scores": annotation.get("confidence_scores", {}),
                "created_at": annotation["created_at"]
            })
        
        return {
            "content": json.dumps(export_data, indent=2),
            "content_type": "application/json",
            "filename": f"annotations_batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        }
    
    async def _export_csv(self, annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export as CSV format"""
        
        rows = []
        for annotation in annotations:
            for ann in annotation["annotations"]:
                rows.append({
                    "annotation_id": annotation["id"],
                    "text": annotation["text"],
                    "entity_text": ann["text"],
                    "entity_start": ann["start"],
                    "entity_end": ann["end"],
                    "entity_tag": ann["tag"],
                    "confidence": ann.get("confidence", ""),
                    "model_used": annotation["model_used"],
                    "created_at": annotation["created_at"]
                })
        
        if not rows:
            return {
                "content": "No annotations to export",
                "content_type": "text/csv",
                "filename": "empty_annotations.csv"
            }
        
        # Create CSV content
        output = StringIO()
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
        return {
            "content": output.getvalue(),
            "content_type": "text/csv",
            "filename": f"annotations_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    
    async def _export_excel(self, annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export as Excel format"""
        
        rows = []
        for annotation in annotations:
            for ann in annotation["annotations"]:
                rows.append({
                    "Annotation ID": annotation["id"],
                    "Text": annotation["text"],
                    "Entity Text": ann["text"],
                    "Start Position": ann["start"],
                    "End Position": ann["end"],
                    "Tag": ann["tag"],
                    "Confidence": ann.get("confidence", ""),
                    "Model Used": annotation["model_used"],
                    "Created At": annotation["created_at"]
                })
        
        if not rows:
            return {
                "content": "No annotations to export",
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "filename": "empty_annotations.xlsx"
            }
        
        # Create Excel file using pandas
        df = pd.DataFrame(rows)
        
        # Save to bytes buffer
        from io import BytesIO
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        
        return {
            "content": buffer.getvalue(),
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "filename": f"annotations_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    
    async def _export_conll(self, annotation: Dict[str, Any]) -> Dict[str, Any]:
        """Export as CoNLL format (IOB tagging)"""
        
        text = annotation["text"]
        annotations = annotation["annotations"]
        
        # Create token-level annotations
        tokens = text.split()
        token_positions = []
        current_pos = 0
        
        # Calculate token positions
        for token in tokens:
            start = text.find(token, current_pos)
            end = start + len(token)
            token_positions.append((token, start, end))
            current_pos = end
        
        # Assign IOB tags
        token_tags = ["O"] * len(tokens)
        
        for ann in annotations:
            ann_start, ann_end = ann["start"], ann["end"]
            tag = ann["tag"]
            
            # Find overlapping tokens
            first_token = True
            for i, (token, token_start, token_end) in enumerate(token_positions):
                # Check if token overlaps with annotation
                if not (token_end <= ann_start or token_start >= ann_end):
                    if first_token:
                        token_tags[i] = f"B-{tag}"
                        first_token = False
                    else:
                        token_tags[i] = f"I-{tag}"
        
        # Create CoNLL format
        conll_lines = []
        for (token, _, _), tag in zip(token_positions, token_tags):
            conll_lines.append(f"{token}\\t{tag}")
        
        conll_content = "\\n".join(conll_lines) + "\\n"
        
        return {
            "content": conll_content,
            "content_type": "text/plain",
            "filename": f"annotation_{annotation['id']}.conll"
        }
    
    async def _export_conll_batch(self, annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export multiple annotations as CoNLL format"""
        
        all_conll_lines = []
        
        for annotation in annotations:
            conll_result = await self._export_conll(annotation)
            all_conll_lines.append(f"# Annotation ID: {annotation['id']}")
            all_conll_lines.append(conll_result["content"].strip())
            all_conll_lines.append("")  # Empty line between annotations
        
        return {
            "content": "\\n".join(all_conll_lines),
            "content_type": "text/plain",
            "filename": f"annotations_batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.conll"
        }
