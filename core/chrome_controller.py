#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-Powered Chrome Controller
ควบคุม Chrome ด้วย AI
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import openai
import cv2
import numpy as np
from PIL import Image
import io
import atexit
import logging
import threading
import time
import subprocess

class AIChromeController:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AIChromeController, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, openai_api_key=""):
        if self._initialized:
            if hasattr(self, 'logger'):
                self.logger.info("[SINGLETON] Reuse existing AIChromeController instance.")
            return
        self.logger = logging.getLogger(__name__)
        self.logger.info("[SINGLETON] Create new AIChromeController instance.")
        self.driver = None
        self.openai_client = None
        self._lock = threading.Lock()
        self._is_initializing = False
        self._last_activity = time.time()
        if openai_api_key:
            try:
                self.openai_client = openai
                self.openai_client.api_key = openai_api_key
            except Exception as e:
                self.logger.warning(f"OpenAI init error: {e}")
        atexit.register(self.cleanup)
        self._initialized = True
        
        # เริ่ม auto cleanup thread
        self.start_auto_cleanup_thread()
        
    def auto_cleanup_chrome_process(self):
        """Kill all chrome.exe processes (Windows only)"""
        try:
            subprocess.call(['taskkill', '/F', '/IM', 'chrome.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.logger.info("[AUTO CLEANUP] Killed all chrome.exe processes.")
        except Exception as e:
            self.logger.warning(f"[AUTO CLEANUP] Failed to kill chrome.exe: {e}")

    async def start_ai_browser(self, headless=True):
        """เริ่มต้น AI browser"""
        import traceback
        import threading
        
        # DEBUG: Log caller information
        caller_frame = traceback.extract_stack()[-2]
        self.logger.info(f"🔍 DEBUG: start_ai_browser called from {caller_frame.filename}:{caller_frame.lineno}")
        self.logger.info(f"🔍 DEBUG: Thread ID: {threading.current_thread().ident}")
        self.logger.info(f"🔍 DEBUG: headless={headless}")
        
        self.logger.info("[BROWSER] start_ai_browser called.")
        
        # Auto cleanup chrome.exe ก่อนเริ่ม
        self.auto_cleanup_chrome_process()
        
        # ตรวจสอบว่า driver กำลังทำงานอยู่หรือไม่
        if self.driver:
            try:
                # ทดสอบว่า driver ยังทำงานอยู่หรือไม่
                self.driver.current_url
                self.logger.info("🔍 DEBUG: Existing driver is still working, reusing...")
                return True
            except Exception:
                self.logger.info("🔍 DEBUG: Existing driver is dead, cleaning up...")
                self.driver = None
        
        # ป้องกันการสร้าง driver ซ้ำ
        if self._is_initializing:
            self.logger.info("🔍 DEBUG: Already initializing, skipping...")
            return False
        
        self._is_initializing = True
        
        try:
            # สร้าง Chrome options
            self.logger.info("🔍 DEBUG: Creating Chrome options...")
            options = Options()
            
            if headless:
                self.logger.info("🔍 DEBUG: Headless mode enabled")
                options.add_argument("--headless")
            
            # เพิ่ม options เพื่อป้องกันการเปิด Chrome ซ้ำ
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--remote-debugging-port=0")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-ipc-flooding-protection")
            # เพิ่ม options เพื่อป้องกันการเปิด Chrome ซ้ำ
            options.add_argument("--single-process")
            options.add_argument("--no-zygote")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-translate")
            options.add_argument("--hide-scrollbars")
            options.add_argument("--mute-audio")
            options.add_argument("--no-first-run")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--disable-component-update")
            options.add_argument("--disable-domain-reliability")
            options.add_argument("--disable-features=AudioServiceOutOfProcess")
            options.add_argument("--disable-hang-monitor")
            options.add_argument("--disable-prompt-on-repost")
            options.add_argument("--disable-web-resources")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-features=BlinkGenPropertyTrees")
            options.add_argument("--disable-features=CalculateNativeWinOcclusion")
            options.add_argument("--disable-features=GlobalMediaControls")
            options.add_argument("--disable-features=MediaRouter")
            options.add_argument("--disable-features=OptimizationHints")
            options.add_argument("--disable-features=PasswordGeneration")
            options.add_argument("--disable-features=PreloadMediaEngagementData")
            options.add_argument("--disable-features=Translate")
            options.add_argument("--disable-features=WebUIDarkMode")
            options.add_argument("--disable-features=WebUIDarkModeV2")
            options.add_argument("--disable-features=WebUIDarkModeV3")
            options.add_argument("--disable-features=WebUIDarkModeV4")
            options.add_argument("--disable-features=WebUIDarkModeV5")
            options.add_argument("--disable-features=WebUIDarkModeV6")
            options.add_argument("--disable-features=WebUIDarkModeV7")
            options.add_argument("--disable-features=WebUIDarkModeV8")
            options.add_argument("--disable-features=WebUIDarkModeV9")
            options.add_argument("--disable-features=WebUIDarkModeV10")
            
            # สร้าง Chrome driver
            self.logger.info("🔍 DEBUG: Creating Chrome driver...")
            self.driver = webdriver.Chrome(options=options)
            
            self.logger.info("✅ Chrome browser เริ่มต้นสำเร็จ")
            self.logger.info(f"🔍 DEBUG: Driver session ID: {self.driver.session_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถเริ่ม Chrome browser: {e}")
            self.driver = None
            return False
        finally:
            self._is_initializing = False
        
    async def ai_navigate(self, url, instruction=""):
        """นำทางด้วย AI"""
        if not self.driver:
            self.logger.warning("❌ Chrome ยังไม่ได้เริ่มต้น")
            return False
        try:
            self.driver.get(url)
            self.logger.info(f"✅ เปิด URL: {url}")
            return True
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถเปิด URL ได้: {e}")
            return False
        
    async def ai_click(self, natural_description):
        """คลิกด้วย AI"""
        if not self.driver:
            self.logger.warning("❌ Chrome ยังไม่ได้เริ่มต้น")
            return False
        try:
            # ใช้ AI หา element จากคำอธิบายธรรมชาติ
            screenshot = self.driver.get_screenshot_as_png()
            element_info = await self.find_element_with_ai(screenshot, natural_description)
            if element_info:
                # คลิกตามที่ AI บอก
                x, y = element_info['coordinates']
                self.driver.execute_script(f"document.elementFromPoint({x}, {y}).click()")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ ไม่สามารถคลิกได้: {e}")
            return False
        
    async def analyze_screenshot_with_ai(self, screenshot, instruction):
        """วิเคราะห์ screenshot ด้วย AI"""
        if not self.openai_client:
            self.logger.warning("❌ OpenAI client ไม่พร้อมใช้งาน")
            return None
        # ส่ง screenshot ไปให้ AI วิเคราะห์
        pass
        
    async def find_element_with_ai(self, screenshot, description):
        """หา element ด้วย AI"""
        if not self.openai_client:
            self.logger.warning("❌ OpenAI client ไม่พร้อมใช้งาน")
            return None
        # ใช้ AI หา element จากคำอธิบาย
        pass
        
    def cleanup(self):
        """ปิด Chrome driver"""
        if hasattr(self, 'logger'):
            self.logger.info("[BROWSER] cleanup called.")
        if self.driver:
            try:
                # ตรวจสอบว่า driver ยังทำงานอยู่หรือไม่
                try:
                    self.driver.current_url
                    self.driver.quit()
                    if hasattr(self, 'logger'):
                        self.logger.info("🔌 ปิด Chrome driver แล้ว")
                except Exception:
                    if hasattr(self, 'logger'):
                        self.logger.info("🔌 Chrome driver ถูกปิดไปแล้ว")
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"❌ ไม่สามารถปิด Chrome driver: {e}")
            finally:
                self.driver = None
            
    def __del__(self):
        """Destructor - ปิด driver เมื่อ object ถูกทำลาย"""
        self.cleanup()
        
    def is_ready(self):
        """ตรวจสอบว่า Chrome Controller พร้อมใช้งานหรือไม่"""
        return self.driver is not None

    def start_auto_cleanup_thread(self):
        """เริ่ม background thread สำหรับ auto cleanup chrome.exe"""
        import threading
        import time
        
        def cleanup_loop():
            while True:
                try:
                    time.sleep(30)  # รอ 30 วินาที
                    self.auto_cleanup_chrome_process()
                except Exception as e:
                    if hasattr(self, 'logger'):
                        self.logger.warning(f"Auto cleanup error: {e}")
                    time.sleep(60)  # รอ 1 นาทีถ้าเกิดข้อผิดพลาด
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        self.logger.info("[AUTO CLEANUP] Background cleanup thread started")
