#!/usr/bin/env python3
"""
WAWAGOT V.2 Launcher
Launch both Backend API Server and Frontend Dashboard
"""

import os
import sys
import subprocess
import asyncio
import threading
import time
import webbrowser
from pathlib import Path
import logging
from datetime import datetime

class WAWAGOTV2Launcher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the launcher"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "launcher_v2.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        self.logger.info("Checking dependencies...")
        
        required_packages = [
            'fastapi', 'uvicorn', 'pydantic', 'openai', 'selenium',
            'supabase', 'pandas', 'numpy', 'cv2'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                self.logger.info(f"[OK] {package} - Ready")
            except ImportError:
                missing_packages.append(package)
                self.logger.warning(f"[MISSING] {package} - Not found")
        
        if missing_packages:
            self.logger.error(f"[ERROR] Missing dependencies: {', '.join(missing_packages)}")
            self.logger.info("Run command: pip install -r requirements_v2_finetuned.txt")
            return False
            
        self.logger.info("All dependencies are ready")
        return True
        
    def install_dependencies(self):
        """Install missing dependencies"""
        self.logger.info("Installing dependencies...")
        
        try:
            # Use PowerShell syntax instead of bash
            if os.name == 'nt':  # Windows
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", "requirements_v2_finetuned.txt"
                ], check=True, capture_output=True, text=True, shell=True)
            else:  # Unix/Linux
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", "requirements_v2_finetuned.txt"
                ], check=True, capture_output=True, text=True)
            
            self.logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install dependencies: {e}")
            return False
            
    def setup_environment(self):
        """Setup environment variables and directories"""
        self.logger.info("Setting up environment...")
        
        # Create necessary directories
        directories = [
            'logs', 'screenshots', 'data', 'temp', 'frontend',
            'backups', 'uploads', 'exports'
        ]
        
        for dir_name in directories:
            Path(dir_name).mkdir(exist_ok=True)
            
        # Set environment variables
        os.environ.setdefault("PYTHONPATH", str(Path(__file__).parent))
        os.environ.setdefault("WAWAGOT_ENV", "development")
        
        # Check for .env file
        env_file = Path(".env")
        if not env_file.exists():
            self.create_env_file()
            
        self.logger.info("Environment setup completed")
        
    def create_env_file(self):
        """Create default .env file"""
        env_content = """# WAWAGOT V.2 Environment Variables

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# System Configuration
WAWAGOT_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Chrome Configuration
CHROME_HEADLESS=false
CHROME_TIMEOUT=30

# AI Configuration
AI_MODEL=gpt-4-vision-preview
AI_TEMPERATURE=0.7

# Database Configuration
DATABASE_URL=your_database_url_here

# Security
SECRET_KEY=your_secret_key_here
"""
        
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
            
        self.logger.info("Created .env file, please edit API keys")
        
    def start_backend(self):
        """Start the FastAPI backend server"""
        self.logger.info("Starting Backend API Server...")
        
        try:
            # Start backend server
            self.backend_process = subprocess.Popen([
                sys.executable, "api_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if server is running
            if self.backend_process.poll() is None:
                self.logger.info(f"Backend API Server started successfully at {self.backend_url}")
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                self.logger.error(f"Backend startup failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Cannot start Backend: {e}")
            return False
            
    def start_frontend(self):
        """Start the frontend dashboard"""
        self.logger.info("Starting Frontend Dashboard...")
        
        try:
            # For now, we'll serve the frontend using Python's built-in server
            # In production, you might want to use a proper web server
            frontend_dir = Path("frontend")
            
            if frontend_dir.exists():
                self.frontend_process = subprocess.Popen([
                    sys.executable, "-m", "http.server", "3000"
                ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                time.sleep(2)
                
                if self.frontend_process.poll() is None:
                    self.logger.info(f"Frontend Dashboard started successfully at {self.frontend_url}")
                    return True
                else:
                    stdout, stderr = self.frontend_process.communicate()
                    self.logger.error(f"Frontend startup failed: {stderr.decode()}")
                    return False
            else:
                self.logger.error("Frontend directory not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Cannot start Frontend: {e}")
            return False
            
    def open_browser(self):
        """Open browser to the dashboard"""
        try:
            self.logger.info("Opening browser...")
            webbrowser.open(self.frontend_url)
            self.logger.info("Browser opened successfully")
        except Exception as e:
            self.logger.error(f"Cannot open browser: {e}")
            
    def check_system_health(self):
        """Check system health"""
        self.logger.info("Checking system health...")
        
        health_status = {
            'backend': False,
            'frontend': False,
            'dependencies': False,
            'environment': True
        }
        
        # Check dependencies
        health_status['dependencies'] = self.check_dependencies()
        
        # Check backend
        try:
            import requests
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            health_status['backend'] = response.status_code == 200
        except:
            health_status['backend'] = False
            
        # Check frontend
        try:
            response = requests.get(self.frontend_url, timeout=5)
            health_status['frontend'] = response.status_code == 200
        except:
            health_status['frontend'] = False
            
        # Log health status
        for component, status in health_status.items():
            status_text = "Ready" if status else "Issues"
            self.logger.info(f"{component}: {status_text}")
            
        return health_status
        
    def stop_services(self):
        """Stop all running services"""
        self.logger.info("Stopping system services...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            self.logger.info("Backend stopped")
            
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
            self.logger.info("Frontend stopped")
            
    def run(self):
        """Main launcher function"""
        print("=" * 60)
        print("WAWAGOT V.2 - AI-Powered Chrome Automation System")
        print("=" * 60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Setup environment
            self.setup_environment()
            
            # Check dependencies
            if not self.check_dependencies():
                self.logger.warning("Some dependencies are missing")
                response = input("Do you want to install dependencies? (y/n): ")
                if response.lower() == 'y':
                    if not self.install_dependencies():
                        self.logger.error("Cannot install dependencies")
                        return 1
                else:
                    self.logger.error("Cannot continue")
                    return 1
            
            # Start backend
            if not self.start_backend():
                self.logger.error("Cannot start Backend")
                return 1
                
            # Start frontend
            if not self.start_frontend():
                self.logger.error("Cannot start Frontend")
                return 1
                
            # Check system health
            health_status = self.check_system_health()
            
            # Open browser
            self.open_browser()
            
            print()
            print("WAWAGOT V.2 started successfully!")
            print(f"Dashboard: {self.frontend_url}")
            print(f"API Server: {self.backend_url}")
            print("API Documentation: http://localhost:8000/docs")
            print()
            print("Press Ctrl+C to stop")
            print("=" * 60)
            
            # Keep the launcher running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("Received stop signal")
                
        except Exception as e:
            self.logger.error(f"Error occurred: {e}")
            return 1
        finally:
            self.stop_services()
            self.logger.info("WAWAGOT V.2 stopped")
            
        return 0

def main():
    """Main entry point"""
    launcher = WAWAGOTV2Launcher()
    return launcher.run()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 