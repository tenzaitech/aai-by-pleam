#!/usr/bin/env python3
"""
Install Dependencies Script
"""

import subprocess
import sys
import time

def install_package(package):
    """ติดตั้ง package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("📦 ติดตั้ง Dependencies...")
    
    packages = [
        "selenium==4.18.1",
        "openai==1.58.1",
        "pythainlp==5.1.2",
        "easyocr==1.7.2",
        "opencv-python==4.11.0.86",
        "pyautogui==0.9.54",
        "transformers==4.53.0",
        "torch==2.7.1"
    ]
    
    success_count = 0
    for package in packages:
        print(f"📦 ติดตั้ง {package}...")
        if install_package(package):
            print(f"✅ {package} สำเร็จ")
            success_count += 1
        else:
            print(f"❌ {package} ล้มเหลว")
        time.sleep(1)
    
    print(f"📊 ติดตั้งสำเร็จ: {success_count}/{len(packages)}")
    
    if success_count == len(packages):
        print("🎯 การติดตั้งเสร็จสมบูรณ์!")
    else:
        print("⚠️ บาง packages ติดตั้งไม่สำเร็จ")

if __name__ == "__main__":
    main()
