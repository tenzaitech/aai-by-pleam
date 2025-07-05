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
import logging
import shutil
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/chrome_cleanup.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def kill_chrome_processes():
    """ปิด Chrome processes ทั้งหมด"""
    logger.info("Starting Chrome processes cleanup")
    print("🔍 กำลังค้นหา Chrome processes...")
    
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            if 'chrome' in proc_name:
                print(f"🔄 ปิด process: {proc.info['name']} (PID: {proc.info['pid']})")
                logger.info(f"Killing Chrome process: {proc.info['name']} (PID: {proc.info['pid']})")
                proc.kill()
                killed_count += 1
        except psutil.NoSuchProcess:
            logger.debug(f"Process {proc.info.get('pid', 'unknown')} no longer exists")
        except psutil.AccessDenied:
            logger.warning(f"Access denied to process {proc.info.get('pid', 'unknown')}")
        except psutil.ZombieProcess:
            logger.debug(f"Zombie process {proc.info.get('pid', 'unknown')} encountered")
        except Exception as e:
            logger.error(f"Unexpected error killing Chrome process: {e}")
    
    print(f"✅ ปิด Chrome processes ไปแล้ว {killed_count} ตัว")
    logger.info(f"Chrome processes cleanup completed: {killed_count} processes killed")
    return killed_count

def kill_chromedriver_processes():
    """ปิด ChromeDriver processes"""
    logger.info("Starting ChromeDriver processes cleanup")
    print("🔍 กำลังค้นหา ChromeDriver processes...")
    
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            if 'chromedriver' in proc_name:
                print(f"🔄 ปิด process: {proc.info['name']} (PID: {proc.info['pid']})")
                logger.info(f"Killing ChromeDriver process: {proc.info['name']} (PID: {proc.info['pid']})")
                proc.kill()
                killed_count += 1
        except psutil.NoSuchProcess:
            logger.debug(f"ChromeDriver process {proc.info.get('pid', 'unknown')} no longer exists")
        except psutil.AccessDenied:
            logger.warning(f"Access denied to ChromeDriver process {proc.info.get('pid', 'unknown')}")
        except psutil.ZombieProcess:
            logger.debug(f"Zombie ChromeDriver process {proc.info.get('pid', 'unknown')} encountered")
        except Exception as e:
            logger.error(f"Unexpected error killing ChromeDriver process: {e}")
    
    print(f"✅ ปิด ChromeDriver processes ไปแล้ว {killed_count} ตัว")
    logger.info(f"ChromeDriver processes cleanup completed: {killed_count} processes killed")
    return killed_count

def cleanup_chrome_data():
    """ลบ Chrome temporary data"""
    logger.info("Starting Chrome temporary data cleanup")
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
                        shutil.rmtree(temp_path)
                        print(f"🧹 ลบ {temp_path}")
                        logger.info(f"Cleaned Chrome temp directory: {temp_path}")
                        cleaned_count += 1
            except PermissionError as e:
                error_msg = f"Permission denied cleaning {data_dir}: {e}"
                logger.warning(error_msg)
                print(f"⚠️ ไม่สามารถลบ {data_dir}: Permission denied")
            except FileNotFoundError as e:
                logger.debug(f"Directory not found during cleanup: {data_dir}")
            except Exception as e:
                error_msg = f"Error cleaning Chrome data directory {data_dir}: {e}"
                logger.error(error_msg)
                print(f"⚠️ ไม่สามารถลบ {data_dir}: {e}")
    
    print(f"✅ ลบ temporary data ไปแล้ว {cleaned_count} โฟลเดอร์")
    logger.info(f"Chrome temporary data cleanup completed: {cleaned_count} directories cleaned")
    return cleaned_count

def main():
    """ฟังก์ชันหลัก"""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Chrome Cleanup Script starting...")
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
        
        logger.info(f"Cleanup summary - Chrome: {chrome_killed}, ChromeDriver: {driver_killed}, Data: {data_cleaned}")
        
        if chrome_killed > 0 or driver_killed > 0:
            success_msg = "Chrome cleanup completed successfully!"
            print(f"\n✅ {success_msg}")
            logger.info(success_msg)
        else:
            info_msg = "No Chrome processes found to kill"
            print(f"\nℹ️ {info_msg}")
            logger.info(info_msg)
            
    except KeyboardInterrupt:
        logger.info("Chrome cleanup interrupted by user")
        print("\n⚠️ การทำความสะอาดถูกยกเลิกโดยผู้ใช้")
        return 1
    except Exception as e:
        error_msg = f"Critical error in Chrome cleanup: {e}"
        logger.error(error_msg)
        logger.error(f"Traceback: {sys.exc_info()}")
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return 1
    
    logger.info("Chrome Cleanup Script completed successfully")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 