from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import aiofiles
import os
from datetime import datetime

from app.api.auth import get_current_user
from app.database import get_db
from app.config import settings

router = APIRouter()


class FileInfo(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size: int
    content_type: str
    uploaded_at: datetime


@router.post("/upload", response_model=FileInfo)
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Upload a text file for annotation"""
    # Validate file type
    allowed_types = ["text/plain", "application/json", "text/csv"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only text files (.txt, .json, .csv) are allowed"
        )
    
    # Validate file size
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
        )
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_user['id']}_{timestamp}_{file.filename}"
    file_path = os.path.join(settings.upload_dir, filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Save file info to database
    file_data = {
        "filename": filename,
        "original_name": file.filename,
        "file_size": len(content),
        "content_type": file.content_type,
        "file_path": file_path,
        "user_id": current_user["id"],
        "uploaded_at": datetime.utcnow().isoformat()
    }
    
    result = db.table("uploaded_files").insert(file_data).execute()
    
    return FileInfo(**result.data[0])


@router.get("/", response_model=List[FileInfo])
async def get_files(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's uploaded files"""
    files = db.table("uploaded_files")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .order("uploaded_at", desc=True)\
        .execute()
    
    return [FileInfo(**file_data) for file_data in files.data]


@router.get("/{file_id}/content")
async def get_file_content(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get file content for annotation"""
    file_info = db.table("uploaded_files")\
        .select("*")\
        .eq("id", file_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not file_info.data:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_data = file_info.data[0]
    file_path = file_data["file_path"]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
        content = await f.read()
    
    return {
        "file_id": file_id,
        "filename": file_data["original_name"],
        "content": content,
        "content_type": file_data["content_type"]
    }


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Download file"""
    file_info = db.table("uploaded_files")\
        .select("*")\
        .eq("id", file_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not file_info.data:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_data = file_info.data[0]
    file_path = file_data["file_path"]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=file_data["original_name"],
        media_type=file_data["content_type"]
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete uploaded file"""
    file_info = db.table("uploaded_files")\
        .select("*")\
        .eq("id", file_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not file_info.data:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_data = file_info.data[0]
    file_path = file_data["file_path"]
    
    # Delete file from disk
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete from database
    db.table("uploaded_files").delete().eq("id", file_id).execute()
    
    return {"message": "File deleted successfully"}


@router.post("/{file_id}/process")
async def process_file(
    file_id: str,
    tagset_id: str,
    model: str = "gpt-4",
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Process entire file for annotation"""
    # Get file content
    file_content = await get_file_content(file_id, current_user, db)
    
    # Get tag set
    tagset = db.table("tag_sets")\
        .select("*")\
        .eq("id", tagset_id)\
        .execute()
    
    if not tagset.data:
        raise HTTPException(status_code=404, detail="Tag set not found")
    
    # Process file with LLM service
    from app.services.file_processor import FileProcessor
    
    processor = FileProcessor()
    result = await processor.process_file(
        content=file_content["content"],
        tagset=tagset.data[0],
        model=model,
        user_id=current_user["id"]
    )
    
    return result
