#!/usr/bin/env python3
"""
Server startup script for the Scientific Text Annotator Backend.
This script ensures proper Python path setup and starts the FastAPI server.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Change working directory to backend
os.chdir(current_dir)

if __name__ == "__main__":
    import uvicorn
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(current_dir)],
        log_level="info"
    )
