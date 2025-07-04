#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Dashboard Launcher
ใช้ Python ระบบและติดตั้ง dependencies อัตโนมัติ
"""

import os
import sys
import subprocess
import importlib

def install_package(package):
    """Install package if not available"""
    try:
        importlib.import_module(package)
        print(f"✅ {package} - Already installed")
        return True
    except ImportError:
        print(f"📦 Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} - Installed successfully")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False

def setup_dependencies():
    """Setup required dependencies"""
    packages = [
        'flask',
        'flask_socketio', 
        'psutil',
        'requests'
    ]
    
    print("📦 Checking and installing dependencies...")
    for package in packages:
        if not install_package(package):
            return False
    return True

def start_dashboard():
    """Start the dashboard"""
    try:
        # Change to system directory
        system_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'system')
        os.chdir(system_dir)
        
        print(f"📁 Changed to directory: {system_dir}")
        
        # Import and run dashboard
        sys.path.insert(0, system_dir)
        
        # Import dashboard app
        from dashboard.app import app, socketio
        
        print("🚀 Starting Dashboard...")
        print("📊 Dashboard will be available at: http://localhost:8000")
        print("📊 Real-time Monitor: http://localhost:8000/real-time-monitor")
        print("Press Ctrl+C to stop")
        
        # Run the app
        socketio.run(app, host='0.0.0.0', port=8000, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🎯 WAWAGOT V.2.5 - Simple Dashboard Launcher")
    print("=" * 50)
    
    # Setup dependencies
    if not setup_dependencies():
        print("\n❌ Failed to setup dependencies")
        return 1
    
    # Start dashboard
    if not start_dashboard():
        print("\n❌ Failed to start dashboard")
        return 1
    
    print("\n✅ Dashboard launcher completed")
    return 0

if __name__ == "__main__":
    exit(main()) 