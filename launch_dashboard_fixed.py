#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed Dashboard Launcher
แก้ไขปัญหา import paths และเริ่ม dashboard ที่ถูกต้อง
"""

import os
import sys
import subprocess
import time

def setup_environment():
    """Setup environment variables and paths"""
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Add system directory to path
    system_dir = os.path.join(current_dir, 'system')
    sys.path.insert(0, system_dir)
    
    # Set environment variables
    os.environ['PYTHONPATH'] = current_dir + os.pathsep + system_dir
    
    print("✅ Environment setup completed")
    print(f"📁 Current directory: {current_dir}")
    print(f"📁 System directory: {system_dir}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'flask_socketio', 'psutil', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def start_dashboard():
    """Start the dashboard with correct paths"""
    try:
        # Change to system directory
        system_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'system')
        os.chdir(system_dir)
        
        print(f"📁 Changed to directory: {system_dir}")
        
        # Start dashboard
        dashboard_script = os.path.join(system_dir, 'dashboard', 'app.py')
        
        if not os.path.exists(dashboard_script):
            print(f"❌ Dashboard script not found: {dashboard_script}")
            return False
        
        print("🚀 Starting Dashboard...")
        print("📊 Dashboard will be available at: http://localhost:8000")
        print("📊 Real-time Monitor: http://localhost:8000/real-time-monitor")
        print("Press Ctrl+C to stop")
        
        # Start the dashboard
        subprocess.run([sys.executable, dashboard_script])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🎯 WAWAGOT V.2.5 - Fixed Dashboard Launcher")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies check failed")
        return 1
    
    # Start dashboard
    if not start_dashboard():
        print("\n❌ Failed to start dashboard")
        return 1
    
    print("\n✅ Dashboard launcher completed")
    return 0

if __name__ == "__main__":
    exit(main()) 