from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from app.api.auth import get_current_user
from app.database import get_db

router = APIRouter()


class AnnotationRequest(BaseModel):
    text: str
    tag_definitions: List[Dict[str, Any]]  # Changed to match new format
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 1000
    chunk_size: int = 1000
    overlap: int = 50


class ManualAnnotationRequest(BaseModel):
    text: str
    start_char: int
    end_char: int
    label: str
    confidence: Optional[float] = 1.0


class ValidationRequest(BaseModel):
    text: str
    annotations: List[Dict[str, Any]]


class FixRequest(BaseModel):
    text: str
    annotations: List[Dict[str, Any]]
    strategy: str = "closest"  # "closest" or "first"


class EvaluationRequest(BaseModel):
    annotations: List[Dict[str, Any]]
    tag_definitions: List[Dict[str, Any]]
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 2000


class ExportRequest(BaseModel):
    annotations: List[Dict[str, Any]]
    text: str
    format_type: str = "json"  # "json", "csv", "conll", "comprehensive_json"
    include_metadata: bool = True


class CostEstimateRequest(BaseModel):
    text_length: int
    model: str
    tag_count: int = 5
    complexity_factor: float = 1.0
    chunk_size: Optional[int] = None
    overlap: int = 50


class AnnotationResult(BaseModel):
    entities: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    chunk_results: Optional[List[Dict[str, Any]]] = None


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
    """Create a new annotation using LLM with chunking support"""
    from app.services.llm_service import LLMService
    from app.services.cost_calculator import CostCalculator
    
    try:
        # Get user's API keys
        user_api_keys = None
        try:
            api_keys_result = db.table("user_api_keys").select("*").eq("user_id", current_user["id"]).execute()
            if api_keys_result.data:
                from app.api.users import decrypt_api_key
                keys_data = api_keys_result.data[0]
                openai_key = decrypt_api_key(keys_data.get("openai_api_key_encrypted", ""))
                anthropic_key = decrypt_api_key(keys_data.get("anthropic_api_key_encrypted", ""))
                
                user_api_keys = {
                    "openai_api_key": openai_key if openai_key else None,
                    "anthropic_api_key": anthropic_key if anthropic_key else None
                }
                
                print(f"🔑 User API keys loaded - OpenAI: {'✓' if openai_key else '✗'}, Anthropic: {'✓' if anthropic_key else '✗'}")
        except Exception as e:
            print(f"Failed to get user API keys: {e}")
        
        # Initialize services with user-specific API keys
        llm_service = LLMService(user_api_keys=user_api_keys)
        cost_calc = CostCalculator()
        
        print(f"🤖 Model requested: {request.model}")
        print(f"🔍 Available clients - OpenAI: {llm_service.has_openai_client()}, Anthropic: {llm_service.has_anthropic_client()}")
        
        # Check if we have the necessary API key for the requested model
        if request.model.startswith("gpt-") and not llm_service.has_openai_client():
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Please add your OpenAI API key in your profile settings."
            )
        elif request.model.startswith("claude-") and not llm_service.has_anthropic_client():
            raise HTTPException(
                status_code=400,
                detail="Anthropic API key not configured. Please add your Anthropic API key in your profile settings."
            )
        
        # Additional check: if no API keys are available at all
        if not llm_service.has_openai_client() and not llm_service.has_anthropic_client():
            raise HTTPException(
                status_code=400,
                detail="No API keys configured. Please add your OpenAI or Anthropic API key in your profile settings to use annotation features."
            )
        
        # Generate annotation using pipeline
        result = await llm_service.run_annotation_pipeline(
            text=request.text,
            tag_definitions=request.tag_definitions,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            chunk_size=request.chunk_size,
            overlap=request.overlap
        )
        
        # Calculate cost
        cost = cost_calc.calculate_cost(
            model=request.model,
            input_tokens=result["statistics"]["total_input_tokens"],
            output_tokens=result["statistics"]["total_output_tokens"]
        )
        
        # Save usage statistics to database
        usage_data = {
            "user_id": current_user["id"],
            "model_used": request.model,
            "tokens_used": result["statistics"]["total_tokens"],
            "input_tokens": result["statistics"]["total_input_tokens"],
            "output_tokens": result["statistics"]["total_output_tokens"],
            "cost": cost["total_cost"],
            "operation_type": "annotation",
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            db.table("usage_stats").insert(usage_data).execute()
        except Exception as e:
            print(f"Failed to save usage stats: {e}")
        
        # Save annotation to database (optional)
        annotation_data = {
            "user_id": current_user["id"],
            "text": request.text[:1000],  # Truncate for storage
            "entities": result["entities"],
            "model_used": request.model,
            "tokens_used": result["statistics"]["total_tokens"],
            "cost": cost["total_cost"],
            "tag_definitions": request.tag_definitions,
            "processing_params": {
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "chunk_size": request.chunk_size,
                "overlap": request.overlap
            },
            "statistics": result["statistics"],
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            db.table("annotations").insert(annotation_data).execute()
        except Exception as e:
            print(f"Failed to save annotation: {e}")
        
        return AnnotationResult(
            entities=result["entities"],
            statistics=result["statistics"],
            chunk_results=result.get("chunk_results", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Annotation error: {e}")
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
    # Check if annotation exists and belongs to user
    annotation = db.table("annotations")\
        .select("*")\
        .eq("id", annotation_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not annotation.data:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    # Delete annotation
    db.table("annotations").delete().eq("id", annotation_id).execute()
    
    return {"message": "Annotation deleted successfully"}


# New Enhanced Endpoints

@router.post("/validate")
async def validate_annotations(
    request: ValidationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Validate annotation positions against source text"""
    from app.services.validation_service import ValidationService
    
    try:
        validation_service = ValidationService()
        validation_results = validation_service.validate_annotations(
            request.text,
            request.annotations
        )
        
        return validation_results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/fix")
async def fix_annotations(
    request: FixRequest,
    current_user: dict = Depends(get_current_user)
):
    """Fix annotation positions using specified strategy"""
    from app.services.validation_service import ValidationService
    
    try:
        validation_service = ValidationService()
        fixed_annotations, fix_stats = validation_service.fix_annotation_positions(
            request.text,
            request.annotations,
            request.strategy
        )
        
        return {
            "fixed_annotations": fixed_annotations,
            "fix_statistics": fix_stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fix failed: {str(e)}"
        )


@router.post("/evaluate")
async def evaluate_annotations(
    request: EvaluationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Evaluate annotations using LLM for quality assessment"""
    from app.services.llm_service import LLMService
    
    try:
        llm_service = LLMService()
        evaluation_results = await llm_service.evaluate_annotations_with_llm(
            request.annotations,
            request.tag_definitions,
            request.model,
            request.temperature,
            request.max_tokens
        )
        
        return {
            "evaluation_results": evaluation_results,
            "summary": {
                "total_entities": len(request.annotations),
                "evaluated_entities": len(evaluation_results)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


@router.post("/export")
async def export_annotations(
    request: ExportRequest,
    current_user: dict = Depends(get_current_user)
):
    """Export annotations in various formats"""
    from app.services.export_service import ExportService
    
    try:
        export_service = ExportService()
        export_result = export_service.export_annotations(
            request.annotations,
            request.text,
            request.format_type,
            request.include_metadata
        )
        
        return export_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.post("/estimate-cost")
async def estimate_annotation_cost(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Estimate cost for annotation task (compatible with CostCalculator component)"""
    from app.services.cost_calculator import CostCalculator
    
    try:
        cost_calc = CostCalculator()
        
        # Extract parameters from request
        text = request.get("text", "")
        model = request.get("model", "gpt-4o-mini")
        chunk_size = request.get("chunk_size", 1000)
        max_tokens = request.get("max_tokens", 1000)
        tag_definitions = request.get("tag_definitions", [])
        
        # Calculate text length and tag count
        text_length = len(text)
        tag_count = len(tag_definitions)
        
        # Estimate input tokens (text + tag definitions + prompt overhead)
        text_tokens = text_length // 4  # Rough estimation
        tag_tokens = sum(len(tag.get("definition", "") + tag.get("examples", "")) for tag in tag_definitions) // 4
        prompt_overhead = 200  # Estimated prompt overhead
        
        input_tokens = text_tokens + tag_tokens + prompt_overhead
        output_tokens = max_tokens
        total_tokens = input_tokens + output_tokens
        
        # Calculate cost based on model
        cost_estimate = cost_calc.calculate_cost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
        return {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "input_cost": cost_estimate["input_cost"],
            "output_cost": cost_estimate["output_cost"],
            "total_cost": cost_estimate["total_cost"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cost estimation failed: {str(e)}"
        )


@router.post("/cost-estimate")
async def estimate_cost(
    request: CostEstimateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Estimate cost for annotation task"""
    from app.services.cost_calculator import CostCalculator
    
    try:
        cost_calc = CostCalculator()
        
        if request.chunk_size:
            # Estimate for chunked processing
            cost_estimate = cost_calc.estimate_chunked_cost(
                request.model,
                request.text_length,
                request.chunk_size,
                request.overlap,
                request.tag_count,
                request.complexity_factor
            )
        else:
            # Estimate for single processing
            cost_estimate = cost_calc.estimate_cost(
                request.model,
                request.text_length,
                request.tag_count,
                request.complexity_factor
            )
        
        return cost_estimate
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cost estimation failed: {str(e)}"
        )


@router.get("/models/pricing")
async def get_model_pricing(
    model: Optional[str] = Query(None, description="Specific model to get pricing for"),
    current_user: dict = Depends(get_current_user)
):
    """Get pricing information for LLM models"""
    from app.services.cost_calculator import CostCalculator
    
    try:
        cost_calc = CostCalculator()
        pricing_info = cost_calc.get_model_pricing(model)
        
        return pricing_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pricing: {str(e)}"
        )


@router.post("/models/compare-costs")
async def compare_model_costs(
    text_length: int,
    models: Optional[List[str]] = None,
    tag_count: int = 5,
    complexity_factor: float = 1.0,
    current_user: dict = Depends(get_current_user)
):
    """Compare costs across different models"""
    from app.services.cost_calculator import CostCalculator
    
    try:
        cost_calc = CostCalculator()
        comparison = cost_calc.compare_model_costs(
            text_length,
            models,
            tag_count,
            complexity_factor
        )
        
        return comparison
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cost comparison failed: {str(e)}"
        )


@router.post("/manual")
async def add_manual_annotation(
    request: ManualAnnotationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Add a manual annotation"""
    try:
        # Validate the manual annotation
        if request.start_char < 0 or request.end_char <= request.start_char:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid character positions"
            )
        
        # Check if text matches positions
        actual_text = request.text[request.start_char:request.end_char]
        if not actual_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty text selection"
            )
        
        manual_annotation = {
            "start_char": request.start_char,
            "end_char": request.end_char,
            "text": actual_text,
            "label": request.label,
            "confidence": request.confidence,
            "source": "manual",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "annotation": manual_annotation,
            "message": "Manual annotation created successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create manual annotation: {str(e)}"
        )


@router.get("/token-recommendations")
async def get_token_recommendations(
    chunk_size: int = Query(1000, description="Chunk size in characters"),
    current_user: dict = Depends(get_current_user)
):
    """Get token recommendations based on chunk size"""
    from app.services.llm_service import LLMService
    
    try:
        llm_service = LLMService()
        recommendations = llm_service.get_token_recommendations(chunk_size)
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/available-models")
async def get_available_models(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get available models based on user's configured API keys"""
    from app.services.llm_service import LLMService
    
    try:
        # Get user's API keys
        user_api_keys = None
        try:
            api_keys_result = db.table("user_api_keys").select("*").eq("user_id", current_user["id"]).execute()
            if api_keys_result.data:
                from app.api.users import decrypt_api_key
                keys_data = api_keys_result.data[0]
                user_api_keys = {
                    "openai_api_key": decrypt_api_key(keys_data.get("openai_api_key_encrypted", "")),
                    "anthropic_api_key": decrypt_api_key(keys_data.get("anthropic_api_key_encrypted", ""))
                }
        except Exception as e:
            print(f"Failed to get user API keys: {e}")
        
        # Initialize LLM service with user keys
        llm_service = LLMService(user_api_keys=user_api_keys)
        available_models = llm_service.get_available_models()
        
        return {
            "models": available_models,
            "has_openai": llm_service.has_openai_client(),
            "has_anthropic": llm_service.has_anthropic_client()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available models: {str(e)}"
        )
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
