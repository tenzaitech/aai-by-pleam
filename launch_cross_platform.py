#!/usr/bin/env python3
"""
WAWAGOT V.2 Cross-Platform Launcher
ทำงานได้ทั้ง Windows, Linux, macOS
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def get_system_info():
    """Get system information"""
    return {
        'os': platform.system(),
        'version': platform.version(),
        'architecture': platform.architecture()[0],
        'python_version': sys.version
    }

def run_command(command, shell=False):
    """Run command with proper error handling"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def setup_environment():
    """Setup environment based on OS"""
    system = platform.system().lower()
    
    print("=" * 60)
    print("WAWAGOT V.2 - Cross-Platform Launcher")
    print("=" * 60)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Architecture: {platform.architecture()[0]}")
    print()
    
    # Create necessary directories
    directories = ['logs', 'screenshots', 'data', 'temp', 'frontend', 'backups']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    
    return system

def setup_virtual_environment():
    """Setup virtual environment"""
    venv_path = Path(".venv-gpu")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        success, output = run_command([sys.executable, "-m", "venv", ".venv-gpu"])
        if not success:
            print(f"Error creating virtual environment: {output}")
            return False
    
    return True

def activate_venv():
    """Activate virtual environment based on OS"""
    system = platform.system().lower()
    
    if system == "windows":
        # Windows
        activate_script = ".venv-gpu\\Scripts\\activate"
        python_path = ".venv-gpu\\Scripts\\python.exe"
    else:
        # Unix/Linux/macOS
        activate_script = ".venv-gpu/bin/activate"
        python_path = ".venv-gpu/bin/python"
    
    # Set environment variables
    os.environ['VIRTUAL_ENV'] = str(Path(".venv-gpu").absolute())
    os.environ['PATH'] = f"{Path('.venv-gpu/Scripts' if system == 'windows' else '.venv-gpu/bin').absolute()}{os.pathsep}{os.environ['PATH']}"
    
    return python_path

def check_dependencies(python_path):
    """Check if all dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'openai', 'selenium',
        'supabase', 'pandas', 'numpy', 'cv2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        success, output = run_command([python_path, "-c", f"import {package}"])
        if success:
            print(f"✅ {package} - Ready")
        else:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        success, output = run_command([python_path, "-m", "pip", "install", "-r", "requirements_v2_finetuned.txt"])
        if not success:
            print(f"Error installing dependencies: {output}")
            return False
    
    return True

def run_system(python_path):
    """Run WAWAGOT V.2 system"""
    print("\nStarting WAWAGOT V.2...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        # Run the launcher
        subprocess.run([python_path, "launch_v2.py"])
    except KeyboardInterrupt:
        print("\nReceived stop signal")
    except Exception as e:
        print(f"Error running system: {e}")
        return False
    
    return True

def main():
    """Main function"""
    try:
        # Setup environment
        system = setup_environment()
        
        # Setup virtual environment
        if not setup_virtual_environment():
            return 1
        
        # Activate virtual environment
        python_path = activate_venv()
        
        # Check dependencies
        if not check_dependencies(python_path):
            return 1
        
        # Run system
        if not run_system(python_path):
            return 1
        
        print("\nWAWAGOT V.2 stopped successfully")
        return 0
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 