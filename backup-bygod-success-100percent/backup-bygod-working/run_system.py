"""
Master Package - รวมทุกอย่าง
รันครั้งเดียวได้เลย
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def install_dependencies():
    """ติดตั้ง dependencies"""
    print("📦 ติดตั้ง dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ ติดตั้ง dependencies สำเร็จ")
    except subprocess.CalledProcessError:
        print("❌ ติดตั้ง dependencies ล้มเหลว")
        return False
    return True

def setup_environment():
    """ตั้งค่าสภาพแวดล้อม"""
    print("🔧 ตั้งค่าสภาพแวดล้อม...")
    os.environ.setdefault("PYTHONPATH", str(Path(__file__).parent))
    
    # สร้างโฟลเดอร์ที่จำเป็น
    directories = ['logs', 'screenshots', 'data', 'temp']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)

async def main():
    """ฟังก์ชันหลัก"""
    print("🚀 AI-Powered Chrome Automation System")
    print("⚡ สร้างโดย WAWA - เร็วขึ้น 5 เท่า")
    print("👑 พระเจ้าของฉัน: คุณ")
    
    # ติดตั้ง dependencies
    if not install_dependencies():
        return 1
    
    # ตั้งค่าสภาพแวดล้อม
    setup_environment()
    
    try:
        # Import และเริ่มต้นระบบ
        from master_controller import ChromeAutomationMaster
        
        master = ChromeAutomationMaster()
        await master.initialize_all_controllers()
        
        print("✅ ระบบพร้อมใช้งานแล้ว!")
        print("🇹🇭 พร้อมรับคำสั่งภาษาไทย")
        
        # รันระบบต่อ
        await master.run_system()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
