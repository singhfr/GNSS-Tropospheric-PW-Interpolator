#!/usr/bin/env python3
"""
Start GNSS Dashboard Services
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend server...")
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    try:
        # Start backend process
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], cwd=backend_dir, creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        print(f"✅ Backend started (PID: {process.pid})")
        print("📍 API: http://localhost:8000")
        print("📍 Docs: http://localhost:8000/docs")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the Next.js frontend"""
    print("\n🚀 Starting frontend server...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    try:
        # Start frontend process
        process = subprocess.Popen([
            "pnpm", "dev"
        ], cwd=frontend_dir, creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        print(f"✅ Frontend started (PID: {process.pid})")
        print("📍 Dashboard: http://localhost:3000")
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    print("🎯 GNSS Dashboard - Starting Services")
    print("=" * 50)
    
    # Start backend
    backend_process = start_backend()
    
    # Wait a moment
    time.sleep(2)
    
    # Start frontend
    frontend_process = start_frontend()
    
    if backend_process and frontend_process:
        print("\n🎉 All services started successfully!")
        print("\n📋 Quick Start:")
        print("1. Wait 10-15 seconds for services to fully start")
        print("2. Open http://localhost:3000 in your browser")
        print("3. Click 'Load Demo Data' to see the interpolation")
        print("\n⏹️  To stop services, close the console windows or press Ctrl+C")
        
        try:
            # Keep script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            if backend_process:
                backend_process.terminate()
            if frontend_process:
                frontend_process.terminate()
    else:
        print("\n❌ Failed to start some services")
        print("Try running manually:")
        print("Backend: cd backend && python -m uvicorn app.main:app --reload")
        print("Frontend: cd frontend && pnpm dev")

if __name__ == "__main__":
    main()
