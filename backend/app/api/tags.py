from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.api.auth import get_current_user
from app.database import get_db

router = APIRouter()


class TagDefinition(BaseModel):
    name: str
    description: str
    color: str
    examples: List[str]
    validation_rules: Optional[Dict[str, Any]] = None


class TagSet(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    tags: List[TagDefinition]
    is_public: bool = False
    created_at: Optional[datetime] = None


@router.post("/tagsets", response_model=TagSet)
async def create_tagset(
    tagset: TagSet,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new tag set"""
    tagset_data = {
        "name": tagset.name,
        "description": tagset.description,
        "tags": [tag.dict() for tag in tagset.tags],
        "is_public": tagset.is_public,
        "user_id": current_user["id"],
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = db.table("tag_sets").insert(tagset_data).execute()
    return TagSet(**result.data[0])


@router.get("/tagsets", response_model=List[TagSet])
async def get_tagsets(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's tag sets and public ones"""
    # Get user's tag sets
    user_tagsets = db.table("tag_sets")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .execute()
    
    # Get public tag sets
    public_tagsets = db.table("tag_sets")\
        .select("*")\
        .eq("is_public", True)\
        .neq("user_id", current_user["id"])\
        .execute()
    
    all_tagsets = user_tagsets.data + public_tagsets.data
    return [TagSet(**tagset) for tagset in all_tagsets]


@router.get("/tagsets/{tagset_id}", response_model=TagSet)
async def get_tagset(
    tagset_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get specific tag set"""
    tagset = db.table("tag_sets")\
        .select("*")\
        .eq("id", tagset_id)\
        .execute()
    
    if not tagset.data:
        raise HTTPException(status_code=404, detail="Tag set not found")
    
    tagset_data = tagset.data[0]
    
    # Check if user has access (owner or public)
    if tagset_data["user_id"] != current_user["id"] and not tagset_data["is_public"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return TagSet(**tagset_data)


@router.put("/tagsets/{tagset_id}", response_model=TagSet)
async def update_tagset(
    tagset_id: str,
    tagset: TagSet,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update tag set (only owner can update)"""
    # Check ownership
    existing = db.table("tag_sets")\
        .select("*")\
        .eq("id", tagset_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not existing.data:
        raise HTTPException(status_code=404, detail="Tag set not found or access denied")
    
    update_data = {
        "name": tagset.name,
        "description": tagset.description,
        "tags": [tag.dict() for tag in tagset.tags],
        "is_public": tagset.is_public,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = db.table("tag_sets")\
        .update(update_data)\
        .eq("id", tagset_id)\
        .execute()
    
    return TagSet(**result.data[0])


@router.delete("/tagsets/{tagset_id}")
async def delete_tagset(
    tagset_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete tag set (only owner can delete)"""
    result = db.table("tag_sets")\
        .delete()\
        .eq("id", tagset_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Tag set not found or access denied")
    
    return {"message": "Tag set deleted successfully"}


@router.get("/predefined")
async def get_predefined_tagsets():
    """Get predefined tag sets for common annotation tasks"""
    predefined_tagsets = [
        {
            "name": "Biomedical NER",
            "description": "Named Entity Recognition for biomedical texts",
            "tags": [
                {
                    "name": "GENE",
                    "description": "Gene names and symbols",
                    "color": "#FF5722",
                    "examples": ["BRCA1", "TP53", "EGFR"]
                },
                {
                    "name": "PROTEIN",
                    "description": "Protein names",
                    "color": "#2196F3",
                    "examples": ["insulin", "hemoglobin", "cytochrome c"]
                },
                {
                    "name": "DISEASE",
                    "description": "Disease and disorder names",
                    "color": "#F44336",
                    "examples": ["cancer", "diabetes", "Alzheimer's disease"]
                },
                {
                    "name": "CHEMICAL",
                    "description": "Chemical compounds and drugs",
                    "color": "#4CAF50",
                    "examples": ["aspirin", "glucose", "ATP"]
                }
            ]
        },
        {
            "name": "Sentiment Analysis",
            "description": "Sentiment classification tags",
            "tags": [
                {
                    "name": "POSITIVE",
                    "description": "Positive sentiment expressions",
                    "color": "#4CAF50",
                    "examples": ["excellent", "amazing", "love it"]
                },
                {
                    "name": "NEGATIVE",
                    "description": "Negative sentiment expressions",
                    "color": "#F44336",
                    "examples": ["terrible", "hate", "disappointing"]
                },
                {
                    "name": "NEUTRAL",
                    "description": "Neutral sentiment expressions",
                    "color": "#9E9E9E",
                    "examples": ["okay", "average", "fine"]
                }
            ]
        }
    ]
    
    return predefined_tagsets
