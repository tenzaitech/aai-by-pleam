#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI - Service Manager
จัดการ Windows Service สำหรับรันระบบตลอดเวลา
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command):
    """Run command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_admin():
    """Check if running as administrator"""
    try:
        return subprocess.run("net session", shell=True, capture_output=True).returncode == 0
    except:
        return False

def install_service():
    """Install WAWAGOT.AI service"""
    print("🔧 ติดตั้ง WAWAGOT.AI Service...")
    
    # Install required packages
    print("📦 ติดตั้ง packages ที่จำเป็น...")
    success, stdout, stderr = run_command("pip install pywin32 psutil")
    if not success:
        print(f"❌ ไม่สามารถติดตั้ง packages ได้: {stderr}")
        return False
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Install service
    success, stdout, stderr = run_command("python wawagot_windows_service.py install")
    if success:
        print("✅ ติดตั้ง Service สำเร็จ")
        return True
    else:
        print(f"❌ ติดตั้ง Service ไม่สำเร็จ: {stderr}")
        return False

def start_service():
    """Start WAWAGOT.AI service"""
    print("🚀 เริ่มต้น Service...")
    success, stdout, stderr = run_command("python wawagot_windows_service.py start")
    if success:
        print("✅ เริ่มต้น Service สำเร็จ")
        return True
    else:
        print(f"❌ เริ่มต้น Service ไม่สำเร็จ: {stderr}")
        return False

def stop_service():
    """Stop WAWAGOT.AI service"""
    print("🛑 หยุด Service...")
    success, stdout, stderr = run_command("python wawagot_windows_service.py stop")
    if success:
        print("✅ หยุด Service สำเร็จ")
        return True
    else:
        print(f"❌ หยุด Service ไม่สำเร็จ: {stderr}")
        return False

def restart_service():
    """Restart WAWAGOT.AI service"""
    print("🔄 รีสตาร์ท Service...")
    success, stdout, stderr = run_command("python wawagot_windows_service.py restart")
    if success:
        print("✅ รีสตาร์ท Service สำเร็จ")
        return True
    else:
        print(f"❌ รีสตาร์ท Service ไม่สำเร็จ: {stderr}")
        return False

def check_status():
    """Check service status"""
    print("📊 ตรวจสอบสถานะ Service...")
    success, stdout, stderr = run_command("python wawagot_windows_service.py status")
    if success:
        print("✅ Service กำลังทำงาน")
        print(stdout)
    else:
        print("❌ Service ไม่ทำงาน")
        print(stderr)
    
    print("\n📋 ตรวจสอบใน Services.msc:")
    print("   - กด Win+R แล้วพิมพ์ services.msc")
    print("   - ค้นหา 'WAWAGOT.AI System Service'")

def remove_service():
    """Remove WAWAGOT.AI service"""
    print("⚠️ ต้องการลบ Service หรือไม่?")
    confirm = input("พิมพ์ 'yes' เพื่อยืนยัน: ")
    if confirm.lower() == 'yes':
        success, stdout, stderr = run_command("python wawagot_windows_service.py remove")
        if success:
            print("✅ ลบ Service สำเร็จ")
        else:
            print(f"❌ ลบ Service ไม่สำเร็จ: {stderr}")
    else:
        print("❌ ยกเลิกการลบ")

def view_log():
    """View service log"""
    log_file = Path("logs/wawagot_service.log")
    if log_file.exists():
        print("📝 เปิด Log File...")
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content[-2000:])  # Show last 2000 characters
        except Exception as e:
            print(f"❌ ไม่สามารถอ่านไฟล์ log ได้: {e}")
    else:
        print("❌ ไม่พบไฟล์ log")

def show_menu():
    """Show service manager menu"""
    print("\n" + "="*80)
    print("WAWAGOT.AI - Service Manager")
    print("="*80)
    print()
    print("📋 เลือกการดำเนินการ:")
    print()
    print("1. ติดตั้ง Service")
    print("2. เริ่มต้น Service")
    print("3. หยุด Service")
    print("4. รีสตาร์ท Service")
    print("5. ตรวจสอบสถานะ")
    print("6. ลบ Service")
    print("7. ดู Log")
    print("8. ออกจากโปรแกรม")
    print()

def main():
    """Main function"""
    # Check if running as administrator
    if not check_admin():
        print("❌ ต้องรันเป็น Administrator")
        print("กรุณาคลิกขวาที่ไฟล์นี้แล้วเลือก 'Run as administrator'")
        input("กด Enter เพื่อออก...")
        return
    
    print("✅ รันเป็น Administrator แล้ว")
    
    # Check Python installation
    success, stdout, stderr = run_command("python --version")
    if not success:
        print("❌ ไม่พบ Python")
        print("กรุณาติดตั้ง Python ก่อน")
        input("กด Enter เพื่อออก...")
        return
    
    print("✅ Python พร้อมใช้งาน")
    
    while True:
        show_menu()
        try:
            choice = input("กรุณาเลือก (1-8): ").strip()
            
            if choice == '1':
                install_service()
            elif choice == '2':
                start_service()
            elif choice == '3':
                stop_service()
            elif choice == '4':
                restart_service()
            elif choice == '5':
                check_status()
            elif choice == '6':
                remove_service()
            elif choice == '7':
                view_log()
            elif choice == '8':
                print("\n👋 ขอบคุณที่ใช้งาน WAWAGOT.AI Service Manager")
                break
            else:
                print("❌ กรุณาเลือก 1-8")
            
            input("\nกด Enter เพื่อกลับไปเมนู...")
            
        except KeyboardInterrupt:
            print("\n\n👋 ขอบคุณที่ใช้งาน WAWAGOT.AI Service Manager")
            break
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            input("กด Enter เพื่อกลับไปเมนู...")

if __name__ == '__main__':
    main() 