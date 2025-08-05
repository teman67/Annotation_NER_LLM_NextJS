from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from app.api.auth import get_current_user
from app.database import get_db

router = APIRouter()


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    created_at: str


class UserUpdate(BaseModel):
    full_name: str


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(**current_user)


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update user profile"""
    result = db.table("users")\
        .update({"full_name": user_update.full_name})\
        .eq("id", current_user["id"])\
        .execute()
    
    return UserProfile(**result.data[0])


@router.get("/stats")
async def get_user_stats(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user statistics"""
    # Count annotations
    annotations_count = db.table("annotations")\
        .select("*", count="exact")\
        .eq("user_id", current_user["id"])\
        .execute()
    
    # Count tag sets
    tagsets_count = db.table("tag_sets")\
        .select("*", count="exact")\
        .eq("user_id", current_user["id"])\
        .execute()
    
    # Count files
    files_count = db.table("uploaded_files")\
        .select("*", count="exact")\
        .eq("user_id", current_user["id"])\
        .execute()
    
    # Calculate total cost
    total_cost = db.table("annotations")\
        .select("cost")\
        .eq("user_id", current_user["id"])\
        .execute()
    
    cost_sum = sum(float(annotation.get("cost", 0)) for annotation in total_cost.data)
    
    return {
        "annotations_count": annotations_count.count,
        "tagsets_count": tagsets_count.count,
        "files_count": files_count.count,
        "total_cost": cost_sum
    }
