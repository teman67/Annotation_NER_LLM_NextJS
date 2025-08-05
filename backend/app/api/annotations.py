from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.api.auth import get_current_user
from app.database import get_db

router = APIRouter()


class AnnotationRequest(BaseModel):
    text: str
    tag_definitions: Dict[str, Any]
    model: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 4000


class AnnotationResult(BaseModel):
    id: str
    text: str
    annotations: List[Dict[str, Any]]
    model_used: str
    tokens_used: int
    cost: float
    confidence_scores: Dict[str, float]
    created_at: datetime


class AnnotationValidation(BaseModel):
    annotation_id: str
    is_valid: bool
    feedback: Optional[str] = None


@router.post("/annotate", response_model=AnnotationResult)
async def create_annotation(
    request: AnnotationRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new annotation using LLM"""
    from app.services.llm_service import LLMService
    from app.services.cost_calculator import CostCalculator
    
    try:
        # Initialize services
        llm_service = LLMService()
        cost_calc = CostCalculator()
        
        # Generate annotation
        result = await llm_service.annotate_text(
            text=request.text,
            tag_definitions=request.tag_definitions,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Calculate cost
        cost = cost_calc.calculate_cost(
            model=request.model,
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"]
        )
        
        # Save to database
        annotation_data = {
            "user_id": current_user["id"],
            "text": request.text,
            "annotations": result["annotations"],
            "model_used": request.model,
            "tokens_used": result["total_tokens"],
            "cost": cost,
            "confidence_scores": result.get("confidence_scores", {}),
            "tag_definitions": request.tag_definitions,
            "created_at": datetime.utcnow().isoformat()
        }
        
        saved_annotation = db.table("annotations").insert(annotation_data).execute()
        
        return AnnotationResult(**saved_annotation.data[0])
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Annotation failed: {str(e)}"
        )


@router.get("/", response_model=List[AnnotationResult])
async def get_annotations(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's annotations"""
    annotations = db.table("annotations")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .order("created_at", desc=True)\
        .range(skip, skip + limit - 1)\
        .execute()
    
    return annotations.data


@router.get("/{annotation_id}", response_model=AnnotationResult)
async def get_annotation(
    annotation_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get specific annotation"""
    annotation = db.table("annotations")\
        .select("*")\
        .eq("id", annotation_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not annotation.data:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    return annotation.data[0]


@router.post("/{annotation_id}/validate")
async def validate_annotation(
    annotation_id: str,
    validation: AnnotationValidation,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Validate/invalidate an annotation"""
    # Check if annotation exists and belongs to user
    annotation = db.table("annotations")\
        .select("*")\
        .eq("id", annotation_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not annotation.data:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    # Save validation
    validation_data = {
        "annotation_id": annotation_id,
        "user_id": current_user["id"],
        "is_valid": validation.is_valid,
        "feedback": validation.feedback,
        "created_at": datetime.utcnow().isoformat()
    }
    
    db.table("annotation_validations").insert(validation_data).execute()
    
    return {"message": "Validation saved successfully"}


@router.delete("/{annotation_id}")
async def delete_annotation(
    annotation_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete an annotation"""
    result = db.table("annotations")\
        .delete()\
        .eq("id", annotation_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    return {"message": "Annotation deleted successfully"}


@router.post("/{annotation_id}/export")
async def export_annotation(
    annotation_id: str,
    format: str = "json",
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Export annotation in various formats"""
    from app.services.export_service import ExportService
    
    annotation = db.table("annotations")\
        .select("*")\
        .eq("id", annotation_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not annotation.data:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    export_service = ExportService()
    return await export_service.export_annotation(annotation.data[0], format)
