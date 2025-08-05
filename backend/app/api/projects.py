from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.api.auth import get_current_user
from app.database import get_db

router = APIRouter()


class Project(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    tagset_id: str
    created_at: Optional[datetime] = None


class ProjectWithStats(BaseModel):
    id: str
    name: str
    description: str
    tagset_id: str
    annotations_count: int
    total_cost: float
    created_at: datetime


@router.post("/", response_model=Project)
async def create_project(
    project: Project,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new project"""
    project_data = {
        "name": project.name,
        "description": project.description,
        "tagset_id": project.tagset_id,
        "user_id": current_user["id"],
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = db.table("projects").insert(project_data).execute()
    return Project(**result.data[0])


@router.get("/", response_model=List[ProjectWithStats])
async def get_projects(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's projects with statistics"""
    projects = db.table("projects")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .order("created_at", desc=True)\
        .execute()
    
    projects_with_stats = []
    for project in projects.data:
        # Get annotation count for this project
        annotations = db.table("annotations")\
            .select("cost")\
            .eq("project_id", project["id"])\
            .execute()
        
        annotations_count = len(annotations.data)
        total_cost = sum(float(ann.get("cost", 0)) for ann in annotations.data)
        
        projects_with_stats.append(ProjectWithStats(
            **project,
            annotations_count=annotations_count,
            total_cost=total_cost
        ))
    
    return projects_with_stats


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get specific project"""
    project = db.table("projects")\
        .select("*")\
        .eq("id", project_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return Project(**project.data[0])


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project: Project,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update project"""
    update_data = {
        "name": project.name,
        "description": project.description,
        "tagset_id": project.tagset_id,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = db.table("projects")\
        .update(update_data)\
        .eq("id", project_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return Project(**result.data[0])


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete project and all associated annotations"""
    # Delete associated annotations
    db.table("annotations")\
        .delete()\
        .eq("project_id", project_id)\
        .execute()
    
    # Delete project
    result = db.table("projects")\
        .delete()\
        .eq("id", project_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Project deleted successfully"}
