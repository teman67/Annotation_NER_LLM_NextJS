#!/usr/bin/env python3
"""
Test script to simulate the annotation API call and identify the 500 error
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

async def test_annotation_api():
    try:
        print("🧪 Testing annotation API simulation...")
        
        # Import all required modules
        from app.api.annotations import AnnotationRequest, create_annotation
        from app.api.auth import get_current_user
        from app.database import get_db
        
        print("✅ All imports successful")
        
        # Mock user
        mock_user = {
            "id": "test-user-id",
            "email": "test@example.com",
            "full_name": "Test User"
        }
        
        # Mock database
        class MockDB:
            def table(self, table_name):
                return MockTable()
        
        class MockTable:
            def select(self, *args):
                return self
            def eq(self, field, value):
                return self
            def execute(self):
                return MockResult()
        
        class MockResult:
            data = []  # Empty data to simulate no API keys
        
        mock_db = MockDB()
        
        # Create annotation request
        request = AnnotationRequest(
            text="John Doe visited Paris last summer and climbed Mount Everest with Alice Smith.",
            tag_definitions=[
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
            ],
            model="gpt-4o-mini"
        )
        
        print("✅ Test request created")
        print(f"📝 Text: {request.text}")
        print(f"🤖 Model: {request.model}")
        print(f"🏷️  Tags: {[tag['tag_name'] for tag in request.tag_definitions]}")
        
        try:
            # This should trigger the API key error
            result = await create_annotation(request, mock_user, mock_db)
            print(f"❌ Unexpected success: {result}")
        
        except Exception as e:
            print(f"✅ Expected error caught: {e}")
            print(f"🔍 Error type: {type(e)}")
        
        print("🎉 API simulation test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_annotation_api())
