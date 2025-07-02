#!/usr/bin/env python3
"""
Test Chrome Minimal - ทดสอบ Chrome แบบ minimal
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_chrome_minimal():
    """ทดสอบ Chrome แบบ minimal"""
    print("🚀 ทดสอบ Chrome แบบ minimal...")
    
    try:
        # สร้าง Chrome options แบบ minimal
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        print("📱 สร้าง Chrome driver...")
        driver = webdriver.Chrome(options=options)
        
        print("✅ Chrome เปิดสำเร็จ!")
        print(f"🔍 Session ID: {driver.session_id}")
        
        # ทดสอบการนำทาง
        print("🌐 ทดสอบการนำทาง...")
        driver.get("https://www.google.com")
        print(f"✅ เปิด URL สำเร็จ: {driver.current_url}")
        
        # รอสักครู่
        time.sleep(3)
        
        print("🎯 ทดสอบเสร็จสิ้น!")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")

def test_chrome_headless():
    """ทดสอบ Chrome แบบ headless"""
    print("\n🚀 ทดสอบ Chrome แบบ headless...")
    
    try:
        # สร้าง Chrome options แบบ minimal + headless
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")
        
        print("📱 สร้าง Chrome driver (headless)...")
        driver = webdriver.Chrome(options=options)
        
        print("✅ Chrome headless เปิดสำเร็จ!")
        print(f"🔍 Session ID: {driver.session_id}")
        
        # ทดสอบการนำทาง
        print("🌐 ทดสอบการนำทาง...")
        driver.get("https://www.google.com")
        print(f"✅ เปิด URL สำเร็จ: {driver.current_url}")
        
        # รอสักครู่
        time.sleep(3)
        
        print("🎯 ทดสอบ headless เสร็จสิ้น!")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_chrome_minimal()
    test_chrome_headless() 