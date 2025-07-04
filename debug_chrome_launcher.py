#!/usr/bin/env python3
"""
🔍 Chrome Debug Launcher
ติดตามทุกการสร้าง webdriver.Chrome() ในระบบ
"""

import os
import sys
import time
import subprocess
import threading
from datetime import datetime

def log_debug(message):
    """บันทึก debug log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 🔍 {message}")

def monitor_chrome_processes():
    """ติดตาม Chrome processes - DISABLED"""
    while True:
        try:
            # result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq chrome.exe'], 
            #                       capture_output=True, text=True)
            # if 'chrome.exe' in result.stdout:
            #     log_debug(f"Chrome processes found:\n{result.stdout}")
            log_debug("Chrome monitoring disabled by user preference")
            time.sleep(10)
        except Exception as e:
            log_debug(f"Monitor error: {e}")
            time.sleep(10)

def start_chrome_monitor():
    """เริ่ม monitor Chrome processes"""
    monitor_thread = threading.Thread(target=monitor_chrome_processes, daemon=True)
    monitor_thread.start()
    log_debug("Chrome process monitor started")

def debug_import_selenium():
    """Debug การ import selenium"""
    log_debug("Testing selenium import...")
    try:
        import selenium
        log_debug(f"Selenium version: {selenium.__version__}")
        
        from selenium import webdriver
        log_debug("WebDriver imported successfully")
        
        from selenium.webdriver.chrome.options import Options
        log_debug("Chrome Options imported successfully")
        
    except Exception as e:
        log_debug(f"Selenium import error: {e}")

def debug_chrome_controller():
    """Debug Chrome Controller"""
    log_debug("Testing Chrome Controller...")
    try:
        from core.chrome_controller import AIChromeController
        log_debug("AIChromeController imported successfully")
        
        controller = AIChromeController()
        log_debug("AIChromeController instance created")
        
        return controller
    except Exception as e:
        log_debug(f"Chrome Controller error: {e}")
        return None

def debug_dashboard():
    """Debug Dashboard"""
    log_debug("Testing Dashboard...")
    try:
        import dashboard.app
        log_debug("Dashboard app imported successfully")
    except Exception as e:
        log_debug(f"Dashboard error: {e}")

def debug_smart_templates():
    """Debug Smart Templates"""
    log_debug("Testing Smart Templates...")
    try:
        import smart_templates
        log_debug("Smart Templates imported successfully")
        
        template = smart_templates.SmartTemplate()
        log_debug("SmartTemplate instance created")
        
    except Exception as e:
        log_debug(f"Smart Templates error: {e}")

def debug_all_modules():
    """Debug ทุก modules"""
    log_debug("=== STARTING FULL DEBUG ===")
    
    # Debug imports
    debug_import_selenium()
    
    # Debug modules
    debug_chrome_controller()
    debug_dashboard()
    debug_smart_templates()
    
    log_debug("=== FULL DEBUG COMPLETED ===")

def main():
    """Main debug function"""
    print("🔍 Chrome Debug Launcher Started")
    print("=" * 50)
    
    # เริ่ม monitor
    start_chrome_monitor()
    
    # Debug ทุก modules
    debug_all_modules()
    
    # รอให้ monitor ทำงาน
    print("\n🔍 Monitoring Chrome processes... Press Ctrl+C to stop")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🔍 Debug stopped by user")

if __name__ == "__main__":
    main() 