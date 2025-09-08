#!/usr/bin/env python3
"""
Render.com startup script for the GNSS API backend
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment variables for Render
os.environ.setdefault("PYTHONPATH", str(backend_dir))
os.environ.setdefault("ENVIRONMENT", "production")

# Import and run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Starting GNSS API on port {port}")
    print(f"📁 Backend directory: {backend_dir}")
    print(f"🐍 Python path: {sys.path}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
