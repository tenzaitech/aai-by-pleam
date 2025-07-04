#!/usr/bin/env python3
"""
WAWAGOT V.2 Simple Launcher
Runs API server without complex logging
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 WAWAGOT V.2 Simple Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("api_server.py").exists():
        print("❌ Error: api_server.py not found!")
        print("   Please run this script from the wawagot.ai directory")
        return 1
    
    # Check if uvicorn is available
    try:
        import uvicorn
        print("✅ Uvicorn found")
    except ImportError:
        print("❌ Uvicorn not found. Installing minimal dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements_minimal.txt"
            ], check=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return 1
    
    # Start the API server
    print("🌐 Starting API server at http://localhost:8000")
    print("   Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", "api_server:app",
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 