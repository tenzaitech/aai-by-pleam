#!/usr/bin/env python3
"""
🎯 WAWAGOD Puppeteer Controller - JavaScript Browser Automation
ความเร็วสูง เหมาะสำหรับ automation เร็ว
"""

import asyncio
import logging
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class WAWAGODPuppeteerController:
    """
    🎯 WAWAGOD Puppeteer Controller
    ใช้ Puppeteer สำหรับ browser automation แบบ JavaScript
    """
    
    def __init__(self):
        """เริ่มต้น Puppeteer Controller"""
        self.logger = logging.getLogger('WAWAGOD.Puppeteer')
        self.browser = None
        self.page = None
        self.is_running = False
        
        # Puppeteer Configuration
        self.config = {
            'headless': False,
            'slow_mo': 100,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        }
        
        self.logger.info("✅ WAWAGOD Puppeteer Controller พร้อมใช้งาน")

    async def initialize(self):
        """เริ่มต้น Puppeteer Controller"""
        try:
            self.logger.info("🔧 เริ่มต้น Puppeteer Controller...")
            
            # ตรวจสอบ Node.js และ Puppeteer
            await self._check_dependencies()
            
            self.logger.info("✅ Puppeteer Controller เริ่มต้นสำเร็จ")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการเริ่มต้น Puppeteer: {e}")
            return False

    async def _check_dependencies(self):
        """ตรวจสอบ dependencies"""
        try:
            # ตรวจสอบ Node.js
            import subprocess
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Node.js ไม่ได้ติดตั้ง")
            
            # ตรวจสอบ Puppeteer
            result = subprocess.run(['npm', 'list', 'puppeteer'], capture_output=True, text=True)
            if 'puppeteer' not in result.stdout:
                self.logger.warning("⚠️ Puppeteer ไม่ได้ติดตั้ง จะติดตั้งให้อัตโนมัติ")
                await self._install_puppeteer()
            
            self.logger.info("✅ Dependencies ครบถ้วน")
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการตรวจสอบ dependencies: {e}")
            raise

    async def _install_puppeteer(self):
        """ติดตั้ง Puppeteer"""
        try:
            self.logger.info("📦 ติดตั้ง Puppeteer...")
            
            import subprocess
            result = subprocess.run(['npm', 'install', 'puppeteer'], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("✅ ติดตั้ง Puppeteer สำเร็จ")
            else:
                raise Exception(f"ติดตั้ง Puppeteer ล้มเหลว: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการติดตั้ง Puppeteer: {e}")
            raise

    async def start_browser(self, headless: bool = False):
        """เริ่มต้น Browser"""
        try:
            self.logger.info(f"🌐 เริ่มต้น Puppeteer Browser (headless: {headless})")
            
            # สร้าง JavaScript script สำหรับเริ่มต้น Puppeteer
            script = self._create_puppeteer_script(headless)
            
            # รัน JavaScript script
            await self._run_puppeteer_script(script)
            
            self.is_running = True
            self.logger.info("✅ Puppeteer Browser เริ่มต้นสำเร็จ")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการเริ่มต้น Browser: {e}")
            return False

    def _create_puppeteer_script(self, headless: bool) -> str:
        """สร้าง JavaScript script สำหรับ Puppeteer"""
        script = f"""
const puppeteer = require('puppeteer');

(async () => {{
    try {{
        console.log('🚀 เริ่มต้น Puppeteer Browser...');
        
        const browser = await puppeteer.launch({{
            headless: {str(headless).lower()},
            slowMo: {self.config['slow_mo']},
            args: {json.dumps(self.config['args'])},
            defaultViewport: {{ width: 1920, height: 1080 }}
        }});
        
        const page = await browser.newPage();
        
        // ตั้งค่า User Agent
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        
        // ตั้งค่า Viewport
        await page.setViewport({{ width: 1920, height: 1080 }});
        
        // บันทึก browser และ page instance
        global.wawagod_browser = browser;
        global.wawagod_page = page;
        
        console.log('✅ Puppeteer Browser เริ่มต้นสำเร็จ');
        
        // ส่งข้อมูลกลับไปยัง Python
        process.send({{ type: 'browser_ready', success: true }});
        
    }} catch (error) {{
        console.error('❌ เกิดข้อผิดพลาด:', error);
        process.send({{ type: 'browser_error', error: error.message }});
    }}
}})();
"""
        return script

    async def _run_puppeteer_script(self, script: str):
        """รัน JavaScript script"""
        try:
            import subprocess
            import tempfile
            
            # สร้างไฟล์ JavaScript ชั่วคราว
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(script)
                script_path = f.name
            
            # รัน script
            process = subprocess.Popen(
                ['node', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # รอผลลัพธ์
            stdout, stderr = process.communicate(timeout=30)
            
            if process.returncode == 0:
                self.logger.info("✅ JavaScript script รันสำเร็จ")
                self.logger.debug(f"stdout: {stdout}")
            else:
                raise Exception(f"JavaScript script ล้มเหลว: {stderr}")
            
            # ลบไฟล์ชั่วคราว
            os.unlink(script_path)
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการรัน JavaScript script: {e}")
            raise

    async def navigate_to(self, url: str):
        """นำทางไปยัง URL"""
        try:
            self.logger.info(f"🌐 นำทางไปยัง: {url}")
            
            script = f"""
(async () => {{
    try {{
        if (global.wawagod_page) {{
            await global.wawagod_page.goto('{url}', {{ 
                waitUntil: 'networkidle2',
                timeout: 30000 
            }});
            console.log('✅ นำทางสำเร็จ: {url}');
            process.send({{ type: 'navigation_success', url: '{url}' }});
        }} else {{
            throw new Error('Page ไม่พร้อมใช้งาน');
        }}
    }} catch (error) {{
        console.error('❌ เกิดข้อผิดพลาดในการนำทาง:', error);
        process.send({{ type: 'navigation_error', error: error.message }});
    }}
}})();
"""
            await self._run_puppeteer_script(script)
            self.logger.info(f"✅ นำทางสำเร็จ: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการนำทาง: {e}")
            return False

    async def click_element(self, element_info: Dict[str, Any]):
        """คลิก Element"""
        try:
            self.logger.info(f"🎯 คลิก Element: {element_info}")
            
            # สร้าง selector จาก element_info
            selector = self._create_selector(element_info)
            
            script = f"""
(async () => {{
    try {{
        if (global.wawagod_page) {{
            await global.wawagod_page.waitForSelector('{selector}', {{ timeout: 10000 }});
            await global.wawagod_page.click('{selector}');
            console.log('✅ คลิก Element สำเร็จ: {selector}');
            process.send({{ type: 'click_success', selector: '{selector}' }});
        }} else {{
            throw new Error('Page ไม่พร้อมใช้งาน');
        }}
    }} catch (error) {{
        console.error('❌ เกิดข้อผิดพลาดในการคลิก:', error);
        process.send({{ type: 'click_error', error: error.message }});
    }}
}})();
"""
            await self._run_puppeteer_script(script)
            self.logger.info(f"✅ คลิก Element สำเร็จ: {selector}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการคลิก: {e}")
            return False

    def _create_selector(self, element_info: Dict[str, Any]) -> str:
        """สร้าง CSS selector จาก element_info"""
        if 'id' in element_info:
            return f"#{element_info['id']}"
        elif 'class' in element_info:
            return f".{element_info['class']}"
        elif 'tag' in element_info:
            return element_info['tag']
        elif 'text' in element_info:
            return f"text={element_info['text']}"
        else:
            return "body"  # fallback

    async def fill_field(self, field_name: str, value: str):
        """กรอกข้อมูลในฟิลด์"""
        try:
            self.logger.info(f"📝 กรอกฟิลด์: {field_name} = {value}")
            
            script = f"""
(async () => {{
    try {{
        if (global.wawagod_page) {{
            // หา input field
            const selector = 'input[name="{field_name}"], input[id="{field_name}"], input[placeholder*="{field_name}"]';
            await global.wawagod_page.waitForSelector(selector, {{ timeout: 10000 }});
            
            // ล้างข้อมูลเดิมและกรอกข้อมูลใหม่
            await global.wawagod_page.click(selector);
            await global.wawagod_page.keyboard.down('Control');
            await global.wawagod_page.keyboard.press('KeyA');
            await global.wawagod_page.keyboard.up('Control');
            await global.wawagod_page.type(selector, '{value}');
            
            console.log('✅ กรอกฟิลด์สำเร็จ: {field_name}');
            process.send({{ type: 'fill_success', field: '{field_name}' }});
        }} else {{
            throw new Error('Page ไม่พร้อมใช้งาน');
        }}
    }} catch (error) {{
        console.error('❌ เกิดข้อผิดพลาดในการกรอกฟิลด์:', error);
        process.send({{ type: 'fill_error', error: error.message }});
    }}
}})();
"""
            await self._run_puppeteer_script(script)
            self.logger.info(f"✅ กรอกฟิลด์สำเร็จ: {field_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการกรอกฟิลด์: {e}")
            return False

    async def take_screenshot(self, file_path: str):
        """ถ่าย Screenshot"""
        try:
            self.logger.info(f"📸 ถ่าย Screenshot: {file_path}")
            
            # สร้างโฟลเดอร์ถ้ายังไม่มี
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            script = f"""
(async () => {{
    try {{
        if (global.wawagod_page) {{
            await global.wawagod_page.screenshot({{
                path: '{file_path}',
                fullPage: true
            }});
            console.log('✅ ถ่าย Screenshot สำเร็จ: {file_path}');
            process.send({{ type: 'screenshot_success', path: '{file_path}' }});
        }} else {{
            throw new Error('Page ไม่พร้อมใช้งาน');
        }}
    }} catch (error) {{
        console.error('❌ เกิดข้อผิดพลาดในการถ่าย Screenshot:', error);
        process.send({{ type: 'screenshot_error', error: error.message }});
    }}
}})();
"""
            await self._run_puppeteer_script(script)
            self.logger.info(f"✅ ถ่าย Screenshot สำเร็จ: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการถ่าย Screenshot: {e}")
            return False

    async def get_page_content(self):
        """รับเนื้อหาของหน้าเว็บ"""
        try:
            self.logger.info("📄 รับเนื้อหาของหน้าเว็บ...")
            
            script = """
(async () => {
    try {
        if (global.wawagod_page) {
            const content = await global.wawagod_page.content();
            const title = await global.wawagod_page.title();
            const url = global.wawagod_page.url();
            
            console.log('✅ รับเนื้อหาสำเร็จ');
            process.send({ 
                type: 'content_success', 
                content: content,
                title: title,
                url: url
            });
        } else {
            throw new Error('Page ไม่พร้อมใช้งาน');
        }
    } catch (error) {
        console.error('❌ เกิดข้อผิดพลาดในการรับเนื้อหา:', error);
        process.send({ type: 'content_error', error: error.message });
    }
})();
"""
            await self._run_puppeteer_script(script)
            self.logger.info("✅ รับเนื้อหาสำเร็จ")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการรับเนื้อหา: {e}")
            return False

    async def wait_for_element(self, selector: str, timeout: int = 10000):
        """รอ Element ปรากฏ"""
        try:
            self.logger.info(f"⏳ รอ Element: {selector}")
            
            script = f"""
(async () => {{
    try {{
        if (global.wawagod_page) {{
            await global.wawagod_page.waitForSelector('{selector}', {{ timeout: {timeout} }});
            console.log('✅ Element ปรากฏแล้ว: {selector}');
            process.send({{ type: 'wait_success', selector: '{selector}' }});
        }} else {{
            throw new Error('Page ไม่พร้อมใช้งาน');
        }}
    }} catch (error) {{
        console.error('❌ เกิดข้อผิดพลาดในการรอ Element:', error);
        process.send({{ type: 'wait_error', error: error.message }});
    }}
}})();
"""
            await self._run_puppeteer_script(script)
            self.logger.info(f"✅ Element ปรากฏแล้ว: {selector}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการรอ Element: {e}")
            return False

    async def stop_browser(self):
        """หยุด Browser"""
        try:
            self.logger.info("🔌 หยุด Puppeteer Browser...")
            
            script = """
(async () => {
    try {
        if (global.wawagod_browser) {
            await global.wawagod_browser.close();
            console.log('✅ หยุด Browser สำเร็จ');
            process.send({ type: 'browser_stopped' });
        } else {
            console.log('⚠️ Browser ไม่ได้เริ่มต้น');
            process.send({ type: 'browser_not_running' });
        }
    } catch (error) {
        console.error('❌ เกิดข้อผิดพลาดในการหยุด Browser:', error);
        process.send({ type: 'browser_stop_error', error: error.message });
    }
})();
"""
            await self._run_puppeteer_script(script)
            
            self.is_running = False
            self.logger.info("✅ หยุด Puppeteer Browser สำเร็จ")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการหยุด Browser: {e}")
            return False

    def get_status(self):
        """รับสถานะ"""
        return {
            'is_running': self.is_running,
            'browser': self.browser is not None,
            'page': self.page is not None,
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }

# Test Function
async def test_puppeteer():
    """ทดสอบ Puppeteer Controller"""
    print("🧪 ทดสอบ WAWAGOD Puppeteer Controller...")
    
    controller = WAWAGODPuppeteerController()
    
    # เริ่มต้น
    success = await controller.initialize()
    if not success:
        print("❌ เริ่มต้นล้มเหลว")
        return
    
    # เริ่มต้น Browser
    success = await controller.start_browser(headless=True)
    if success:
        print("✅ Browser เริ่มต้นสำเร็จ")
        
        # ทดสอบการนำทาง
        await controller.navigate_to("https://www.google.com")
        
        # ทดสอบการถ่าย Screenshot
        await controller.take_screenshot("test_screenshot.png")
        
        # หยุด Browser
        await controller.stop_browser()
    else:
        print("❌ Browser เริ่มต้นล้มเหลว")
    
    print("✅ ทดสอบเสร็จสิ้น")

if __name__ == "__main__":
    asyncio.run(test_puppeteer()) 