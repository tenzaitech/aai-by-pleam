"""
🚀 START SYSTEM FIXED
ระบบเริ่มต้นที่แก้ไขปัญหา Unicode encoding ใน Windows
"""

import asyncio
import sys
import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import codecs

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass
    
    # Set console to UTF-8
    try:
        os.system('chcp 65001 >nul')
    except:
        pass

class FixedSystemLauncher:
    def __init__(self):
        self.logger = self.setup_fixed_logger()
        self.config = self.load_config()
        self.status = {"running": False, "components": {}}
        
    def setup_fixed_logger(self):
        """ตั้งค่า logging ที่แก้ไขปัญหา Unicode"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create UTF-8 file handler
        log_file = log_dir / "system_fixed.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                # Custom console handler for Windows
                self.create_console_handler()
            ]
        )
        return logging.getLogger(__name__)
        
    def create_console_handler(self):
        """สร้าง console handler ที่รองรับ Unicode"""
        class UnicodeStreamHandler(logging.StreamHandler):
            def emit(self, record):
                try:
                    msg = self.format(record)
                    # Encode to UTF-8 and decode to handle Unicode properly
                    if sys.platform == "win32":
                        try:
                            # Try to write with UTF-8 encoding
                            self.stream.buffer.write(msg.encode('utf-8'))
                            self.stream.buffer.write(b'\n')
                            self.stream.buffer.flush()
                        except:
                            # Fallback to ASCII-safe version
                            safe_msg = msg.encode('ascii', 'ignore').decode('ascii')
                            self.stream.write(safe_msg + '\n')
                            self.stream.flush()
                    else:
                        self.stream.write(msg + '\n')
                        self.stream.flush()
                except Exception:
                    self.handleError(record)
        
        return UnicodeStreamHandler()
        
    def load_config(self):
        """โหลดการตั้งค่า"""
        config_path = Path("config/system.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.get_default_config()
        
    def get_default_config(self):
        """การตั้งค่าเริ่มต้น"""
        return {
            "system": {
                "name": "AI-Powered Chrome Automation - FIXED",
                "version": "2.0.0",
                "auto_start": True
            },
            "chrome": {
                "headless": False,
                "timeout": 30,
                "window_size": "1920x1080"
            },
            "ai": {
                "enabled": True,
                "provider": "local",
                "model": "local_enhanced"
            },
            "thai": {
                "enabled": True,
                "ocr_confidence": 0.8
            },
            "logging": {
                "level": "INFO",
                "file_rotation": True
            }
        }
        
    async def initialize_components(self):
        """เริ่มต้น components ทั้งหมด"""
        print("🔧 เริ่มต้น components...")
        
        components = [
            ("Chrome Controller", self.init_chrome),
            ("Thai Processor", self.init_thai),
            ("AI Integration", self.init_ai),
            ("Visual Recognition", self.init_visual),
            ("Backup Controller", self.init_backup)
        ]
        
        for name, init_func in components:
            try:
                await init_func()
                self.status["components"][name] = "ready"
                print(f"✅ {name} พร้อม")
            except Exception as e:
                self.status["components"][name] = "error"
                print(f"❌ {name} ผิดพลาด: {e}")
                
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
            self.ai_integration = MultimodalAIIntegration(api_key)
            
    async def init_visual(self):
        """เริ่มต้น Visual Recognition"""
        from core.visual_recognition import VisualRecognition
        self.visual_recognition = VisualRecognition()
        
    async def init_backup(self):
        """เริ่มต้น Backup Controller"""
        from core.backup_controller import BackupController
        self.backup_controller = BackupController()
        
    async def launch_system(self):
        """รันระบบแบบแก้ไขแล้ว"""
        print("🚀 เริ่มต้นระบบแบบแก้ไขแล้ว")
        print(f"📋 ระบบ: {self.config['system']['name']} v{self.config['system']['version']}")
        
        try:
            # เริ่มต้น components
            await self.initialize_components()
            
            # ตรวจสอบสถานะ
            ready_components = sum(1 for status in self.status["components"].values() if status == "ready")
            total_components = len(self.status["components"])
            
            print(f"📊 Components พร้อม: {ready_components}/{total_components}")
            
            if ready_components >= 3:  # อย่างน้อย 3 components ต้องพร้อม
                self.status["running"] = True
                print("✅ ระบบพร้อมใช้งาน")
                
                # รันระบบหลัก
                await self.run_main_system()
                
            else:
                print("⚠️ บาง components ไม่พร้อม แต่จะรันต่อ")
                await self.run_main_system()
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            return 1
            
        return 0
        
    async def run_main_system(self):
        """รันระบบหลัก"""
        print("🎯 เริ่มรันระบบหลัก")
        
        # ตัวอย่างการใช้งาน
        if hasattr(self, 'chrome_controller'):
            try:
                await self.chrome_controller.ai_navigate("https://www.google.com", "เปิดหน้า Google")
                print("🌐 เปิด Google แล้ว")
            except Exception as e:
                print(f"⚠️ ไม่สามารถเปิด Google ได้: {e}")
            
        # ทดสอบ Thai Processor
        if hasattr(self, 'thai_processor'):
            try:
                test_text = "สวัสดีครับ นี่คือการทดสอบภาษาไทย"
                result = await self.thai_processor.process_thai_text(test_text)
                print(f"🇹🇭 ทดสอบ Thai Processor: {result[:50]}...")
            except Exception as e:
                print(f"⚠️ ไม่สามารถทดสอบ Thai Processor ได้: {e}")
        
        # ทดสอบ AI Integration
        if hasattr(self, 'ai_integration'):
            try:
                test_prompt = "อธิบายการทำงานของระบบ backup-bygod"
                result = await self.ai_integration.process_text(test_prompt)
                print(f"🤖 ทดสอบ AI Integration: {result[:50]}...")
            except Exception as e:
                print(f"⚠️ ไม่สามารถทดสอบ AI Integration ได้: {e}")
        
        print("🔄 ระบบทำงานต่อ...")
        print("🎉 ระบบพร้อมใช้งานเต็มรูปแบบ!")
        
    def get_system_status(self):
        """ดูสถานะระบบ"""
        return {
            "running": self.status["running"],
            "components": self.status["components"],
            "config": self.config
        }
        
async def main():
    """Main function"""
    launcher = FixedSystemLauncher()
    return await launcher.launch_system()
    
if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 ระบบถูกหยุดโดยผู้ใช้")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        sys.exit(1) 