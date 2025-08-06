#!/usr/bin/env python3
"""
Test database API key retrieval process
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_database_api_key_retrieval():
    """Test the actual database API key retrieval"""
    
    print("🧪 Testing database API key retrieval...")
    print("=" * 50)
    
    try:
        from app.database import get_db, get_admin_db
        from app.api.users import decrypt_api_key
        
        print("🗄️  Testing database connections:")
        
        # Test regular database connection
        try:
            db = get_db()
            print("   ✅ Regular database connection successful")
        except Exception as e:
            print(f"   ❌ Regular database connection failed: {e}")
            
        # Test admin database connection
        try:
            admin_db = get_admin_db()
            print("   ✅ Admin database connection successful")
        except Exception as e:
            print(f"   ❌ Admin database connection failed: {e}")
            return
        
        # Test querying the user_api_keys table
        print("\n🔍 Testing user_api_keys table access:")
        
        # Try with regular database (this might fail due to RLS)
        try:
            regular_result = db.table("user_api_keys").select("*").limit(1).execute()
            print(f"   ✅ Regular DB query successful: {len(regular_result.data)} rows")
        except Exception as e:
            print(f"   ❌ Regular DB query failed: {e}")
        
        # Try with admin database
        try:
            admin_result = admin_db.table("user_api_keys").select("*").limit(1).execute()
            print(f"   ✅ Admin DB query successful: {len(admin_result.data)} rows")
            
            # If we have data, test decryption
            if admin_result.data:
                print("\n🔓 Testing decryption of actual database data:")
                sample_data = admin_result.data[0]
                
                if sample_data.get("openai_api_key_encrypted"):
                    decrypted_openai = decrypt_api_key(sample_data["openai_api_key_encrypted"])
                    print(f"   OpenAI key decrypted: {'✓' if decrypted_openai else '✗'}")
                
                if sample_data.get("anthropic_api_key_encrypted"):
                    decrypted_anthropic = decrypt_api_key(sample_data["anthropic_api_key_encrypted"])
                    print(f"   Anthropic key decrypted: {'✓' if decrypted_anthropic else '✗'}")
            else:
                print("   ℹ️  No API keys in database to test")
                
        except Exception as e:
            print(f"   ❌ Admin DB query failed: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
        
        # Test the specific query used in annotation endpoint
        print("\n🎯 Testing annotation endpoint query pattern:")
        fake_user_id = "test-user-id-123"
        
        try:
            api_keys_result = admin_db.table("user_api_keys").select("*").eq("user_id", fake_user_id).execute()
            print(f"   Query executed successfully, found {len(api_keys_result.data)} records")
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
        
        print("\n📋 Diagnosis:")
        print("   - If regular DB fails but admin DB works: RLS policy issue (expected)")
        print("   - If both fail: Database connection or table structure issue")
        print("   - If decryption fails: Encryption key mismatch")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎉 Database testing completed!")

if __name__ == "__main__":
    test_database_api_key_retrieval()
