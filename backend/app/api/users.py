from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import base64
from cryptography.fernet import Fernet
import os

from app.api.auth import get_current_user
from app.database import get_db, get_admin_db
from app.config import settings

router = APIRouter()

# Encryption key for API keys (in production, use a proper key management system)
def get_encryption_key():
    """Get or create encryption key for API keys"""
    key_env = os.getenv('API_KEY_ENCRYPTION_KEY')
    if key_env:
        return key_env.encode()
    
    # For development, create a consistent key based on secret
    key_material = hashlib.sha256(settings.secret_key.encode()).digest()
    return base64.urlsafe_b64encode(key_material)

def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage"""
    if not api_key:
        return ""
    
    fernet = Fernet(get_encryption_key())
    return fernet.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from storage"""
    if not encrypted_key:
        return ""
    
    try:
        fernet = Fernet(get_encryption_key())
        return fernet.decrypt(encrypted_key.encode()).decode()
    except:
        return ""

def mask_api_key(encrypted_key: str) -> str:
    """Return a masked version of the API key for display"""
    if not encrypted_key:
        return ""
    
    try:
        decrypted = decrypt_api_key(encrypted_key)
        if not decrypted:
            return ""
        
        if decrypted.startswith("sk-ant-"):
            return f"sk-ant-***{decrypted[-4:]}"
        elif decrypted.startswith("sk-"):
            return f"sk-***{decrypted[-4:]}"
        else:
            return "***"
    except:
        return ""


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: str
    updated_at: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class ApiKeySettings(BaseModel):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        avatar_url=current_user.get("avatar_url"),
        is_active=current_user.get("is_active", True),
        created_at=current_user["created_at"],
        updated_at=current_user.get("updated_at", current_user["created_at"])
    )


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update user profile"""
    update_data = {}
    
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.avatar_url is not None:
        update_data["avatar_url"] = user_update.avatar_url
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Update user in database
    result = db.table("users").update(update_data).eq("id", current_user["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = result.data[0]
    return UserProfile(
        id=updated_user["id"],
        email=updated_user["email"],
        full_name=updated_user.get("full_name"),
        avatar_url=updated_user.get("avatar_url"),
        is_active=updated_user.get("is_active", True),
        created_at=updated_user["created_at"],
        updated_at=updated_user.get("updated_at", updated_user["created_at"])
    )


@router.get("/api-keys")
async def get_api_keys(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_admin_db)
):
    """Get user's encrypted API keys (returns masked versions)"""
    try:
        # Get user's API keys from database
        result = db.table("user_api_keys").select("*").eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            return ApiKeySettings()
        
        keys_data = result.data[0]
        
        # Return masked versions for security
        return {
            "openai_api_key": mask_api_key(keys_data.get("openai_api_key_encrypted", "")),
            "anthropic_api_key": mask_api_key(keys_data.get("anthropic_api_key_encrypted", ""))
        }
    except Exception:
        return ApiKeySettings()


@router.put("/api-keys")
async def update_api_keys(
    api_keys: ApiKeySettings,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_admin_db)
):
    """Update user's API keys"""
    try:
        update_data = {}
        
        if api_keys.openai_api_key is not None:
            # Don't update if it's a masked value
            if not api_keys.openai_api_key.startswith("sk-***"):
                update_data["openai_api_key_encrypted"] = encrypt_api_key(api_keys.openai_api_key)
        
        if api_keys.anthropic_api_key is not None:
            # Don't update if it's a masked value
            if not api_keys.anthropic_api_key.startswith("sk-ant-***"):
                update_data["anthropic_api_key_encrypted"] = encrypt_api_key(api_keys.anthropic_api_key)
        
        if not update_data:
            return {"message": "No API keys to update"}
        
        # Check if user already has API keys record
        existing = db.table("user_api_keys").select("*").eq("user_id", current_user["id"]).execute()
        
        if existing.data:
            # Update existing record
            db.table("user_api_keys").update(update_data).eq("user_id", current_user["id"]).execute()
        else:
            # Create new record
            update_data["user_id"] = current_user["id"]
            db.table("user_api_keys").insert(update_data).execute()
        
        return {"message": "API keys updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update API keys: {str(e)}")


@router.get("/api-keys/decrypted")
async def get_decrypted_api_keys(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_admin_db)
):
    """Get user's decrypted API keys for internal use"""
    try:
        result = db.table("user_api_keys").select("*").eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            return ApiKeySettings()
        
        keys_data = result.data[0]
        
        return ApiKeySettings(
            openai_api_key=decrypt_api_key(keys_data.get("openai_api_key_encrypted", "")),
            anthropic_api_key=decrypt_api_key(keys_data.get("anthropic_api_key_encrypted", ""))
        )
    except Exception:
        return ApiKeySettings()


@router.get("/stats")
async def get_user_stats(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user statistics"""
    try:
        # Count annotations
        annotations_result = db.table("annotations")\
            .select("*", count="exact")\
            .eq("user_id", current_user["id"])\
            .execute()
        
        # Count projects
        projects_result = db.table("projects")\
            .select("*", count="exact")\
            .eq("user_id", current_user["id"])\
            .execute()
        
        # Count files
        files_result = db.table("files")\
            .select("*", count="exact")\
            .eq("user_id", current_user["id"])\
            .execute()
        
        # Calculate total cost from usage_stats
        usage_result = db.table("usage_stats")\
            .select("cost")\
            .eq("user_id", current_user["id"])\
            .execute()
        
        total_cost = sum(float(usage.get("cost", 0)) for usage in usage_result.data) if usage_result.data else 0
        
        # Count total tokens
        total_tokens = sum(int(usage.get("tokens_used", 0)) for usage in usage_result.data) if usage_result.data else 0
        
        return {
            "annotations_count": annotations_result.count or 0,
            "projects_count": projects_result.count or 0,
            "files_count": files_result.count or 0,
            "total_cost": round(total_cost, 2),
            "total_tokens": total_tokens
        }
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {
            "annotations_count": 0,
            "projects_count": 0,
            "files_count": 0,
            "total_cost": 0.0,
            "total_tokens": 0
        }
