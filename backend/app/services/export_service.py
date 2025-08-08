import json
import csv
import io
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd


class ExportService:
    """Service for exporting annotations in various formats"""
    
    def __init__(self):
        self.supported_formats = ["json", "csv", "conll", "comprehensive_json"]
    
    def export_annotations(
        self,
        annotations: List[Dict[str, Any]],
        text: str,
        format_type: str = "json",
        include_metadata: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Export annotations in the specified format"""
        
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}. Supported: {self.supported_formats}")
        
        if format_type == "json":
            return self._export_json(annotations, text, include_metadata, **kwargs)
        elif format_type == "csv":
            return self._export_csv(annotations, text, include_metadata, **kwargs)
        elif format_type == "conll":
            return self._export_conll(annotations, text, include_metadata, **kwargs)
        elif format_type == "comprehensive_json":
            return self._export_comprehensive_json(annotations, text, include_metadata, **kwargs)
    
    def _export_json(
        self,
        annotations: List[Dict[str, Any]],
        text: str,
        include_metadata: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Export as basic JSON format"""
        
        # Clean annotations (remove any internal fields)
        clean_annotations = []
        for ann in annotations:
            clean_ann = {
                "start_char": ann.get("start_char", 0),
                "end_char": ann.get("end_char", 0),
                "text": ann.get("text", ""),
                "label": ann.get("label", ""),
                "source": ann.get("source", "llm")
            }
            clean_annotations.append(clean_ann)
        
        result = {
            "text": text,
            "entities": clean_annotations
        }
        
        if include_metadata:
            result["metadata"] = {
                "total_entities": len(annotations),
                "export_timestamp": datetime.now().isoformat(),
                "export_format": "json"
            }
        
        return {
            "content": json.dumps(result, indent=2, ensure_ascii=False),
            "filename": f"annotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "mime_type": "application/json"
        }
    
    def _export_csv(
        self,
        annotations: List[Dict[str, Any]],
        text: str,
        include_metadata: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Export as CSV format"""
        
        # Create CSV data
        csv_data = []
        for i, ann in enumerate(annotations):
            row = {
                "id": i + 1,
                "start_char": ann.get("start_char", 0),
                "end_char": ann.get("end_char", 0),
                "text": ann.get("text", ""),
                "label": ann.get("label", ""),
                "length": len(ann.get("text", "")),
                "source": ann.get("source", "llm")
            }
            csv_data.append(row)
        
        # Convert to CSV string
        output = io.StringIO()
        if csv_data:
            fieldnames = ["id", "start_char", "end_char", "text", "label", "length", "source"]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        
        csv_content = output.getvalue()
        output.close()
        
        # Add metadata as comments if requested
        if include_metadata and csv_data:
            header_comments = [
                f"# Annotations Export - {datetime.now().isoformat()}",
                f"# Total entities: {len(annotations)}",
                f"# Text length: {len(text)} characters",
                "# Format: CSV",
                "#"
            ]
            csv_content = "\n".join(header_comments) + "\n" + csv_content
        
        return {
            "content": csv_content,
            "filename": f"annotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "mime_type": "text/csv"
        }
    
    def _export_conll(
        self,
        annotations: List[Dict[str, Any]],
        text: str,
        include_metadata: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Export in CoNLL format (BIO tagging)"""
        
        # Tokenize text (simple whitespace tokenization)
        tokens = []
        token_positions = []
        current_pos = 0
        
        for word in text.split():
            start_pos = text.find(word, current_pos)
            end_pos = start_pos + len(word)
            tokens.append(word)
            token_positions.append((start_pos, end_pos))
            current_pos = end_pos
        
        # Create BIO tags
        bio_tags = ["O"] * len(tokens)
        
        for ann in annotations:
            start_char = ann.get("start_char", 0)
            end_char = ann.get("end_char", 0)
            label = ann.get("label", "")
            
            # Find tokens that overlap with this annotation
            first_token = True
            for i, (token_start, token_end) in enumerate(token_positions):
                # Check if token overlaps with annotation
                if not (token_end <= start_char or token_start >= end_char):
                    if first_token:
                        bio_tags[i] = f"B-{label}"
                        first_token = False
                    else:
                        bio_tags[i] = f"I-{label}"
        
        # Create CoNLL format output
        conll_lines = []
        
        if include_metadata:
            conll_lines.extend([
                f"# Annotations Export - {datetime.now().isoformat()}",
                f"# Total entities: {len(annotations)}",
                f"# Total tokens: {len(tokens)}",
                f"# Format: CoNLL (BIO tagging)",
                ""
            ])
        
        for token, tag in zip(tokens, bio_tags):
            conll_lines.append(f"{token}\t{tag}")
        
        # Add sentence boundary
        conll_lines.append("")
        
        conll_content = "\n".join(conll_lines)
        
        return {
            "content": conll_content,
            "filename": f"annotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.conll",
            "mime_type": "text/plain"
        }
    
    def _export_comprehensive_json(
        self,
        annotations: List[Dict[str, Any]],
        text: str,
        include_metadata: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Export comprehensive JSON with all available data"""
        
        # Separate LLM and manual annotations if available
        llm_entities = []
        manual_entities = []
        all_entities = []
        
        for ann in annotations:
            clean_ann = {
                "start_char": ann.get("start_char", 0),
                "end_char": ann.get("end_char", 0),
                "text": ann.get("text", ""),
                "label": ann.get("label", "")
            }
            
            # Add optional fields
            for field in ["chunk_id", "source"]:
                if field in ann:
                    clean_ann[field] = ann[field]
            
            all_entities.append(clean_ann)
            
            # Categorize by source if available
            source = ann.get("source", "unknown")
            if source == "llm":
                llm_entities.append(clean_ann)
            elif source == "manual":
                manual_entities.append(clean_ann)
        
        result = {
            "text": text,
            "all_entities": all_entities
        }
        
        # Add separated entities if we have source information
        if llm_entities or manual_entities:
            result["llm_entities"] = llm_entities
            result["manual_entities"] = manual_entities
        
        if include_metadata:
            result["metadata"] = {
                "total_entities": len(annotations),
                "total_llm_entities": len(llm_entities),
                "total_manual_entities": len(manual_entities),
                "export_timestamp": datetime.now().isoformat(),
                "export_format": "comprehensive_json",
                "text_length": len(text),
                "processing_parameters": kwargs.get("processing_parameters", {}),
                "model_info": kwargs.get("model_info", {})
            }
        
        # Add evaluation data if available
        if "evaluation_results" in kwargs:
            result["evaluation"] = {
                "evaluation_results": kwargs["evaluation_results"],
                "evaluation_summary": kwargs.get("evaluation_summary", {}),
                "evaluation_timestamp": datetime.now().isoformat()
            }
        
        # Add validation data if available
        if "validation_results" in kwargs:
            result["validation"] = {
                "validation_results": kwargs["validation_results"],
                "validation_timestamp": datetime.now().isoformat()
            }
        
        # Add fix data if available
        if "fix_results" in kwargs:
            result["position_fixes"] = {
                "fix_results": kwargs["fix_results"],
                "fix_timestamp": datetime.now().isoformat()
            }
        
        return {
            "content": json.dumps(result, indent=2, ensure_ascii=False),
            "filename": f"annotations_comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "mime_type": "application/json"
        }
    
    def get_export_statistics(self, annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the annotations for export"""
        
        if not annotations:
            return {
                "total_entities": 0,
                "labels": {},
                "sources": {},
                "text_length_stats": {}
            }
        
        # Count by label
        label_counts = {}
        for ann in annotations:
            label = ann.get("label", "unknown")
            label_counts[label] = label_counts.get(label, 0) + 1
        
        # Count by source
        source_counts = {}
        for ann in annotations:
            source = ann.get("source", "unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Text length statistics
        text_lengths = [len(ann.get("text", "")) for ann in annotations]
        text_length_stats = {
            "min": min(text_lengths) if text_lengths else 0,
            "max": max(text_lengths) if text_lengths else 0,
            "avg": sum(text_lengths) / len(text_lengths) if text_lengths else 0
        }
        
        return {
            "total_entities": len(annotations),
            "labels": label_counts,
            "sources": source_counts,
            "text_length_stats": text_length_stats
        }
