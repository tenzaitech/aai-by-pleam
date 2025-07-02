#!/usr/bin/env python3
"""
Parallel Chrome Test - WAWA
เปิด Chrome 2 windows, จัดเรียงซ้าย-ขวา, พิมพ์ตัวเลขสุ่ม 10 วินาที
"""

import asyncio
import random
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

class ParallelChromeTest:
    def __init__(self):
        self.drivers = []
        self.screen_width = 1920  # ปรับตามจอของคุณ
        self.screen_height = 1080
        
    def create_chrome_window(self, window_position):
        """สร้าง Chrome window ใหม่"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-web-security")
        options.add_argument("--remote-debugging-port=0")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
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
        options.add_argument("--disable-features=BlinkGenPropertyTrees")
        options.add_argument("--disable-features=CalculateNativeWinOcclusion")
        options.add_argument("--disable-features=GlobalMediaControls")
        options.add_argument("--disable-features=MediaRouter")
        options.add_argument("--disable-features=OptimizationHints")
        options.add_argument("--disable-features=PasswordGeneration")
        options.add_argument("--disable-features=PreloadMediaEngagementData")
        options.add_argument("--disable-features=Translate")
        options.add_argument("--disable-features=WebUIDarkMode")
        
        # ตั้งค่าขนาดและตำแหน่ง window
        options.add_argument(f"--window-size={self.screen_width//2},{self.screen_height}")
        options.add_argument(f"--window-position={window_position},0")
        
        # ใช้ remote debugging port ที่แตกต่างกัน
        if window_position == 0:
            options.add_argument("--remote-debugging-port=9222")
        else:
            options.add_argument("--remote-debugging-port=9223")
        
        driver = webdriver.Chrome(options=options)
        return driver
    
    def position_window(self, driver, position):
        """จัดตำแหน่ง window"""
        if position == "left":
            driver.set_window_position(0, 0)
            driver.set_window_size(self.screen_width//2, self.screen_height)
        else:  # right
            driver.set_window_position(self.screen_width//2, 0)
            driver.set_window_size(self.screen_width//2, self.screen_height)
    
    def random_typing_test(self, driver, duration=10):
        """พิมพ์ตัวเลขสุ่มและลบแบบสุ่ม"""
        try:
            # ไปที่ Google
            driver.get("https://www.google.com")
            
            # รอให้ search box โหลด
            wait = WebDriverWait(driver, 10)
            search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
            
            start_time = time.time()
            while time.time() - start_time < duration:
                # สุ่มว่าจะพิมพ์หรือลบ
                action = random.choice(['type', 'delete'])
                
                if action == 'type':
                    # พิมพ์ตัวเลขสุ่ม 1-3 ตัว
                    digits = ''.join([str(random.randint(0, 9)) for _ in range(random.randint(1, 3))])
                    search_box.send_keys(digits)
                    time.sleep(random.uniform(0.1, 0.3))
                else:
                    # ลบตัวอักษรสุ่ม 1-3 ตัว
                    delete_count = random.randint(1, 3)
                    for _ in range(delete_count):
                        search_box.send_keys(Keys.BACKSPACE)
                        time.sleep(random.uniform(0.1, 0.2))
                
                time.sleep(random.uniform(0.1, 0.5))
                
        except Exception as e:
            print(f"Error in random typing test: {e}")
    
    async def run_parallel_test(self):
        """รันการทดสอบแบบ parallel"""
        print("🚀 เริ่ม Parallel Chrome Test...")
        
        try:
            # สร้าง Chrome windows 2 ตัว
            print("📱 สร้าง Chrome windows...")
            driver1 = self.create_chrome_window(0)  # ซ้าย
            time.sleep(2)  # รอให้ window แรกสร้างเสร็จ
            driver2 = self.create_chrome_window(self.screen_width//2)  # ขวา
            
            self.drivers = [driver1, driver2]
            
            # จัดตำแหน่ง windows
            print("📍 จัดตำแหน่ง windows...")
            self.position_window(driver1, "left")
            time.sleep(1)
            self.position_window(driver2, "right")
            
            # รันการทดสอบแบบ parallel
            print("⌨️ เริ่มพิมพ์ตัวเลขสุ่ม 10 วินาที...")
            start_time = time.time()
            
            # สร้าง threads สำหรับแต่ละ window
            thread1 = threading.Thread(target=self.random_typing_test, args=(driver1, 10))
            thread2 = threading.Thread(target=self.random_typing_test, args=(driver2, 10))
            
            thread1.start()
            thread2.start()
            
            thread1.join()
            thread2.join()
            
            print(f"✅ เสร็จสิ้น! ใช้เวลา {time.time() - start_time:.2f} วินาที")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            # ปิด browsers - DISABLED
            print("🔒 ปิด Chrome windows - DISABLED")
            for driver in self.drivers:
                try:
                    print(f"[DEBUG] driver.quit() called from: {traceback.format_stack()}")
                    # driver.quit()  # DISABLED - ไม่ให้ปิด Chrome อัตโนมัติ
                    pass
                except:
                    pass
            
            print("🎯 Parallel Chrome Test เสร็จสิ้น! (Chrome cleanup disabled)")

async def main():
    """Main function"""
    test = ParallelChromeTest()
    await test.run_parallel_test()

if __name__ == "__main__":
    asyncio.run(main()) 