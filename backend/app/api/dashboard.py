from fastapi import APIRouter, Depends
from typing import Dict, List, Any
from datetime import datetime, timedelta

from app.api.auth import get_current_user
from app.database import get_db

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get dashboard overview statistics"""
    # Recent annotations (last 30 days)
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
    
    recent_annotations = db.table("annotations")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .gte("created_at", thirty_days_ago)\
        .execute()
    
    # Total statistics
    total_annotations = db.table("annotations")\
        .select("*", count="exact")\
        .eq("user_id", current_user["id"])\
        .execute()
    
    total_projects = db.table("projects")\
        .select("*", count="exact")\
        .eq("user_id", current_user["id"])\
        .execute()
    
    total_tagsets = db.table("tag_sets")\
        .select("*", count="exact")\
        .eq("user_id", current_user["id"])\
        .execute()
    
    # Calculate costs
    all_annotations = db.table("annotations")\
        .select("cost, created_at")\
        .eq("user_id", current_user["id"])\
        .execute()
    
    total_cost = sum(float(ann.get("cost", 0)) for ann in all_annotations.data)
    recent_cost = sum(float(ann.get("cost", 0)) for ann in recent_annotations.data)
    
    # Recent activity
    recent_activity = []
    for annotation in recent_annotations.data[-10:]:  # Last 10 annotations
        recent_activity.append({
            "type": "annotation",
            "description": f"Annotated text with {annotation['model_used']}",
            "timestamp": annotation["created_at"],
            "cost": annotation.get("cost", 0)
        })
    
    return {
        "totals": {
            "annotations": total_annotations.count,
            "projects": total_projects.count,
            "tagsets": total_tagsets.count,
            "total_cost": total_cost
        },
        "recent": {
            "annotations_last_30_days": len(recent_annotations.data),
            "cost_last_30_days": recent_cost
        },
        "recent_activity": recent_activity
    }


@router.get("/analytics")
async def get_analytics(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get detailed analytics"""
    # Get all annotations for analysis
    annotations = db.table("annotations")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .execute()
    
    # Model usage statistics
    model_usage = {}
    cost_by_model = {}
    tokens_by_model = {}
    
    for annotation in annotations.data:
        model = annotation.get("model_used", "unknown")
        cost = float(annotation.get("cost", 0))
        tokens = int(annotation.get("tokens_used", 0))
        
        model_usage[model] = model_usage.get(model, 0) + 1
        cost_by_model[model] = cost_by_model.get(model, 0) + cost
        tokens_by_model[model] = tokens_by_model.get(model, 0) + tokens
    
    # Daily annotation counts (last 30 days)
    daily_counts = {}
    for annotation in annotations.data:
        date_str = annotation["created_at"][:10]  # Extract date part
        daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
    
    # Cost analysis by tag set
    tagset_costs = {}
    for annotation in annotations.data:
        # This would need tag set info - simplified for now
        tagset_costs["default"] = tagset_costs.get("default", 0) + float(annotation.get("cost", 0))
    
    return {
        "model_usage": model_usage,
        "cost_by_model": cost_by_model,
        "tokens_by_model": tokens_by_model,
        "daily_annotation_counts": daily_counts,
        "cost_by_tagset": tagset_costs
    }


@router.get("/cost-estimation")
async def get_cost_estimation(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get cost estimation and budget tracking"""
    # Get annotations from current month
    current_month = datetime.utcnow().strftime("%Y-%m")
    month_start = f"{current_month}-01T00:00:00"
    
    monthly_annotations = db.table("annotations")\
        .select("cost, tokens_used, model_used")\
        .eq("user_id", current_user["id"])\
        .gte("created_at", month_start)\
        .execute()
    
    monthly_cost = sum(float(ann.get("cost", 0)) for ann in monthly_annotations.data)
    monthly_tokens = sum(int(ann.get("tokens_used", 0)) for ann in monthly_annotations.data)
    
    # Calculate average cost per annotation
    if monthly_annotations.data:
        avg_cost = monthly_cost / len(monthly_annotations.data)
        avg_tokens = monthly_tokens / len(monthly_annotations.data)
    else:
        avg_cost = 0
        avg_tokens = 0
    
    # Estimate costs for different models (per 1000 tokens)
    cost_estimates = {
        "gpt-4": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "claude-3": {"input": 0.008, "output": 0.024}
    }
    
    return {
        "current_month": {
            "total_cost": monthly_cost,
            "total_tokens": monthly_tokens,
            "annotation_count": len(monthly_annotations.data),
            "average_cost_per_annotation": avg_cost,
            "average_tokens_per_annotation": avg_tokens
        },
        "cost_estimates_per_1k_tokens": cost_estimates
    }
