#!/usr/bin/env python3

import sys
import os
from supabase import create_client

# Add the app directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings

def check_users():
    """Check what users exist in the database"""
    print("🔍 Checking users in database...")
    
    # Create admin client (bypasses RLS)
    supabase = create_client(settings.supabase_url, settings.supabase_service_key)
    
    try:
        # Get all users
        users_response = supabase.table("users").select("id, email, created_at").execute()
        
        print(f"📊 Found {len(users_response.data)} users:")
        for user in users_response.data:
            print(f"  - ID: {user['id']}")
            print(f"    Email: {user['email']}")
            print(f"    Created: {user['created_at']}")
            print()
            
        return users_response.data
        
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        return []

if __name__ == "__main__":
    check_users()
