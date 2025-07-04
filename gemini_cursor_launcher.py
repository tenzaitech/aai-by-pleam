#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini Cursor Integration Launcher
Launcher script สำหรับระบบ Gemini Cursor Integration
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """ตรวจสอบ environment และ dependencies"""
    logger.info("🔍 ตรวจสอบ environment...")
    
    # ตรวจสอบ Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        logger.error("❌ ต้องการ Python 3.8 หรือสูงกว่า")
        return False
    
    logger.info(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # ตรวจสอบ virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.info("✅ Virtual environment ใช้งานอยู่")
    else:
        logger.warning("⚠️ ไม่ได้ใช้งาน virtual environment")
    
    return True

def check_dependencies():
    """ตรวจสอบ dependencies ที่จำเป็น"""
    logger.info("🔍 ตรวจสอบ dependencies...")
    
    required_packages = [
        'flask',
        'flask-socketio',
        'google-generativeai',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package}")
        except ImportError:
            logger.warning(f"❌ {package} - ไม่พบ")
            missing_packages.append(package)
    
    if missing_packages:
        logger.info("📦 ติดตั้ง dependencies ที่ขาดหาย...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            logger.info("✅ ติดตั้ง dependencies สำเร็จ")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ ไม่สามารถติดตั้ง dependencies ได้: {e}")
            return False
    
    return True

def check_cursor_path():
    """ตรวจสอบ path ของ Cursor"""
    logger.info("🔍 ตรวจสอบ Cursor path...")
    
    username = os.getenv('USERNAME', 'pleam')
    cursor_paths = [
        rf"C:\Users\{username}\AppData\Local\Programs\cursor\Cursor.exe",
        rf"C:\Users\{username}\AppData\Roaming\cursor\Cursor.exe",
        r"C:\Program Files\Cursor\Cursor.exe",
        r"C:\Program Files (x86)\Cursor\Cursor.exe"
    ]
    
    for path in cursor_paths:
        if os.path.exists(path):
            logger.info(f"✅ พบ Cursor ที่: {path}")
            return path
    
    logger.warning("⚠️ ไม่พบ Cursor ในระบบ")
    return None

def check_api_key():
    """ตรวจสอบ Google API Key"""
    logger.info("🔍 ตรวจสอบ Google API Key...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        logger.info("✅ พบ Google API Key")
        return True
    else:
        logger.warning("⚠️ ไม่พบ GOOGLE_API_KEY environment variable")
        logger.info("💡 ตั้งค่า API Key ด้วยคำสั่ง:")
        logger.info("   set GOOGLE_API_KEY=your_api_key_here")
        return False

def create_config_file():
    """สร้างไฟล์ config หากไม่มี"""
    config_file = Path("gemini_cursor_config.json")
    
    if not config_file.exists():
        logger.info("📝 สร้างไฟล์ config...")
        
        config = {
            "cursor_path": check_cursor_path(),
            "api_key": os.getenv('GOOGLE_API_KEY'),
            "port": 8002,
            "host": "0.0.0.0",
            "debug": True
        }
        
        import json
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info("✅ สร้างไฟล์ config สำเร็จ")
        return config_file
    
    return config_file

def start_system():
    """เริ่มต้นระบบ Gemini Cursor Integration"""
    logger.info("🚀 เริ่มต้นระบบ Gemini Cursor Integration...")
    
    try:
        # ตรวจสอบไฟล์หลัก
        main_file = Path("gemini_cursor_integration.py")
        if not main_file.exists():
            logger.error("❌ ไม่พบไฟล์ gemini_cursor_integration.py")
            return False
        
        # รันระบบ
        logger.info("🌐 เริ่มต้น WebApp ที่ http://localhost:8002")
        subprocess.run([sys.executable, "gemini_cursor_integration.py"])
        
    except KeyboardInterrupt:
        logger.info("⏹️ หยุดระบบโดยผู้ใช้")
    except Exception as e:
        logger.error(f"❌ เกิดข้อผิดพลาด: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 Gemini Cursor Integration Launcher")
    print("=" * 60)
    
    # ตรวจสอบ environment
    if not check_environment():
        return False
    
    # ตรวจสอบ dependencies
    if not check_dependencies():
        return False
    
    # ตรวจสอบ Cursor
    cursor_path = check_cursor_path()
    if not cursor_path:
        logger.warning("⚠️ ระบบจะทำงานได้จำกัดหากไม่พบ Cursor")
    
    # ตรวจสอบ API Key
    if not check_api_key():
        logger.warning("⚠️ ระบบจะไม่สามารถใช้งาน Gemini AI ได้")
    
    # สร้าง config file
    config_file = create_config_file()
    
    print("\n" + "=" * 60)
    print("✅ ระบบพร้อมใช้งาน!")
    print("=" * 60)
    print("📋 สรุปการตรวจสอบ:")
    print(f"   • Python: ✅")
    print(f"   • Dependencies: ✅")
    print(f"   • Cursor: {'✅' if cursor_path else '⚠️'}")
    print(f"   • API Key: {'✅' if check_api_key() else '⚠️'}")
    print(f"   • Config: ✅ ({config_file})")
    print("\n🌐 เปิด browser ไปที่: http://localhost:8002")
    print("📝 ตัวอย่างคำสั่ง:")
    print("   • เปิดไฟล์ test.py ใน Cursor")
    print("   • รันคำสั่ง python script.py")
    print("   • เปิดเว็บไซต์ google.com")
    print("\n⏹️ กด Ctrl+C เพื่อหยุดระบบ")
    print("=" * 60)
    
    # เริ่มต้นระบบ
    return start_system()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 