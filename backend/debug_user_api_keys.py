#!/usr/bin/env python3
"""
Debug script to help diagnose API key issues during annotation
Run this script when you encounter the "API key not configured" error
"""

import sys
import os
from pathlib import Path
import uuid

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def debug_user_api_keys(user_email: str = None, user_id: str = None):
    """Debug API key retrieval for a specific user"""
    
    print("🔍 API Key Debug Tool")
    print("=" * 60)
    
    try:
        from app.database import get_db, get_admin_db
        from app.api.users import decrypt_api_key, encrypt_api_key
        
        # Get database connections
        db = get_db()
        admin_db = get_admin_db()
        
        print("✅ Database connections established")
        
        # If user_id is provided, use it directly
        if user_id:
            print(f"🎯 Looking up user by ID: {user_id}")
            user_result = admin_db.table("users").select("*").eq("id", user_id).execute()
        elif user_email:
            print(f"🎯 Looking up user by email: {user_email}")
            user_result = admin_db.table("users").select("*").eq("email", user_email).execute()
        else:
            print("📋 Listing all users with API keys:")
            # Get all users who have API keys
            api_keys_result = admin_db.table("user_api_keys").select("user_id").execute()
            if api_keys_result.data:
                user_ids = [item["user_id"] for item in api_keys_result.data]
                print(f"   Found {len(user_ids)} users with API keys")
                
                for uid in user_ids[:5]:  # Show first 5
                    user_result = admin_db.table("users").select("email").eq("id", uid).execute()
                    if user_result.data:
                        print(f"   - {uid}: {user_result.data[0]['email']}")
                
                if len(user_ids) > 5:
                    print(f"   ... and {len(user_ids) - 5} more")
                    
                print("\nℹ️  Run with specific email: python debug_user_api_keys.py your-email@example.com")
                return
            else:
                print("   No users with API keys found")
                return
        
        if not user_result.data:
            print("❌ User not found")
            return
        
        user = user_result.data[0]
        user_id = user["id"]
        user_email = user["email"]
        
        print(f"👤 User found:")
        print(f"   ID: {user_id}")
        print(f"   Email: {user_email}")
        print(f"   Name: {user.get('full_name', 'N/A')}")
        
        # Check API keys
        print(f"\n🔍 Checking API keys for user {user_id}...")
        
        # Try with regular database first
        try:
            regular_result = db.table("user_api_keys").select("*").eq("user_id", user_id).execute()
            print(f"📊 Regular DB query: {len(regular_result.data)} records")
        except Exception as e:
            print(f"📊 Regular DB query failed: {e}")
        
        # Try with admin database
        admin_result = admin_db.table("user_api_keys").select("*").eq("user_id", user_id).execute()
        print(f"📊 Admin DB query: {len(admin_result.data)} records")
        
        if admin_result.data:
            keys_data = admin_result.data[0]
            print(f"\n🔑 API Key data found:")
            print(f"   Created: {keys_data.get('created_at', 'N/A')}")
            print(f"   Updated: {keys_data.get('updated_at', 'N/A')}")
            
            # Check encrypted keys
            openai_encrypted = keys_data.get("openai_api_key_encrypted", "")
            anthropic_encrypted = keys_data.get("anthropic_api_key_encrypted", "")
            
            print(f"\n🔐 Encrypted keys:")
            print(f"   OpenAI: {'✓' if openai_encrypted else '✗'} ({len(openai_encrypted)} chars)")
            print(f"   Anthropic: {'✓' if anthropic_encrypted else '✗'} ({len(anthropic_encrypted)} chars)")
            
            # Try decryption
            print(f"\n🔓 Decryption test:")
            try:
                if openai_encrypted:
                    openai_decrypted = decrypt_api_key(openai_encrypted)
                    print(f"   OpenAI: {'✓' if openai_decrypted else '✗'} ({len(openai_decrypted)} chars)")
                    if openai_decrypted:
                        print(f"   OpenAI preview: {openai_decrypted[:10]}...{openai_decrypted[-4:]}")
                
                if anthropic_encrypted:
                    anthropic_decrypted = decrypt_api_key(anthropic_encrypted)
                    print(f"   Anthropic: {'✓' if anthropic_decrypted else '✗'} ({len(anthropic_decrypted)} chars)")
                    if anthropic_decrypted:
                        print(f"   Anthropic preview: {anthropic_decrypted[:15]}...{anthropic_decrypted[-4:]}")
                        
            except Exception as e:
                print(f"   ❌ Decryption failed: {e}")
            
            # Test LLM service initialization
            print(f"\n🤖 Testing LLM service initialization:")
            try:
                from app.services.llm_service import LLMService
                
                user_api_keys = {
                    "openai_api_key": decrypt_api_key(openai_encrypted) if openai_encrypted else None,
                    "anthropic_api_key": decrypt_api_key(anthropic_encrypted) if anthropic_encrypted else None
                }
                
                llm_service = LLMService(user_api_keys=user_api_keys)
                print(f"   OpenAI client available: {llm_service.has_openai_client()}")
                print(f"   Anthropic client available: {llm_service.has_anthropic_client()}")
                
                if not llm_service.has_openai_client() and not llm_service.has_anthropic_client():
                    print("   ❌ No LLM clients available!")
                    print("   💡 This explains the 'API key not configured' error")
                
            except Exception as e:
                print(f"   ❌ LLM service test failed: {e}")
                import traceback
                traceback.print_exc()
        
        else:
            print("❌ No API keys found for this user")
            print("💡 User needs to add API keys in profile settings")
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎉 Debug completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Check if it's an email or UUID
        arg = sys.argv[1]
        if "@" in arg:
            debug_user_api_keys(user_email=arg)
        else:
            try:
                # Try to parse as UUID
                uuid.UUID(arg)
                debug_user_api_keys(user_id=arg)
            except ValueError:
                print(f"❌ Invalid argument: {arg}")
                print("Usage: python debug_user_api_keys.py <email@example.com> or <user-uuid>")
    else:
        debug_user_api_keys()  # Show all users
