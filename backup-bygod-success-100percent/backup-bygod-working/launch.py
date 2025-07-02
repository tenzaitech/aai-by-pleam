"""
One-Click Launcher - รันครั้งเดียว
ไฟล์เดียวที่รันระบบทั้งหมด
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

class OneClickLauncher:
    def __init__(self):
        self.system_name = "AI-Powered Chrome Automation System"
        self.version = "1.0.0"
        self.creator = "WAWA"
        
    async def launch(self):
        """รันระบบ"""
        print("🎯 One-Click Launcher")
        print(f"🚀 {self.system_name} v{self.version}")
        print(f"🧠 สร้างโดย {self.creator}")
        print("👑 พระเจ้าของฉัน: คุณ")
        print("=" * 50)
        
        # ตรวจสอบ dependencies
        if not self.check_dependencies():
            print("📦 ติดตั้ง dependencies...")
            if not self.install_dependencies():
                return 1
        
        # ตั้งค่าสภาพแวดล้อม
        self.setup_environment()
        
        # รันระบบหลัก
        return await self.run_main_system()
    
    def check_dependencies(self):
        """ตรวจสอบ dependencies"""
        try:
            import selenium
            import openai
            import pythainlp
            return True
        except ImportError:
            return False
    
    def install_dependencies(self):
        """ติดตั้ง dependencies"""
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def setup_environment(self):
        """ตั้งค่าสภาพแวดล้อม"""
        print("🔧 ตั้งค่าสภาพแวดล้อม...")
        os.environ.setdefault("PYTHONPATH", str(Path(__file__).parent))
        
        # สร้างโฟลเดอร์
        for dir_name in ['logs', 'screenshots', 'data', 'temp']:
            Path(dir_name).mkdir(exist_ok=True)
    
    async def run_main_system(self):
        """รันระบบหลัก"""
        try:
            print("🚀 เริ่มต้นระบบ...")
            
            # Import ระบบ
            from master_controller import FullSystemLauncher
            
            # สร้าง instance
            master = FullSystemLauncher()
            
            # เริ่มต้นระบบ
            return await master.launch_full_system()
            
            # ระบบจะทำงานต่อใน launch_full_system()
            pass
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            return 1
        
        return 0

async def main():
    """ฟังก์ชันหลัก"""
    launcher = OneClickLauncher()
    return await launcher.launch()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
