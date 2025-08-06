#!/usr/bin/env python3

import requests
import json
import sys
import os

# Add the app directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

API_BASE_URL = "http://127.0.0.1:8000"

def test_login():
    """Test login and get token"""
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    print("🔐 Testing login...")
    response = requests.post(f"{API_BASE_URL}/api/auth/login", json=login_data)
    print(f"Login Response Status: {response.status_code}")
    print(f"Login Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print("❌ Login failed!")
        return None

def test_authenticated_endpoints(token):
    """Test the export, validate, and fix endpoints"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data
    test_export_data = {
        "text": "This is a test text.",
        "annotations": [
            {
                "start_char": 0,
                "end_char": 4,
                "text": "This",
                "label": "TEST"
            }
        ],
        "format_type": "json",
        "include_metadata": True
    }
    
    test_validate_data = {
        "text": "This is a test text.",
        "annotations": [
            {
                "start_char": 0,
                "end_char": 4,
                "text": "This",
                "label": "TEST"
            }
        ]
    }
    
    test_fix_data = {
        "text": "This is a test text.",
        "annotations": [
            {
                "start_char": 0,
                "end_char": 4,
                "text": "This",
                "label": "TEST"
            }
        ],
        "strategy": "fuzzy_match"
    }
    
    # Test export endpoint
    print("\n📤 Testing export endpoint...")
    response = requests.post(f"{API_BASE_URL}/api/annotations/export", 
                           headers=headers, json=test_export_data)
    print(f"Export Response Status: {response.status_code}")
    print(f"Export Response: {response.text[:500]}...")
    
    # Test validate endpoint
    print("\n✅ Testing validate endpoint...")
    response = requests.post(f"{API_BASE_URL}/api/annotations/validate", 
                           headers=headers, json=test_validate_data)
    print(f"Validate Response Status: {response.status_code}")
    print(f"Validate Response: {response.text[:500]}...")
    
    # Test fix endpoint
    print("\n🔧 Testing fix endpoint...")
    response = requests.post(f"{API_BASE_URL}/api/annotations/fix", 
                           headers=headers, json=test_fix_data)
    print(f"Fix Response Status: {response.status_code}")
    print(f"Fix Response: {response.text[:500]}...")

def main():
    print("🧪 Testing authentication endpoints...")
    
    # Use a pre-created token for testing
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbWlyaG9zc2Vpbi5iYXlhbmlAZ21haWwuY29tIiwidXNlcl9pZCI6IjdmZmU4OGEzLTUzMDQtNDdiNS04YWFlLTNkOTM5MmI0OGIxOCIsImV4cCI6MTc1NDQ4ODAwNSwiaWF0IjoxNzU0NDg2MjA1fQ.gVUUabtxhCnEP7Vy4bsxQVuCaF4psu2Krtzs7wdvxUc"
    
    print(f"🎫 Using token: {token[:20]}...")
    
    # Test authenticated endpoints
    test_authenticated_endpoints(token)

if __name__ == "__main__":
    main()
