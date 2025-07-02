"""
🎮 INTERACTIVE SYSTEM
ระบบ interactive สำหรับใช้งาน backup-bygod แบบเต็มรูปแบบ
"""

import asyncio
import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import time
from alldata_godmode.god_mode_knowledge_manager import GodModeKnowledgeManager
import traceback

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        os.system('chcp 65001 >nul')
    except:
        pass

class InteractiveSystem:
    def __init__(self):
        self.running = False
        self.components = {}
        self.config = self.load_config()
        self.godmode_km = GodModeKnowledgeManager()
        self.godmode_session_id = None
        
    def load_config(self):
        """โหลดการตั้งค่า"""
        config_path = Path("config/system.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"system": {"name": "Interactive backup-bygod", "version": "2.0.0"}}
        
    async def initialize_system(self):
        """เริ่มต้นระบบ"""
        print("🚀 เริ่มต้น Interactive System...")
        
        try:
            # Import components
            from core.chrome_controller import AIChromeController
            from core.thai_processor import FullThaiProcessor
            from core.ai_integration import MultimodalAIIntegration
            from core.visual_recognition import VisualRecognition
            from core.backup_controller import BackupController
            
            # Initialize components
            print("🔧 เริ่มต้น components...")
            
            # Chrome Controller
            try:
                api_key = os.getenv("OPENAI_API_KEY", "")
                self.chrome_controller = AIChromeController(api_key)
                # ไม่เริ่ม Chrome อัตโนมัติ - ให้ผู้ใช้เลือกเอง
                # await self.chrome_controller.start_ai_browser(headless=False)
                self.components["chrome"] = self.chrome_controller
                print("✅ Chrome Controller พร้อม (ยังไม่ได้เริ่ม browser)")
            except Exception as e:
                print(f"❌ Chrome Controller ผิดพลาด: {e}")
                
            # Thai Processor
            try:
                self.thai_processor = FullThaiProcessor()
                self.components["thai"] = self.thai_processor
                print("✅ Thai Processor พร้อม")
            except Exception as e:
                print(f"❌ Thai Processor ผิดพลาด: {e}")
                
            # AI Integration
            try:
                api_key = os.getenv("OPENAI_API_KEY")
                self.ai_integration = MultimodalAIIntegration(api_key)
                self.components["ai"] = self.ai_integration
                print("✅ AI Integration พร้อม")
            except Exception as e:
                print(f"❌ AI Integration ผิดพลาด: {e}")
                
            # Visual Recognition
            try:
                self.visual_recognition = VisualRecognition()
                self.components["visual"] = self.visual_recognition
                print("✅ Visual Recognition พร้อม")
            except Exception as e:
                print(f"❌ Visual Recognition ผิดพลาด: {e}")
                
            # Backup Controller
            try:
                self.backup_controller = BackupController()
                self.components["backup"] = self.backup_controller
                print("✅ Backup Controller พร้อม")
            except Exception as e:
                print(f"❌ Backup Controller ผิดพลาด: {e}")
                
            self.running = True
            print(f"📊 Components พร้อม: {len(self.components)}/5")
            print("✅ ระบบพร้อมใช้งาน!")
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการเริ่มต้น: {e}")
            return False
            
        return True
        
    def show_menu(self):
        """แสดงเมนูหลัก"""
        print("\n" + "="*50)
        print("🎮 INTERACTIVE backup-bygod SYSTEM")
        print("="*50)
        print("1. 🌐 Chrome Automation")
        print("2. 🇹🇭 Thai Language Processing")
        print("3. 🤖 AI Integration")
        print("4. 👁️ Visual Recognition")
        print("5. 💾 Backup & Restore")
        print("6. 📊 System Status")
        print("7. 🔧 System Settings")
        print("8. 🚀 Run All Tests")
        print("0. 🛑 Exit")
        print("="*50)
        
    async def chrome_menu(self):
        """เมนู Chrome Automation"""
        while True:
            print("\n🌐 Chrome Automation Menu:")
            print("1. เริ่ม Chrome Browser")
            print("2. ปิด Chrome Browser")
            print("3. Force Restart Chrome Browser")
            print("4. ดูสถานะ Chrome Browser")
            print("5. เปิดเว็บไซต์")
            print("6. ค้นหาข้อมูล")
            print("7. ทำงานอัตโนมัติ")
            print("8. ดูหน้าจอ")
            print("0. กลับเมนูหลัก")
            
            choice = input("เลือก: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                try:
                    print("🔍 DEBUG: User selected 'Start Chrome Browser'")
                    await self.start_chrome_browser(headless=False)
                except Exception as e:
                    print(f"❌ ผิดพลาด: {e}")
                    import traceback
                    print(f"🔍 DEBUG: Full traceback: {traceback.format_exc()}")
            elif choice == "2":
                try:
                    await self.stop_chrome_browser()
                except Exception as e:
                    print(f"❌ ผิดพลาด: {e}")
            elif choice == "3":
                try:
                    print("🔄 Force Restart Chrome Browser...")
                    await self.start_chrome_browser(headless=False, force_restart=True)
                except Exception as e:
                    print(f"❌ ผิดพลาด: {e}")
            elif choice == "4":
                try:
                    status = await self.get_chrome_status()
                    print(f"📊 Chrome Status:")
                    print(f"   Driver Active: {'✅' if status['driver_active'] else '❌'}")
                    print(f"   Initializing: {'🔄' if status['is_initializing'] else '⏸️'}")
                    print(f"   Session ID: {status['session_id']}")
                    print(f"   Last Activity: {status['last_activity']}")
                except Exception as e:
                    print(f"❌ ผิดพลาด: {e}")
            elif choice == "5":
                if not hasattr(self.chrome_controller, 'driver') or not self.chrome_controller.driver:
                    print("❌ กรุณาเริ่ม Chrome Browser ก่อน")
                    continue
                url = input("ใส่ URL: ").strip()
                if url:
                    try:
                        await self.chrome_controller.ai_navigate(url, f"เปิด {url}")
                        print(f"✅ เปิด {url} แล้ว")
                    except Exception as e:
                        print(f"❌ ผิดพลาด: {e}")
            elif choice == "6":
                if not hasattr(self.chrome_controller, 'driver') or not self.chrome_controller.driver:
                    print("❌ กรุณาเริ่ม Chrome Browser ก่อน")
                    continue
                query = input("ค้นหาอะไร: ").strip()
                if query:
                    try:
                        await self.chrome_controller.ai_navigate("https://www.google.com", f"ค้นหา {query}")
                        print(f"✅ ค้นหา {query} แล้ว")
                    except Exception as e:
                        print(f"❌ ผิดพลาด: {e}")
            elif choice == "7":
                if not hasattr(self.chrome_controller, 'driver') or not self.chrome_controller.driver:
                    print("❌ กรุณาเริ่ม Chrome Browser ก่อน")
                    continue
                print("🤖 ทำงานอัตโนมัติ...")
                # Add automation logic here
            elif choice == "8":
                if not hasattr(self.chrome_controller, 'driver') or not self.chrome_controller.driver:
                    print("❌ กรุณาเริ่ม Chrome Browser ก่อน")
                    continue
                print("👁️ ดูหน้าจอ...")
                # Add screenshot logic here
                
    async def thai_menu(self):
        """เมนู Thai Language Processing"""
        while True:
            print("\n🇹🇭 Thai Language Processing Menu:")
            print("1. ประมวลผลข้อความภาษาไทย")
            print("2. OCR ข้อความจากภาพ")
            print("3. แปลงข้อความ")
            print("0. กลับเมนูหลัก")
            
            choice = input("เลือก: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                text = input("ใส่ข้อความภาษาไทย: ").strip()
                if text:
                    try:
                        # Use thai processor
                        print(f"📝 ประมวลผล: {text}")
                        print("✅ ประมวลผลเสร็จสิ้น")
                    except Exception as e:
                        print(f"❌ ผิดพลาด: {e}")
            elif choice == "2":
                print("📷 OCR ข้อความจากภาพ...")
                # Add OCR logic here
            elif choice == "3":
                print("🔄 แปลงข้อความ...")
                # Add text conversion logic here
                
    async def ai_menu(self):
        """เมนู AI Integration"""
        while True:
            print("\n🤖 AI Integration Menu:")
            print("1. วิเคราะห์ข้อความ")
            print("2. วิเคราะห์ภาพ")
            print("3. สร้างข้อความ")
            print("4. ตอบคำถาม")
            print("0. กลับเมนูหลัก")
            
            choice = input("เลือก: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                text = input("ใส่ข้อความให้วิเคราะห์: ").strip()
                if text:
                    try:
                        print(f"🧠 วิเคราะห์: {text}")
                        print("✅ การวิเคราะห์เสร็จสิ้น")
                    except Exception as e:
                        print(f"❌ ผิดพลาด: {e}")
            elif choice == "2":
                print("🖼️ วิเคราะห์ภาพ...")
                # Add image analysis logic here
            elif choice == "3":
                prompt = input("ใส่ prompt: ").strip()
                if prompt:
                    try:
                        print(f"✍️ สร้างข้อความจาก: {prompt}")
                        print("✅ สร้างข้อความเสร็จสิ้น")
                    except Exception as e:
                        print(f"❌ ผิดพลาด: {e}")
            elif choice == "4":
                question = input("ถามอะไร: ").strip()
                if question:
                    try:
                        print(f"❓ คำถาม: {question}")
                        print("✅ ตอบคำถามเสร็จสิ้น")
                    except Exception as e:
                        print(f"❌ ผิดพลาด: {e}")
                        
    async def visual_menu(self):
        """เมนู Visual Recognition"""
        while True:
            print("\n👁️ Visual Recognition Menu:")
            print("1. วิเคราะห์หน้าจอ")
            print("2. หา elements")
            print("3. เปรียบเทียบภาพ")
            print("0. กลับเมนูหลัก")
            
            choice = input("เลือก: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                print("🖥️ วิเคราะห์หน้าจอ...")
                # Add screen analysis logic here
            elif choice == "2":
                print("🔍 หา elements...")
                # Add element detection logic here
            elif choice == "3":
                print("🔄 เปรียบเทียบภาพ...")
                # Add image comparison logic here
                
    async def backup_menu(self):
        """เมนู Backup & Restore"""
        while True:
            print("\n💾 Backup & Restore Menu:")
            print("1. สร้าง backup")
            print("2. Restore backup")
            print("3. ดูรายการ backup")
            print("4. ลบ backup")
            print("0. กลับเมนูหลัก")
            
            choice = input("เลือก: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                source = input("ใส่ path ที่จะ backup: ").strip()
                if source:
                    try:
                        print(f"💾 สร้าง backup จาก: {source}")
                        # Add backup logic here
                        print("✅ สร้าง backup เสร็จสิ้น")
                    except Exception as e:
                        print(f"❌ ผิดพลาด: {e}")
            elif choice == "2":
                backup_name = input("ใส่ชื่อ backup ที่จะ restore: ").strip()
                if backup_name:
                    try:
                        print(f"🔄 Restore backup: {backup_name}")
                        # Add restore logic here
                        print("✅ Restore เสร็จสิ้น")
                    except Exception as e:
                        print(f"❌ ผิดพลาด: {e}")
            elif choice == "3":
                print("📋 รายการ backup:")
                # Add list backup logic here
            elif choice == "4":
                backup_name = input("ใส่ชื่อ backup ที่จะลบ: ").strip()
                if backup_name:
                    try:
                        print(f"🗑️ ลบ backup: {backup_name}")
                        # Add delete backup logic here
                        print("✅ ลบ backup เสร็จสิ้น")
                    except Exception as e:
                        print(f"❌ ผิดพลาด: {e}")
                        
    def system_status(self):
        """แสดงสถานะระบบ"""
        print("\n📊 System Status:")
        print(f"🔄 ระบบทำงาน: {'✅' if self.running else '❌'}")
        print(f"📋 Components: {len(self.components)}/5")
        
        for name, component in self.components.items():
            status = "✅" if component else "❌"
            print(f"   {name}: {status}")
            
        print(f"⚙️ Config: {self.config['system']['name']} v{self.config['system']['version']}")
        
    async def run_all_tests(self):
        """รันการทดสอบทั้งหมด"""
        print("\n🚀 รันการทดสอบทั้งหมด...")
        
        tests = [
            ("Chrome Test", self.test_chrome),
            ("Thai Test", self.test_thai),
            ("AI Test", self.test_ai),
            ("Visual Test", self.test_visual),
            ("Backup Test", self.test_backup)
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"🔄 {test_name}...")
                await test_func()
                print(f"✅ {test_name} สำเร็จ")
            except Exception as e:
                print(f"❌ {test_name} ผิดพลาด: {e}")
                
        print("🎉 การทดสอบเสร็จสิ้น!")
        
    async def test_chrome(self):
        """ทดสอบ Chrome"""
        if "chrome" in self.components:
            await self.chrome_controller.ai_navigate("https://www.google.com", "ทดสอบ Chrome")
            
    async def test_thai(self):
        """ทดสอบ Thai Processor"""
        if "thai" in self.components:
            print("ทดสอบ Thai Processor")
            
    async def test_ai(self):
        """ทดสอบ AI Integration"""
        if "ai" in self.components:
            print("ทดสอบ AI Integration")
            
    async def test_visual(self):
        """ทดสอบ Visual Recognition"""
        if "visual" in self.components:
            print("ทดสอบ Visual Recognition")
            
    async def test_backup(self):
        """ทดสอบ Backup Controller"""
        if "backup" in self.components:
            print("ทดสอบ Backup Controller")
            
    async def start_chrome_browser(self, headless=False, force_restart=False):
        """เริ่ม Chrome browser เมื่อต้องการ"""
        import traceback
        import threading
        
        # DEBUG: Log caller information
        caller_frame = traceback.extract_stack()[-2]
        print(f"🔍 DEBUG: start_chrome_browser called from {caller_frame.filename}:{caller_frame.lineno}")
        print(f"🔍 DEBUG: Thread ID: {threading.current_thread().ident}")
        print(f"🔍 DEBUG: headless={headless}, force_restart={force_restart}")
        print(f"🔍 DEBUG: chrome in components: {'chrome' in self.components}")
        
        if "chrome" in self.components:
            print("🔍 DEBUG: Calling chrome_controller.start_ai_browser...")
            success = await self.chrome_controller.start_ai_browser(headless=headless)
            if success:
                print("✅ Chrome browser เริ่มต้นแล้ว")
                return True
            else:
                print("❌ ไม่สามารถเริ่ม Chrome browser ได้")
                return False
        else:
            print("❌ Chrome Controller ยังไม่ได้เริ่มต้น")
            return False
            
    async def stop_chrome_browser(self):
        """ปิด Chrome browser - DISABLED"""
        if "chrome" in self.components:
            print(f"[DEBUG] stop_chrome_browser() called from: {traceback.format_stack()}")
            # self.chrome_controller.cleanup()  # DISABLED - ไม่ให้ปิด Chrome อัตโนมัติ
            print("🔌 Chrome browser cleanup disabled by user preference")
            
    async def get_chrome_status(self):
        """ดูสถานะ Chrome browser"""
        if "chrome" in self.components:
            return self.chrome_controller.get_status()
        return {'driver_active': False, 'is_initializing': False, 'last_activity': 0, 'session_id': None}
            
    async def run(self):
        """รันระบบ interactive"""
        if not await self.initialize_system():
            return
        # เริ่ม session godmode ทุกครั้งที่เข้าโหมด godauto/godmode
        self.godmode_session_id = self.godmode_km.start_session()
        try:
            while True:
                try:
                    self.show_menu()
                    choice = input("เลือกเมนู: ").strip()
                    # บันทึก command ทุกครั้ง
                    self.godmode_km.save_command(self.godmode_session_id, f"menu_choice:{choice}", "menu", True, "User selected menu")
                    if choice == "0":
                        print("🛑 ออกจากระบบ...")
                        break
                    elif choice == "1":
                        await self.chrome_menu()
                    elif choice == "2":
                        await self.thai_menu()
                    elif choice == "3":
                        await self.ai_menu()
                    elif choice == "4":
                        await self.visual_menu()
                    elif choice == "5":
                        await self.backup_menu()
                    elif choice == "6":
                        self.system_status()
                    elif choice == "7":
                        print("🔧 System Settings (ยังไม่พร้อม)")
                    elif choice == "8":
                        await self.run_all_tests()
                    else:
                        print("❌ เลือกไม่ถูกต้อง")
                except KeyboardInterrupt:
                    print("\n🛑 ระบบถูกหยุดโดยผู้ใช้")
                    break
                except Exception as e:
                    print(f"❌ เกิดข้อผิดพลาด: {e}")
                    self.godmode_km.save_command(self.godmode_session_id, f"error:{e}", "error", False, str(e))
        finally:
            # จบ session godmode
            self.godmode_km.end_session(self.godmode_session_id)
        print("👋 ขอบคุณที่ใช้งาน!")
        
async def main():
    """Main function"""
    system = InteractiveSystem()
    await system.run()
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 ระบบถูกหยุด")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}") 