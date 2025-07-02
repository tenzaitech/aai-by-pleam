#!/usr/bin/env python3
"""
Setup Script - ติดตั้งระบบ
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """ติดตั้ง dependencies"""
    print("📦 ติดตั้ง dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_environment():
    """ตั้งค่าสภาพแวดล้อม"""
    print("🔧 ตั้งค่าสภาพแวดล้อม...")
    
    # สร้างโฟลเดอร์ที่จำเป็น
    directories = ['logs', 'screenshots', 'data', 'temp']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    
    # สร้างไฟล์ .env ถ้ายังไม่มี
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write("# AI-Powered Chrome Automation Environment\n")
            f.write("OPENAI_API_KEY=your_api_key_here\n")

def test_installation():
    """ทดสอบการติดตั้ง"""
    print("🧪 ทดสอบการติดตั้ง...")
    
    try:
        import selenium
        import openai
        import pythainlp
        import easyocr
        print("✅ การติดตั้งสำเร็จ!")
        return True
    except ImportError as e:
        print(f"❌ การติดตั้งล้มเหลว: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 เริ่มติดตั้งระบบ AI-Powered Chrome Automation")
    print("⚡ สร้างโดย WAWA - เร็วขึ้น 5 เท่า")
    
    # ติดตั้ง dependencies
    install_dependencies()
    
    # ตั้งค่าสภาพแวดล้อม
    setup_environment()
    
    # ทดสอบการติดตั้ง
    if test_installation():
        print("🎯 ระบบพร้อมใช้งาน!")
        print("รัน: python run_system.py")
    else:
        print("❌ กรุณาติดตั้งใหม่")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
