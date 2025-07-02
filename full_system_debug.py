#!/usr/bin/env python3
"""
🔍 Full System Chrome Debug
ตรวจสอบทุกจุดใน C:/ และ D:/ ที่อาจทำให้ Chrome เปิดเอง
"""

import os
import sys
import time
import subprocess
import threading
import glob
from datetime import datetime
from pathlib import Path

def log_debug(message):
    """บันทึก debug log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 🔍 {message}")

def scan_python_files_for_selenium(directory):
    """สแกนไฟล์ Python ใน directory ที่มีการใช้ selenium"""
    selenium_files = []
    
    try:
        # หาไฟล์ Python ทั้งหมด
        python_files = glob.glob(os.path.join(directory, "**/*.py"), recursive=True)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # ตรวจสอบการใช้งาน selenium
                    if any(keyword in content for keyword in [
                        'webdriver.Chrome',
                        'selenium',
                        'from selenium',
                        'import selenium',
                        'Chrome(',
                        'Options()'
                    ]):
                        selenium_files.append(file_path)
                        
            except Exception as e:
                log_debug(f"Error reading {file_path}: {e}")
                
    except Exception as e:
        log_debug(f"Error scanning {directory}: {e}")
    
    return selenium_files

def monitor_chrome_processes():
    """ติดตาม Chrome processes แบบ real-time"""
    while True:
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe'], 
                                  capture_output=True, text=True)
            if 'chrome.exe' in result.stdout:
                log_debug(f"🚨 CHROME DETECTED:\n{result.stdout}")
            time.sleep(2)
        except Exception as e:
            log_debug(f"Monitor error: {e}")
            time.sleep(5)

def scan_drives():
    """สแกน C:/ และ D:/ สำหรับไฟล์ที่เกี่ยวข้องกับ Chrome automation"""
    log_debug("=== STARTING FULL DRIVE SCAN ===")
    
    drives_to_scan = ['C:', 'D:']
    
    for drive in drives_to_scan:
        if os.path.exists(drive):
            log_debug(f"Scanning drive {drive}...")
            
            # สแกนเฉพาะโฟลเดอร์ที่เกี่ยวข้อง
            relevant_dirs = [
                os.path.join(drive, 'FULL-AI-IDEA'),
                os.path.join(drive, 'Users'),
                os.path.join(drive, 'Program Files'),
                os.path.join(drive, 'Program Files (x86)'),
                os.path.join(drive, 'Python'),
                os.path.join(drive, 'Anaconda'),
                os.path.join(drive, 'Miniconda'),
            ]
            
            for dir_path in relevant_dirs:
                if os.path.exists(dir_path):
                    log_debug(f"Scanning {dir_path}...")
                    selenium_files = scan_python_files_for_selenium(dir_path)
                    
                    if selenium_files:
                        log_debug(f"Found {len(selenium_files)} files with selenium in {dir_path}")
                        for file_path in selenium_files[:10]:  # แสดงแค่ 10 ไฟล์แรก
                            log_debug(f"  - {file_path}")
                    else:
                        log_debug(f"No selenium files found in {dir_path}")

def test_current_project():
    """ทดสอบโปรเจกต์ปัจจุบัน"""
    log_debug("=== TESTING CURRENT PROJECT ===")
    
    # ทดสอบการ import modules
    try:
        import selenium
        log_debug(f"Selenium version: {selenium.__version__}")
    except Exception as e:
        log_debug(f"Selenium import error: {e}")
    
    # ทดสอบ Chrome Controller
    try:
        from core.chrome_controller import AIChromeController
        controller = AIChromeController()
        log_debug("Chrome Controller created successfully")
    except Exception as e:
        log_debug(f"Chrome Controller error: {e}")
    
    # ทดสอบ Dashboard
    try:
        import dashboard.app
        log_debug("Dashboard imported successfully")
    except Exception as e:
        log_debug(f"Dashboard error: {e}")

def check_running_processes():
    """ตรวจสอบ processes ที่กำลังทำงาน"""
    log_debug("=== CHECKING RUNNING PROCESSES ===")
    
    try:
        # ตรวจสอบ Python processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        log_debug(f"Python processes:\n{result.stdout}")
        
        # ตรวจสอบ Chrome processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe'], 
                              capture_output=True, text=True)
        log_debug(f"Chrome processes:\n{result.stdout}")
        
    except Exception as e:
        log_debug(f"Process check error: {e}")

def main():
    """Main debug function"""
    print("🔍 Full System Chrome Debug Started")
    print("=" * 60)
    
    # เริ่ม monitor Chrome processes
    monitor_thread = threading.Thread(target=monitor_chrome_processes, daemon=True)
    monitor_thread.start()
    log_debug("Chrome process monitor started")
    
    # ตรวจสอบ processes ที่กำลังทำงาน
    check_running_processes()
    
    # ทดสอบโปรเจกต์ปัจจุบัน
    test_current_project()
    
    # สแกน drives
    scan_drives()
    
    # รอให้ monitor ทำงาน
    print("\n🔍 Full system debug completed. Monitoring Chrome processes...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🔍 Debug stopped by user")

if __name__ == "__main__":
    main() 