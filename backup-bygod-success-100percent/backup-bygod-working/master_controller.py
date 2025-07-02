
"""
Full System Launcher
รันระบบแบบเต็มรูปแบบ
"""

import asyncio
import sys
import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class FullSystemLauncher:
    def __init__(self):
        self.logger = self.setup_logger()
        self.config = self.load_config()
        self.status = {"running": False, "components": {}}
        
    def setup_logger(self):
        """ตั้งค่า logging แบบเต็มรูปแบบ"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "system.log"),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
        
    def load_config(self):
        """โหลดการตั้งค่า"""
        config_path = Path("config/system.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.get_default_config()
        
    def get_default_config(self):
        """การตั้งค่าเริ่มต้นแบบเต็มรูปแบบ"""
        return {
            "system": {
                "name": "AI-Powered Chrome Automation",
                "version": "1.0.0",
                "auto_start": True
            },
            "chrome": {
                "headless": False,
                "timeout": 30,
                "window_size": "1920x1080"
            },
            "ai": {
                "enabled": True,
                "provider": "openai",
                "model": "gpt-4-vision-preview"
            },
            "thai": {
                "enabled": True,
                "ocr_confidence": 0.5
            },
            "logging": {
                "level": "INFO",
                "file_rotation": True
            }
        }
        
    async def initialize_components(self):
        """เริ่มต้น components ทั้งหมด"""
        self.logger.info("🔧 เริ่มต้น components...")
        
        components = [
            ("Chrome Controller", self.init_chrome),
            ("Thai Processor", self.init_thai),
            ("AI Integration", self.init_ai),
            ("Visual Recognition", self.init_visual)
        ]
        
        for name, init_func in components:
            try:
                await init_func()
                self.status["components"][name] = "ready"
                self.logger.info(f"✅ {name} พร้อม")
            except Exception as e:
                self.status["components"][name] = "error"
                self.logger.error(f"❌ {name} ผิดพลาด: {e}")
                
    async def init_chrome(self):
        """เริ่มต้น Chrome Controller"""
        from core.chrome_controller import AIChromeController
        api_key = os.getenv("OPENAI_API_KEY", "")
        self.chrome_controller = AIChromeController(api_key)
        await self.chrome_controller.start_ai_browser(
            headless=self.config["chrome"]["headless"]
        )
        
    async def init_thai(self):
        """เริ่มต้น Thai Processor"""
        from core.thai_processor import FullThaiProcessor
        self.thai_processor = FullThaiProcessor()
        
    async def init_ai(self):
        """เริ่มต้น AI Integration"""
        if self.config["ai"]["enabled"]:
            from core.ai_integration import MultimodalAIIntegration
            api_key = os.getenv("OPENAI_API_KEY")
            # ใช้ AI Integration แม้ไม่มี API Key (จะใช้ Local Processing)
            self.ai_integration = MultimodalAIIntegration(api_key)
            
    async def init_visual(self):
        """เริ่มต้น Visual Recognition"""
        from core.visual_recognition import VisualRecognition
        self.visual_recognition = VisualRecognition()
        
    async def launch_full_system(self):
        """รันระบบแบบเต็มรูปแบบ"""
        self.logger.info("🚀 เริ่มต้นระบบแบบเต็มรูปแบบ")
        self.logger.info(f"📋 ระบบ: {self.config['system']['name']} v{self.config['system']['version']}")
        
        try:
            # เริ่มต้น components
            await self.initialize_components()
            
            # ตรวจสอบสถานะ
            ready_components = sum(1 for status in self.status["components"].values() if status == "ready")
            total_components = len(self.status["components"])
            
            self.logger.info(f"📊 Components พร้อม: {ready_components}/{total_components}")
            
            if ready_components == total_components:
                self.status["running"] = True
                self.logger.info("✅ ระบบพร้อมใช้งานเต็มรูปแบบ")
                
                # รันระบบหลัก
                await self.run_main_system()
            else:
                self.logger.warning("⚠️ บาง components ไม่พร้อม แต่จะรันต่อ")
                await self.run_main_system()
                
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาด: {e}")
            return 1
            
        return 0
        
    async def run_main_system(self):
        """รันระบบหลัก"""
        self.logger.info("🎯 เริ่มรันระบบหลัก")
        
        # ตัวอย่างการใช้งาน
        if hasattr(self, 'chrome_controller'):
            await self.chrome_controller.ai_navigate("https://www.google.com", "เปิดหน้า Google")
            self.logger.info("🌐 เปิด Google แล้ว")
            
        # รันระบบต่อ (สามารถเพิ่ม logic ได้)
        self.logger.info("🔄 ระบบทำงานต่อ...")
        
    def get_system_status(self):
        """ดูสถานะระบบ"""
        return self.status

async def main():
    """ฟังก์ชันหลัก"""
    launcher = FullSystemLauncher()
    return await launcher.launch_full_system()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
