#!/usr/bin/env python3
"""
Test script to isolate the annotation endpoint issue
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

async def test_annotation():
    try:
        print("🧪 Testing annotation pipeline...")
        
        # Import services
        from app.services.llm_service import LLMService
        from app.services.cost_calculator import CostCalculator
        
        print("✅ Services imported successfully")
        
        # Initialize services
        llm_service = LLMService()
        cost_calc = CostCalculator()
        
        print("✅ Services initialized successfully")
        
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
        
        print("✅ Tag definitions created")
        
        # Test text
        test_text = "John Doe visited Paris last summer and climbed Mount Everest with Alice Smith."
        
        print("✅ Test text prepared")
        print(f"📝 Text: {test_text}")
        print(f"🏷️  Tags: {[tag['tag_name'] for tag in tag_definitions]}")
        
        # Check if we have API keys
        print(f"🔑 OpenAI client available: {llm_service.has_openai_client()}")
        print(f"🔑 Anthropic client available: {llm_service.has_anthropic_client()}")
        
        if not llm_service.has_openai_client() and not llm_service.has_anthropic_client():
            print("⚠️  No API keys configured. Cannot test LLM annotation.")
            return
        
        # Test annotation pipeline
        model = "gpt-4o-mini" if llm_service.has_openai_client() else "claude-3-haiku-20240307"
        
        print(f"🤖 Testing with model: {model}")
        
        result = await llm_service.run_annotation_pipeline(
            text=test_text,
            tag_definitions=tag_definitions,
            model=model,
            temperature=0.1,
            max_tokens=1000,
            chunk_size=1000,
            overlap=50
        )
        
        print("✅ Annotation pipeline completed successfully")
        print(f"📊 Results:")
        print(f"   - Total entities: {result['statistics']['total_entities']}")
        print(f"   - Total tokens: {result['statistics']['total_tokens']}")
        print(f"   - Entities: {result['entities']}")
        
        # Test cost calculation
        if result['statistics']['total_input_tokens'] > 0:
            cost = cost_calc.calculate_cost(
                model=model,
                input_tokens=result['statistics']['total_input_tokens'],
                output_tokens=result['statistics']['total_output_tokens']
            )
            print(f"💰 Cost: ${cost['total_cost']:.4f}")
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_annotation())
