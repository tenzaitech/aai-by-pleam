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
from performance_optimizer import PerformanceOptimizer
from smart_batcher import SmartBatcher, BatchJob
from core.backup_controller import BackupController
from enhanced_integration import FullSystemIntegration

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
            # 1. Optimize system ก่อนเริ่ม
            optimizer = PerformanceOptimizer()
            await optimizer.optimize_system()

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

                # 3. Integrate Enhanced Integration แบบเต็มรูปแบบ
                self.logger.info("🚀 เริ่ม Enhanced Integration Test")
                enhanced_integration = FullSystemIntegration()
                integration_results = await enhanced_integration.run_full_integration_test()
                
                self.logger.info(f"📊 Enhanced Integration Results:")
                self.logger.info(f"   - งานทั้งหมด: {integration_results['total_tasks']}")
                self.logger.info(f"   - สำเร็จ: {integration_results['successful_tasks']}")
                self.logger.info(f"   - อัตราความสำเร็จ: {integration_results['success_rate']:.1f}%")
                self.logger.info(f"   - ประสิทธิภาพ Parallel: {integration_results['parallel_efficiency']:.2f}x")

                # 2. Integrate SmartBatcher กับ logic backup จริง
                batcher = SmartBatcher(max_concurrent=3)
                backup_controller = BackupController()
                # ตัวอย่าง: backup ทุกโฟลเดอร์ใน data/
                data_dir = Path("data")
                if data_dir.exists():
                    for item in data_dir.iterdir():
                        if item.is_dir() or item.is_file():
                            batcher.add_job(BatchJob(
                                f"Backup {item.name}",
                                self._backup_job,
                                (str(item), backup_controller),
                                priority=1
                            ))
                    results = await batcher.process_batch()
                    print("📊 Batch Results:", results)
                else:
                    print("❌ ไม่พบโฟลเดอร์ data/ สำหรับ backup")
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

    @staticmethod
    async def _backup_job(source_path, backup_controller):
        loop = asyncio.get_event_loop()
        # เรียกใช้ create_backup แบบ sync ใน thread pool
        return await loop.run_in_executor(None, backup_controller.create_backup, source_path)

async def main():
    """ฟังก์ชันหลัก"""
    launcher = FullSystemLauncher()
    return await launcher.launch_full_system()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
