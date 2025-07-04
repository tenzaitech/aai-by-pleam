#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment Cards for Backup-byGod
แสดงข้อมูล Environment ของโปรแกรมต่างๆ แบบง่าย
"""

import os
import sys
import platform
import psutil
import json
from datetime import datetime
from typing import Dict, List, Any
import subprocess

class EnvironmentCards:
    """Environment Cards Controller"""
    
    def __init__(self):
        self.cards = {}
        self.update_interval = 30  # อัปเดตทุก 30 วินาที
        self.last_update = None
        
    def get_system_info(self) -> Dict[str, Any]:
        """ข้อมูลระบบพื้นฐาน"""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": sys.version,
            "architecture": platform.architecture()[0],
            "hostname": platform.node(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_total": psutil.disk_usage('/').total
        }
    
    def get_python_environment(self) -> Dict[str, Any]:
        """ข้อมูล Python Environment"""
        try:
            # ดึงข้อมูล packages ที่ติดตั้ง
            result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'], 
                                  capture_output=True, text=True)
            packages = json.loads(result.stdout) if result.returncode == 0 else []
            
            return {
                "python_path": sys.executable,
                "pip_version": self._get_pip_version(),
                "virtual_env": os.environ.get('VIRTUAL_ENV', 'Not activated'),
                "installed_packages": len(packages),
                "key_packages": self._get_key_packages(packages)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_chrome_environment(self) -> Dict[str, Any]:
        """ข้อมูล Chrome Environment"""
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser"
        ]
        
        chrome_info = {"installed": False, "version": "Unknown", "path": "Not found"}
        
        for path in chrome_paths:
            if os.path.exists(path):
                try:
                    result = subprocess.run([path, '--version'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        chrome_info = {
                            "installed": True,
                            "version": result.stdout.strip(),
                            "path": path
                        }
                        break
                except:
                    continue
        
        return chrome_info
    
    def get_database_environment(self) -> Dict[str, Any]:
        """ข้อมูล Database Environment"""
        databases = {}
        
        # SQLite
        try:
            import sqlite3
            databases["sqlite"] = {
                "available": True,
                "version": sqlite3.sqlite_version
            }
        except:
            databases["sqlite"] = {"available": False}
        
        # PostgreSQL
        try:
            import psycopg2
            databases["postgresql"] = {"available": True}
        except:
            databases["postgresql"] = {"available": False}
        
        # Supabase
        try:
            from supabase import create_client
            databases["supabase"] = {"available": True}
        except:
            databases["supabase"] = {"available": False}
        
        return databases
    
    def get_ai_environment(self) -> Dict[str, Any]:
        """ข้อมูล AI Environment"""
        ai_libs = {}
        
        # TensorFlow
        try:
            import tensorflow as tf
            gpu_available = False
            try:
                gpu_available = len(tf.config.list_physical_devices('GPU')) > 0
            except:
                gpu_available = False
                
            ai_libs["tensorflow"] = {
                "available": True,
                "version": tf.__version__,
                "gpu_available": gpu_available
            }
        except:
            ai_libs["tensorflow"] = {"available": False}
        
        # OpenCV
        try:
            import cv2
            ai_libs["opencv"] = {
                "available": True,
                "version": cv2.__version__
            }
        except:
            ai_libs["opencv"] = {"available": False}
        
        # EasyOCR
        try:
            import easyocr
            ai_libs["easyocr"] = {"available": True}
        except:
            ai_libs["easyocr"] = {"available": False}
        
        # Selenium
        try:
            import selenium
            ai_libs["selenium"] = {
                "available": True,
                "version": selenium.__version__
            }
        except:
            ai_libs["selenium"] = {"available": False}
        
        return ai_libs
    
    def get_network_environment(self) -> Dict[str, Any]:
        """ข้อมูล Network Environment"""
        try:
            import requests
            
            # ทดสอบการเชื่อมต่ออินเทอร์เน็ต
            response = requests.get("https://httpbin.org/ip", timeout=5)
            external_ip = response.json().get("origin", "Unknown")
            
            return {
                "internet_available": True,
                "external_ip": external_ip,
                "requests_available": True
            }
        except:
            return {
                "internet_available": False,
                "external_ip": "Unknown",
                "requests_available": False
            }
    
    def get_backup_environment(self) -> Dict[str, Any]:
        """ข้อมูล Backup Environment"""
        backup_dirs = ["backups", "data", "temp", "screenshots"]
        backup_status = {}
        
        for dir_name in backup_dirs:
            dir_path = os.path.join(os.getcwd(), dir_name)
            if os.path.exists(dir_path):
                try:
                    size = sum(os.path.getsize(os.path.join(dirpath, filename))
                              for dirpath, dirnames, filenames in os.walk(dir_path)
                              for filename in filenames)
                    file_count = sum(len(filenames) for dirpath, dirnames, filenames in os.walk(dir_path))
                    backup_status[dir_name] = {
                        "exists": True,
                        "size_bytes": size,
                        "file_count": file_count
                    }
                except:
                    backup_status[dir_name] = {"exists": True, "error": "Access denied"}
            else:
                backup_status[dir_name] = {"exists": False}
        
        return backup_status
    
    def generate_all_cards(self) -> Dict[str, Any]:
        """สร้าง Environment Cards ทั้งหมด"""
        self.cards = {
            "system": self.get_system_info(),
            "python": self.get_python_environment(),
            "chrome": self.get_chrome_environment(),
            "databases": self.get_database_environment(),
            "ai_libraries": self.get_ai_environment(),
            "network": self.get_network_environment(),
            "backup": self.get_backup_environment(),
            "last_update": datetime.now().isoformat()
        }
        
        self.last_update = datetime.now()
        return self.cards
    
    def get_card_summary(self) -> Dict[str, Any]:
        """สรุปสถานะ Environment Cards"""
        if not self.cards:
            self.generate_all_cards()
        
        summary = {
            "total_components": 0,
            "ready_components": 0,
            "issues": [],
            "recommendations": []
        }
        
        # ตรวจสอบ Python Environment
        if "error" not in self.cards["python"]:
            summary["total_components"] += 1
            summary["ready_components"] += 1
        else:
            summary["issues"].append("Python environment has issues")
        
        # ตรวจสอบ Chrome
        if self.cards["chrome"]["installed"]:
            summary["total_components"] += 1
            summary["ready_components"] += 1
        else:
            summary["issues"].append("Chrome not found")
            summary["recommendations"].append("Install Google Chrome for automation")
        
        # ตรวจสอบ AI Libraries
        ai_ready = sum(1 for lib in self.cards["ai_libraries"].values() if lib.get("available", False))
        summary["total_components"] += len(self.cards["ai_libraries"])
        summary["ready_components"] += ai_ready
        
        if ai_ready < len(self.cards["ai_libraries"]):
            summary["recommendations"].append("Install missing AI libraries")
        
        # ตรวจสอบ Network
        if self.cards["network"]["internet_available"]:
            summary["total_components"] += 1
            summary["ready_components"] += 1
        else:
            summary["issues"].append("No internet connection")
        
        # คำนวณ readiness percentage
        summary["readiness_percent"] = (summary["ready_components"] / summary["total_components"] * 100) if summary["total_components"] > 0 else 0
        
        return summary
    
    def _get_pip_version(self) -> str:
        """ดึง pip version"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except:
            return "Unknown"
    
    def _get_key_packages(self, packages: List[Dict]) -> List[str]:
        """ดึงรายชื่อ packages สำคัญ"""
        key_packages = ["tensorflow", "opencv", "selenium", "easyocr", "supabase", "flask", "requests"]
        found_packages = []
        
        for package in packages:
            if package.get("name", "").lower() in key_packages:
                found_packages.append(f"{package['name']} {package.get('version', 'unknown')}")
        
        return found_packages

# Global instance
env_cards = EnvironmentCards() 