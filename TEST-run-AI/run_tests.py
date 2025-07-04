#!/usr/bin/env python3
"""
WAWAGOT V.2 API Test Runner
ทดสอบ API ทั้งหมดอัตโนมัติ
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def install_test_dependencies():
    """ติดตั้ง dependencies สำหรับการทดสอบ"""
    print("📦 ติดตั้ง dependencies สำหรับการทดสอบ...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ ติดตั้ง dependencies สำเร็จ")
        return True
    except subprocess.CalledProcessError:
        print("❌ ติดตั้ง dependencies ล้มเหลว")
        return False

def check_server_status():
    """ตรวจสอบสถานะของ API server"""
    print("🔍 ตรวจสอบสถานะ API server...")
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server พร้อมใช้งาน")
            return True
        else:
            print(f"❌ API server ไม่พร้อมใช้งาน (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ API server ได้: {e}")
        return False

def run_api_tests():
    """รันการทดสอบ API"""
    print("🧪 เริ่มการทดสอบ API...")
    try:
        result = subprocess.run([
            sys.executable, "test_api_run.py"
        ], capture_output=True, text=True)
        
        print("📋 ผลการทดสอบ:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ ข้อผิดพลาด:")
            print(result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการทดสอบ: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("=" * 60)
    print("🧪 WAWAGOT V.2 API Test Runner")
    print("=" * 60)
    
    # เปลี่ยนไปยังโฟลเดอร์ TEST-run-AI
    test_dir = Path(__file__).parent
    os.chdir(test_dir)
    
    # ติดตั้ง dependencies
    if not install_test_dependencies():
        return 1
    
    # ตรวจสอบสถานะ server
    if not check_server_status():
        print("\n⚠️  หมายเหตุ:")
        print("1. ตรวจสอบว่าได้รัน 'python launch_v2.py' แล้ว")
        print("2. ตรวจสอบว่า API server ทำงานที่ port 8000")
        print("3. รันคำสั่งนี้ใหม่อีกครั้ง")
        return 1
    
    # รันการทดสอบ
    success = run_api_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 การทดสอบเสร็จสิ้น - ระบบทำงานปกติ")
    else:
        print("❌ การทดสอบพบปัญหา - ตรวจสอบข้อผิดพลาดข้างต้น")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 