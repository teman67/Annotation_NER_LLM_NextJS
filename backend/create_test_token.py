#!/usr/bin/env python3

import sys
import os
from datetime import datetime, timedelta
import jwt

# Add the app directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings

def create_test_token():
    """Create a test JWT token for existing user"""
    print("🎫 Creating test JWT token...")
    
    # Use one of your existing users
    user_email = "amirhossein.bayani@gmail.com"
    user_id = "7ffe88a3-5304-47b5-8aae-3d9392b48b18"
    
    payload = {
        "sub": user_email,
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    print(f"✅ Created token for {user_email}")
    print(f"Token: {token}")
    return token

if __name__ == "__main__":
    create_test_token()
