#!/usr/bin/env python3
"""
Test API key storage and retrieval process
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_api_key_encryption():
    """Test the encryption and decryption process"""
    
    print("🧪 Testing API key encryption/decryption...")
    print("=" * 50)
    
    try:
        from app.api.users import encrypt_api_key, decrypt_api_key
        
        # Test with a fake OpenAI API key
        test_openai_key = "sk-test1234567890abcdef1234567890abcdef1234567890"
        test_anthropic_key = "sk-ant-test1234567890abcdef1234567890abcdef1234567890"
        
        print("🔐 Testing encryption:")
        encrypted_openai = encrypt_api_key(test_openai_key)
        encrypted_anthropic = encrypt_api_key(test_anthropic_key)
        
        print(f"   Original OpenAI key: {test_openai_key}")
        print(f"   Encrypted: {encrypted_openai[:50]}...")
        
        print(f"   Original Anthropic key: {test_anthropic_key}")
        print(f"   Encrypted: {encrypted_anthropic[:50]}...")
        
        print("\n🔓 Testing decryption:")
        decrypted_openai = decrypt_api_key(encrypted_openai)
        decrypted_anthropic = decrypt_api_key(encrypted_anthropic)
        
        print(f"   Decrypted OpenAI key: {decrypted_openai}")
        print(f"   Decrypted Anthropic key: {decrypted_anthropic}")
        
        # Verify they match
        if decrypted_openai == test_openai_key and decrypted_anthropic == test_anthropic_key:
            print("\n✅ Encryption/decryption working correctly!")
        else:
            print("\n❌ Encryption/decryption mismatch!")
            
        # Test with empty/invalid keys
        print("\n🧪 Testing edge cases:")
        empty_result = decrypt_api_key("")
        print(f"   Empty string decryption: '{empty_result}'")
        
        invalid_result = decrypt_api_key("invalid-encrypted-data")
        print(f"   Invalid data decryption: '{invalid_result}'")
        
        # Test LLM service validation
        print("\n🤖 Testing LLM service validation:")
        from app.services.llm_service import LLMService
        
        valid_keys = {
            "openai_api_key": test_openai_key,
            "anthropic_api_key": test_anthropic_key
        }
        
        llm_service = LLMService(user_api_keys=valid_keys)
        print(f"   OpenAI client available: {llm_service.has_openai_client()}")
        print(f"   Anthropic client available: {llm_service.has_anthropic_client()}")
        
        # Test with empty keys
        empty_keys = {
            "openai_api_key": "",
            "anthropic_api_key": ""
        }
        
        llm_service_empty = LLMService(user_api_keys=empty_keys)
        print(f"   OpenAI client with empty key: {llm_service_empty.has_openai_client()}")
        print(f"   Anthropic client with empty key: {llm_service_empty.has_anthropic_client()}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎉 API key testing completed!")

if __name__ == "__main__":
    test_api_key_encryption()
