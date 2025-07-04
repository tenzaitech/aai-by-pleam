#!/usr/bin/env python3
"""
🎯 WAWAGOD Master Controller - Ultimate AI Automation System
รวมพลังจาก WAWA + Chrome Automation 100%
"""

import asyncio
import logging
import os
import sys
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import WAWAGOD Core Controllers
try:
    from core.wawagod_chrome_controller import WAWAGODChromeController
    from core.wawagod_puppeteer_controller import WAWAGODPuppeteerController
    from core.wawagod_selenium_controller import WAWAGODSeleniumController
    from core.wawagod_thai_processor import WAWAGODThaiProcessor
    from core.wawagod_ai_integration import WAWAGODAIIntegration
    from core.wawagod_visual_recognition import WAWAGODVisualRecognition
    from core.wawagod_ocr_processor import WAWAGODOCRProcessor
    from core.wawagod_input_controller import WAWAGODInputController
    from core.wawagod_backup_controller import WAWAGODBackupController
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("🔄 Creating core controllers...")

class WAWAGODMaster:
    """
    🎯 WAWAGOD Master Controller - ตัวควบคุมหลักของระบบ WAWAGOD
    รวมพลังจาก WAWA + Chrome Automation 100%
    """
    
    def __init__(self):
        """เริ่มต้น WAWAGOD Master Controller"""
        self.logger = self._setup_logger()
        self.logger.info("🎯 WAWAGOD Master Controller เริ่มต้น")
        
        # Controllers
        self.chrome_controller = None
        self.puppeteer_controller = None
        self.selenium_controller = None
        self.thai_processor = None
        self.ai_integration = None
        self.visual_recognition = None
        self.ocr_processor = None
        self.input_controller = None
        self.backup_controller = None
        
        # System Status
        self.system_initialized = False
        self.browser_session_active = False
        self.current_browser_type = None
        
        # Configuration
        self.config = {
            'browser_type': 'puppeteer',  # puppeteer, selenium, hybrid
            'headless': False,
            'thai_language': True,
            'ai_enabled': True,
            'auto_backup': True,
            'debug_mode': True
        }
        
        self.logger.info("✅ WAWAGOD Master Controller พร้อมใช้งาน")

    def _setup_logger(self):
        """ตั้งค่า Logger"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('wawagod.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('WAWAGOD')

    async def initialize_system(self):
        """เริ่มต้นระบบ WAWAGOD ทั้งหมด"""
        try:
            self.logger.info("🚀 เริ่มต้นระบบ WAWAGOD...")
            
            # สร้าง Controllers แบบ Parallel
            await self._create_controllers_parallel()
            
            # เริ่มต้น Controllers
            await self._initialize_controllers()
            
            self.system_initialized = True
            self.logger.info("✅ ระบบ WAWAGOD เริ่มต้นสำเร็จ")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการเริ่มต้นระบบ: {e}")
            self.logger.error(traceback.format_exc())
            return False

    async def _create_controllers_parallel(self):
        """สร้าง Controllers แบบ Parallel"""
        self.logger.info("🔧 สร้าง Controllers แบบ Parallel...")
        
        # สร้าง Controllers พร้อมกัน
        tasks = [
            self._create_chrome_controller(),
            self._create_puppeteer_controller(),
            self._create_selenium_controller(),
            self._create_thai_processor(),
            self._create_ai_integration(),
            self._create_visual_recognition(),
            self._create_ocr_processor(),
            self._create_input_controller(),
            self._create_backup_controller()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        self.logger.info("✅ สร้าง Controllers เสร็จสิ้น")

    async def _create_chrome_controller(self):
        """สร้าง Chrome Controller"""
        try:
            from core.wawagod_chrome_controller import WAWAGODChromeController
            self.chrome_controller = WAWAGODChromeController()
            self.logger.info("✅ Chrome Controller สร้างสำเร็จ")
        except Exception as e:
            self.logger.warning(f"⚠️ Chrome Controller: {e}")

    async def _create_puppeteer_controller(self):
        """สร้าง Puppeteer Controller"""
        try:
            from core.wawagod_puppeteer_controller import WAWAGODPuppeteerController
            self.puppeteer_controller = WAWAGODPuppeteerController()
            self.logger.info("✅ Puppeteer Controller สร้างสำเร็จ")
        except Exception as e:
            self.logger.warning(f"⚠️ Puppeteer Controller: {e}")

    async def _create_selenium_controller(self):
        """สร้าง Selenium Controller"""
        try:
            from core.wawagod_selenium_controller import WAWAGODSeleniumController
            self.selenium_controller = WAWAGODSeleniumController()
            self.logger.info("✅ Selenium Controller สร้างสำเร็จ")
        except Exception as e:
            self.logger.warning(f"⚠️ Selenium Controller: {e}")

    async def _create_thai_processor(self):
        """สร้าง Thai Language Processor"""
        try:
            from core.wawagod_thai_processor import WAWAGODThaiProcessor
            self.thai_processor = WAWAGODThaiProcessor()
            self.logger.info("✅ Thai Language Processor สร้างสำเร็จ")
        except Exception as e:
            self.logger.warning(f"⚠️ Thai Language Processor: {e}")

    async def _create_ai_integration(self):
        """สร้าง AI Integration"""
        try:
            from core.wawagod_ai_integration import WAWAGODAIIntegration
            self.ai_integration = WAWAGODAIIntegration()
            self.logger.info("✅ AI Integration สร้างสำเร็จ")
        except Exception as e:
            self.logger.warning(f"⚠️ AI Integration: {e}")

    async def _create_visual_recognition(self):
        """สร้าง Visual Recognition"""
        try:
            from core.wawagod_visual_recognition import WAWAGODVisualRecognition
            self.visual_recognition = WAWAGODVisualRecognition()
            self.logger.info("✅ Visual Recognition สร้างสำเร็จ")
        except Exception as e:
            self.logger.warning(f"⚠️ Visual Recognition: {e}")

    async def _create_ocr_processor(self):
        """สร้าง OCR Processor"""
        try:
            from core.wawagod_ocr_processor import WAWAGODOCRProcessor
            self.ocr_processor = WAWAGODOCRProcessor()
            self.logger.info("✅ OCR Processor สร้างสำเร็จ")
        except Exception as e:
            self.logger.warning(f"⚠️ OCR Processor: {e}")

    async def _create_input_controller(self):
        """สร้าง Input Controller"""
        try:
            from core.wawagod_input_controller import WAWAGODInputController
            self.input_controller = WAWAGODInputController()
            self.logger.info("✅ Input Controller สร้างสำเร็จ")
        except Exception as e:
            self.logger.warning(f"⚠️ Input Controller: {e}")

    async def _create_backup_controller(self):
        """สร้าง Backup Controller"""
        try:
            from core.wawagod_backup_controller import WAWAGODBackupController
            self.backup_controller = WAWAGODBackupController()
            self.logger.info("✅ Backup Controller สร้างสำเร็จ")
        except Exception as e:
            self.logger.warning(f"⚠️ Backup Controller: {e}")

    async def _initialize_controllers(self):
        """เริ่มต้น Controllers ทั้งหมด"""
        self.logger.info("🔧 เริ่มต้น Controllers...")
        
        # เริ่มต้น Controllers ที่สำคัญ
        if self.thai_processor:
            await self.thai_processor.initialize()
        
        if self.ai_integration:
            await self.ai_integration.initialize()
        
        if self.visual_recognition:
            await self.visual_recognition.initialize()
        
        if self.ocr_processor:
            await self.ocr_processor.initialize()
        
        if self.backup_controller:
            await self.backup_controller.initialize()
        
        self.logger.info("✅ เริ่มต้น Controllers เสร็จสิ้น")

    async def start_browser_session(self, browser_type: str = 'puppeteer', headless: bool = False):
        """เริ่มต้น Browser Session"""
        try:
            self.logger.info(f"🌐 เริ่มต้น Browser Session: {browser_type}")
            
            if browser_type == 'puppeteer' and self.puppeteer_controller:
                await self.puppeteer_controller.start_browser(headless=headless)
                self.current_browser_type = 'puppeteer'
                self.browser_session_active = True
                
            elif browser_type == 'selenium' and self.selenium_controller:
                await self.selenium_controller.start_browser(headless=headless)
                self.current_browser_type = 'selenium'
                self.browser_session_active = True
                
            elif browser_type == 'chrome' and self.chrome_controller:
                await self.chrome_controller.start_browser(headless=headless)
                self.current_browser_type = 'chrome'
                self.browser_session_active = True
                
            else:
                raise Exception(f"Browser type {browser_type} ไม่รองรับ")
            
            self.logger.info(f"✅ Browser Session เริ่มต้นสำเร็จ: {browser_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการเริ่มต้น Browser: {e}")
            return False

    async def navigate_to_url(self, url: str):
        """นำทางไปยัง URL"""
        try:
            self.logger.info(f"🌐 นำทางไปยัง: {url}")
            
            if self.current_browser_type == 'puppeteer' and self.puppeteer_controller:
                await self.puppeteer_controller.navigate_to(url)
            elif self.current_browser_type == 'selenium' and self.selenium_controller:
                await self.selenium_controller.navigate_to(url)
            elif self.current_browser_type == 'chrome' and self.chrome_controller:
                await self.chrome_controller.navigate_to(url)
            else:
                raise Exception("ไม่มี Browser Session ที่ใช้งานได้")
            
            self.logger.info(f"✅ นำทางสำเร็จ: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการนำทาง: {e}")
            return False

    async def smart_click(self, element_description: str):
        """Smart Click ด้วย AI"""
        try:
            self.logger.info(f"🎯 Smart Click: {element_description}")
            
            # ใช้ AI วิเคราะห์และหา element
            if self.ai_integration:
                element_info = await self.ai_integration.analyze_element(element_description)
                
                # คลิก element
                if self.current_browser_type == 'puppeteer' and self.puppeteer_controller:
                    await self.puppeteer_controller.click_element(element_info)
                elif self.current_browser_type == 'selenium' and self.selenium_controller:
                    await self.selenium_controller.click_element(element_info)
                elif self.current_browser_type == 'chrome' and self.chrome_controller:
                    await self.chrome_controller.click_element(element_info)
            
            self.logger.info(f"✅ Smart Click สำเร็จ: {element_description}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดใน Smart Click: {e}")
            return False

    async def automated_form_filling(self, form_data: Dict[str, str]):
        """กรอกฟอร์มอัตโนมัติ"""
        try:
            self.logger.info(f"📝 กรอกฟอร์มอัตโนมัติ: {len(form_data)} fields")
            
            for field_name, value in form_data.items():
                if self.current_browser_type == 'puppeteer' and self.puppeteer_controller:
                    await self.puppeteer_controller.fill_field(field_name, value)
                elif self.current_browser_type == 'selenium' and self.selenium_controller:
                    await self.selenium_controller.fill_field(field_name, value)
                elif self.current_browser_type == 'chrome' and self.chrome_controller:
                    await self.chrome_controller.fill_field(field_name, value)
            
            self.logger.info("✅ กรอกฟอร์มอัตโนมัติสำเร็จ")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการกรอกฟอร์ม: {e}")
            return False

    async def comprehensive_screenshot_analysis(self):
        """วิเคราะห์หน้าจอแบบครบถ้วน"""
        try:
            self.logger.info("🔍 วิเคราะห์หน้าจอแบบครบถ้วน...")
            
            # ถ่าย screenshot
            screenshot_path = await self._take_screenshot()
            
            # วิเคราะห์ด้วย AI
            if self.ai_integration:
                ai_analysis = await self.ai_integration.analyze_screenshot(screenshot_path)
            
            # OCR ข้อความ
            if self.ocr_processor:
                ocr_texts = await self.ocr_processor.extract_text(screenshot_path)
            
            # วิเคราะห์ภาษาไทย
            if self.thai_processor:
                thai_analysis = await self.thai_processor.analyze_text(ocr_texts)
            
            analysis_result = {
                'screenshot_path': screenshot_path,
                'ai_analysis': ai_analysis if 'ai_analysis' in locals() else None,
                'ocr_texts': ocr_texts if 'ocr_texts' in locals() else None,
                'thai_analysis': thai_analysis if 'thai_analysis' in locals() else None,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("✅ วิเคราะห์หน้าจอเสร็จสิ้น")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการวิเคราะห์หน้าจอ: {e}")
            return None

    async def process_thai_command(self, command: str):
        """ประมวลผลคำสั่งภาษาไทย"""
        try:
            self.logger.info(f"🇹🇭 ประมวลผลคำสั่งไทย: {command}")
            
            if self.thai_processor:
                # แปลคำสั่งไทยเป็นอังกฤษ
                english_command = await self.thai_processor.translate_command(command)
                
                # ประมวลผลคำสั่ง
                result = await self._execute_command(english_command)
                
                self.logger.info(f"✅ ประมวลผลคำสั่งไทยสำเร็จ: {command}")
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการประมวลผลคำสั่งไทย: {e}")
            return None

    async def ocr_thai_text(self, image_path: str):
        """OCR ข้อความไทย"""
        try:
            self.logger.info(f"🇹🇭 OCR ข้อความไทย: {image_path}")
            
            if self.ocr_processor:
                thai_texts = await self.ocr_processor.extract_thai_text(image_path)
                self.logger.info(f"✅ OCR ข้อความไทยสำเร็จ: {len(thai_texts)} texts")
                return thai_texts
            
            return []
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดใน OCR ข้อความไทย: {e}")
            return []

    async def analyze_thai_screenshot(self, screenshot_path: str):
        """วิเคราะห์หน้าจอภาษาไทย"""
        try:
            self.logger.info(f"🇹🇭 วิเคราะห์หน้าจอภาษาไทย: {screenshot_path}")
            
            # OCR ข้อความไทย
            thai_texts = await self.ocr_thai_text(screenshot_path)
            
            # วิเคราะห์ด้วย AI
            if self.ai_integration:
                ai_analysis = await self.ai_integration.analyze_thai_screenshot(screenshot_path, thai_texts)
            
            # วิเคราะห์ภาษาไทย
            if self.thai_processor:
                thai_analysis = await self.thai_processor.analyze_screenshot_content(thai_texts)
            
            analysis_result = {
                'screenshot_path': screenshot_path,
                'thai_texts': thai_texts,
                'ai_analysis': ai_analysis if 'ai_analysis' in locals() else None,
                'thai_analysis': thai_analysis if 'thai_analysis' in locals() else None,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("✅ วิเคราะห์หน้าจอภาษาไทยเสร็จสิ้น")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการวิเคราะห์หน้าจอภาษาไทย: {e}")
            return None

    async def _take_screenshot(self):
        """ถ่าย screenshot"""
        try:
            screenshot_path = f"screenshots/wawagod_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            if self.current_browser_type == 'puppeteer' and self.puppeteer_controller:
                await self.puppeteer_controller.take_screenshot(screenshot_path)
            elif self.current_browser_type == 'selenium' and self.selenium_controller:
                await self.selenium_controller.take_screenshot(screenshot_path)
            elif self.current_browser_type == 'chrome' and self.chrome_controller:
                await self.chrome_controller.take_screenshot(screenshot_path)
            
            return screenshot_path
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการถ่าย screenshot: {e}")
            return None

    async def _execute_command(self, command: str):
        """ประมวลผลคำสั่ง"""
        try:
            self.logger.info(f"⚡ ประมวลผลคำสั่ง: {command}")
            
            # แยกคำสั่งและประมวลผล
            if "navigate" in command.lower():
                # คำสั่งนำทาง
                url = command.split()[-1]
                return await self.navigate_to_url(url)
            
            elif "click" in command.lower():
                # คำสั่งคลิก
                element = command.split("click")[-1].strip()
                return await self.smart_click(element)
            
            elif "fill" in command.lower():
                # คำสั่งกรอกฟอร์ม
                # ต้องมี form_data
                return True
            
            else:
                self.logger.warning(f"⚠️ คำสั่งไม่รู้จัก: {command}")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการประมวลผลคำสั่ง: {e}")
            return False

    async def stop_browser_session(self):
        """หยุด Browser Session"""
        try:
            self.logger.info("🔌 หยุด Browser Session...")
            
            if self.current_browser_type == 'puppeteer' and self.puppeteer_controller:
                await self.puppeteer_controller.stop_browser()
            elif self.current_browser_type == 'selenium' and self.selenium_controller:
                await self.selenium_controller.stop_browser()
            elif self.current_browser_type == 'chrome' and self.chrome_controller:
                await self.chrome_controller.stop_browser()
            
            self.browser_session_active = False
            self.current_browser_type = None
            
            self.logger.info("✅ หยุด Browser Session สำเร็จ")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการหยุด Browser: {e}")
            return False

    async def cleanup(self):
        """ทำความสะอาดระบบ"""
        try:
            self.logger.info("🧹 ทำความสะอาดระบบ WAWAGOD...")
            
            # หยุด Browser Session
            if self.browser_session_active:
                await self.stop_browser_session()
            
            # ทำความสะอาด Controllers
            if self.backup_controller:
                await self.backup_controller.cleanup()
            
            self.system_initialized = False
            self.logger.info("✅ ทำความสะอาดระบบเสร็จสิ้น")
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการทำความสะอาด: {e}")

    def get_system_status(self):
        """รับสถานะระบบ"""
        return {
            'system_initialized': self.system_initialized,
            'browser_session_active': self.browser_session_active,
            'current_browser_type': self.current_browser_type,
            'controllers': {
                'chrome_controller': self.chrome_controller is not None,
                'puppeteer_controller': self.puppeteer_controller is not None,
                'selenium_controller': self.selenium_controller is not None,
                'thai_processor': self.thai_processor is not None,
                'ai_integration': self.ai_integration is not None,
                'visual_recognition': self.visual_recognition is not None,
                'ocr_processor': self.ocr_processor is not None,
                'input_controller': self.input_controller is not None,
                'backup_controller': self.backup_controller is not None
            },
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }

# Test Function
async def test_wawagod():
    """ทดสอบ WAWAGOD Master Controller"""
    print("🧪 ทดสอบ WAWAGOD Master Controller...")
    
    wawagod = WAWAGODMaster()
    
    # เริ่มต้นระบบ
    success = await wawagod.initialize_system()
    if not success:
        print("❌ เริ่มต้นระบบล้มเหลว")
        return
    
    # แสดงสถานะระบบ
    status = wawagod.get_system_status()
    print(f"📊 สถานะระบบ: {status}")
    
    # ทดสอบ Browser Session
    success = await wawagod.start_browser_session('puppeteer', headless=True)
    if success:
        print("✅ Browser Session สำเร็จ")
        
        # ทดสอบการนำทาง
        await wawagod.navigate_to_url("https://www.google.com")
        
        # หยุด Browser
        await wawagod.stop_browser_session()
    else:
        print("❌ Browser Session ล้มเหลว")
    
    # ทำความสะอาด
    await wawagod.cleanup()
    print("✅ ทดสอบเสร็จสิ้น")

if __name__ == "__main__":
    asyncio.run(test_wawagod()) 