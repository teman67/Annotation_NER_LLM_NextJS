from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime


class ValidationService:
    """Service for validating and fixing annotation positions"""
    
    def __init__(self):
        pass
    
    def validate_annotations(
        self,
        text: str,
        annotations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate annotations against the source text"""
        
        validation_results = {
            "total_entities": len(annotations),
            "correct_entities": 0,
            "errors": [],
            "warnings": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Check each annotation
        for i, annotation in enumerate(annotations):
            try:
                start_char = annotation.get("start_char", 0)
                end_char = annotation.get("end_char", 0)
                expected_text = annotation.get("text", "")
                label = annotation.get("label", "")
                
                # Validate position boundaries
                if start_char < 0 or end_char > len(text) or start_char >= end_char:
                    validation_results["errors"].append({
                        "entity_index": i,
                        "error": "Invalid position boundaries",
                        "start_char": start_char,
                        "end_char": end_char,
                        "expected_text": expected_text,
                        "label": label
                    })
                    continue
                
                # Check if text matches
                actual_text = text[start_char:end_char]
                if actual_text != expected_text:
                    validation_results["errors"].append({
                        "entity_index": i,
                        "error": "Text mismatch",
                        "start_char": start_char,
                        "end_char": end_char,
                        "expected_text": expected_text,
                        "actual_text": actual_text,
                        "label": label
                    })
                    continue
                
                # If we get here, annotation is correct
                validation_results["correct_entities"] += 1
                
            except Exception as e:
                validation_results["errors"].append({
                    "entity_index": i,
                    "error": f"Validation exception: {str(e)}",
                    "start_char": annotation.get("start_char", 0),
                    "end_char": annotation.get("end_char", 0),
                    "expected_text": annotation.get("text", ""),
                    "label": annotation.get("label", "")
                })
        
        # Check for overlapping annotations
        self._check_overlaps(annotations, validation_results)
        
        # Check for zero-length annotations
        self._check_zero_length(annotations, validation_results)
        
        return validation_results
    
    def _check_overlaps(self, annotations: List[Dict[str, Any]], validation_results: Dict[str, Any]):
        """Check for overlapping annotations"""
        sorted_annotations = sorted(
            [(i, ann) for i, ann in enumerate(annotations)],
            key=lambda x: x[1].get("start_char", 0)
        )
        
        for i in range(len(sorted_annotations) - 1):
            current_idx, current = sorted_annotations[i]
            next_idx, next_ann = sorted_annotations[i + 1]
            
            current_end = current.get("end_char", 0)
            next_start = next_ann.get("start_char", 0)
            
            if current_end > next_start:
                validation_results["warnings"].append({
                    "type": "overlap",
                    "entity1": {
                        "index": current_idx,
                        "text": current.get("text", ""),
                        "start_char": current.get("start_char", 0),
                        "end_char": current_end,
                        "label": current.get("label", "")
                    },
                    "entity2": {
                        "index": next_idx,
                        "text": next_ann.get("text", ""),
                        "start_char": next_start,
                        "end_char": next_ann.get("end_char", 0),
                        "label": next_ann.get("label", "")
                    }
                })
    
    def _check_zero_length(self, annotations: List[Dict[str, Any]], validation_results: Dict[str, Any]):
        """Check for zero-length annotations"""
        for i, annotation in enumerate(annotations):
            start_char = annotation.get("start_char", 0)
            end_char = annotation.get("end_char", 0)
            
            if start_char == end_char:
                validation_results["warnings"].append({
                    "type": "zero_length",
                    "entity_index": i,
                    "annotation": annotation
                })
    
    def fix_annotation_positions(
        self,
        text: str,
        annotations: List[Dict[str, Any]],
        strategy: str = "closest"
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Fix annotation positions using different strategies"""
        
        fixed_entities = []
        fix_stats = {
            "total": len(annotations),
            "already_correct": 0,
            "fixed": 0,
            "unfixable": 0,
            "multiple_matches": 0,
            "strategy_used": strategy
        }
        
        for annotation in annotations:
            try:
                start_char = annotation.get("start_char", 0)
                end_char = annotation.get("end_char", 0)
                expected_text = annotation.get("text", "")
                
                # Check if already correct
                if (0 <= start_char < end_char <= len(text) and 
                    text[start_char:end_char] == expected_text):
                    fixed_entities.append(annotation.copy())
                    fix_stats["already_correct"] += 1
                    continue
                
                # Try to fix the position
                fixed_annotation = self._find_correct_position(
                    text, expected_text, annotation, strategy
                )
                
                if fixed_annotation:
                    # Check if we found multiple matches
                    all_positions = self._find_all_positions(text, expected_text)
                    if len(all_positions) > 1:
                        fix_stats["multiple_matches"] += 1
                    
                    fixed_entities.append(fixed_annotation)
                    fix_stats["fixed"] += 1
                else:
                    fix_stats["unfixable"] += 1
                    
            except Exception:
                fix_stats["unfixable"] += 1
        
        return fixed_entities, fix_stats
    
    def _find_correct_position(
        self,
        text: str,
        expected_text: str,
        original_annotation: Dict[str, Any],
        strategy: str
    ) -> Optional[Dict[str, Any]]:
        """Find the correct position for an annotation"""
        
        if not expected_text.strip():
            return None
        
        positions = self._find_all_positions(text, expected_text)
        
        if not positions:
            return None
        
        if strategy == "first":
            chosen_pos = positions[0]
        elif strategy == "closest":
            original_start = original_annotation.get("start_char", 0)
            chosen_pos = min(positions, key=lambda pos: abs(pos - original_start))
        else:
            chosen_pos = positions[0]
        
        fixed_annotation = original_annotation.copy()
        fixed_annotation["start_char"] = chosen_pos
        fixed_annotation["end_char"] = chosen_pos + len(expected_text)
        
        return fixed_annotation
    
    def _find_all_positions(self, text: str, search_text: str) -> List[int]:
        """Find all positions where the search text appears"""
        positions = []
        start = 0
        
        while True:
            pos = text.find(search_text, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        return positions
    
    def apply_fixes(
        self,
        annotations: List[Dict[str, Any]],
        fix_indices: List[int],
        fixed_annotations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply fixes to specific annotations"""
        
        result = []
        fix_map = {idx: fixed_annotations[i] for i, idx in enumerate(fix_indices)}
        
        for i, annotation in enumerate(annotations):
            if i in fix_map:
                result.append(fix_map[i])
            else:
                result.append(annotation)
        
        return result
    
    def get_validation_summary(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of validation results"""
        
        total = validation_results["total_entities"]
        correct = validation_results["correct_entities"]
        errors = len(validation_results["errors"])
        warnings = len(validation_results["warnings"])
        
        return {
            "total_entities": total,
            "correct_entities": correct,
            "error_count": errors,
            "warning_count": warnings,
            "accuracy_percentage": (correct / total * 100) if total > 0 else 0,
            "has_errors": errors > 0,
            "has_warnings": warnings > 0,
            "validation_status": "passed" if errors == 0 else "failed"
        }
