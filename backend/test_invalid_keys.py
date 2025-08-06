#!/usr/bin/env python3
"""
Test with invalid API keys to see what happens
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

async def test_with_invalid_keys():
    try:
        print("🧪 Testing annotation with invalid API keys...")
        
        # Import services
        from app.services.llm_service import LLMService
        from app.services.cost_calculator import CostCalculator
        
        print("✅ Services imported successfully")
        
        # Test with invalid API keys (but properly formatted)
        invalid_user_keys = {
            "openai_api_key": "sk-invalid-key-for-testing-purposes-1234567890",
            "anthropic_api_key": "sk-ant-invalid-key-for-testing-purposes-1234567890"
        }
        
        # Initialize services
        llm_service = LLMService(user_api_keys=invalid_user_keys)
        cost_calc = CostCalculator()
        
        print("✅ Services initialized successfully")
        print(f"🔑 OpenAI client available: {llm_service.has_openai_client()}")
        print(f"🔑 Anthropic client available: {llm_service.has_anthropic_client()}")
        
        # Test tag definitions
        tag_definitions = [
            {
                "tag_name": "PERSON",
                "definition": "Names of people",
                "examples": "John Doe, Alice Smith"
            },
            {
                "tag_name": "LOCATION", 
                "definition": "Places and locations",
                "examples": "New York, Paris, Mount Everest"
            }
        ]
        
        # Test text
        test_text = "John Doe visited Paris last summer and climbed Mount Everest with Alice Smith."
        
        print("🤖 Testing annotation with invalid API key...")
        
        try:
            result = await llm_service.run_annotation_pipeline(
                text=test_text,
                tag_definitions=tag_definitions,
                model="gpt-4o-mini",
                temperature=0.1,
                max_tokens=1000,
                chunk_size=1000,
                overlap=50
            )
            
            print(f"❌ Unexpected success: {result}")
        
        except Exception as e:
            print(f"✅ Expected error caught: {e}")
            print(f"🔍 Error type: {type(e)}")
        
        print("🎉 Invalid key test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_with_invalid_keys())
