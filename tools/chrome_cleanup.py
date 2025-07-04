#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Cleanup Script
ปิด Chrome processes ที่ค้างอยู่
"""

import os
import subprocess
import psutil
import sys

def kill_chrome_processes():
    """ปิด Chrome processes ทั้งหมด"""
    print("🔍 กำลังค้นหา Chrome processes...")
    
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            if 'chrome' in proc_name:
                print(f"🔄 ปิด process: {proc.info['name']} (PID: {proc.info['pid']})")
                proc.kill()
                killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    print(f"✅ ปิด Chrome processes ไปแล้ว {killed_count} ตัว")
    return killed_count

def kill_chromedriver_processes():
    """ปิด ChromeDriver processes"""
    print("🔍 กำลังค้นหา ChromeDriver processes...")
    
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            if 'chromedriver' in proc_name:
                print(f"🔄 ปิด process: {proc.info['name']} (PID: {proc.info['pid']})")
                proc.kill()
                killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    print(f"✅ ปิด ChromeDriver processes ไปแล้ว {killed_count} ตัว")
    return killed_count

def cleanup_chrome_data():
    """ลบ Chrome temporary data"""
    print("🧹 กำลังลบ Chrome temporary data...")
    
    chrome_data_dirs = [
        os.path.expanduser("~/.config/google-chrome"),
        os.path.expanduser("~/AppData/Local/Google/Chrome/User Data"),
        os.path.expanduser("~/Library/Application Support/Google/Chrome")
    ]
    
    cleaned_count = 0
    
    for data_dir in chrome_data_dirs:
        if os.path.exists(data_dir):
            try:
                # ลบเฉพาะ temporary files
                temp_dirs = ["Cache", "Code Cache", "GPUCache"]
                for temp_dir in temp_dirs:
                    temp_path = os.path.join(data_dir, "Default", temp_dir)
                    if os.path.exists(temp_path):
                        import shutil
                        shutil.rmtree(temp_path)
                        print(f"🧹 ลบ {temp_path}")
                        cleaned_count += 1
            except Exception as e:
                print(f"⚠️ ไม่สามารถลบ {data_dir}: {e}")
    
    print(f"✅ ลบ temporary data ไปแล้ว {cleaned_count} โฟลเดอร์")
    return cleaned_count

def main():
    """ฟังก์ชันหลัก"""
    print("🚨 Chrome Cleanup Script")
    print("=" * 40)
    
    try:
        # ปิด Chrome processes
        chrome_killed = kill_chrome_processes()
        
        # ปิด ChromeDriver processes
        driver_killed = kill_chromedriver_processes()
        
        # ลบ temporary data
        data_cleaned = cleanup_chrome_data()
        
        print("\n📊 สรุปการทำความสะอาด:")
        print(f"   - Chrome processes ที่ปิด: {chrome_killed}")
        print(f"   - ChromeDriver processes ที่ปิด: {driver_killed}")
        print(f"   - Temporary data ที่ลบ: {data_cleaned}")
        
        if chrome_killed > 0 or driver_killed > 0:
            print("\n✅ Chrome cleanup เสร็จสิ้น!")
        else:
            print("\nℹ️ ไม่พบ Chrome processes ที่ต้องปิด")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 