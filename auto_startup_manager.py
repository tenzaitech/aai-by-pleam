#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI - Auto Startup Manager
จัดการการรันระบบอัตโนมัติเมื่อเปิดเครื่อง
"""

import os
import sys
import winreg
import subprocess
from pathlib import Path

def get_startup_registry():
    """Get startup registry key"""
    try:
        return winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE
        )
    except Exception as e:
        print(f"❌ ไม่สามารถเปิด Registry ได้: {e}")
        return None

def add_to_startup():
    """Add WAWAGOT.AI to Windows startup"""
    try:
        # Get current script path
        script_path = Path(__file__).parent / "launch_v2.py"
        python_path = sys.executable
        
        # Create startup command
        startup_command = f'"{python_path}" "{script_path}"'
        
        # Add to registry
        key = get_startup_registry()
        if key:
            winreg.SetValueEx(
                key,
                "WAWAGOT.AI",
                0,
                winreg.REG_SZ,
                startup_command
            )
            winreg.CloseKey(key)
            print("✅ เพิ่ม WAWAGOT.AI ลงใน Startup สำเร็จ")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ ไม่สามารถเพิ่ม Startup ได้: {e}")
        return False

def remove_from_startup():
    """Remove WAWAGOT.AI from Windows startup"""
    try:
        key = get_startup_registry()
        if key:
            winreg.DeleteValue(key, "WAWAGOT.AI")
            winreg.CloseKey(key)
            print("✅ ลบ WAWAGOT.AI ออกจาก Startup สำเร็จ")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ ไม่สามารถลบ Startup ได้: {e}")
        return False

def check_startup_status():
    """Check if WAWAGOT.AI is in startup"""
    try:
        key = get_startup_registry()
        if key:
            try:
                value, _ = winreg.QueryValueEx(key, "WAWAGOT.AI")
                winreg.CloseKey(key)
                print("✅ WAWAGOT.AI อยู่ใน Startup แล้ว")
                print(f"   Command: {value}")
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                print("❌ WAWAGOT.AI ไม่ได้อยู่ใน Startup")
                return False
        else:
            return False
            
    except Exception as e:
        print(f"❌ ไม่สามารถตรวจสอบ Startup ได้: {e}")
        return False

def create_startup_script():
    """Create startup script"""
    try:
        script_content = '''@echo off
cd /d "%~dp0"
python launch_v2.py
pause
'''
        
        script_path = Path("startup_wawagot.bat")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"✅ สร้าง Startup Script: {script_path}")
        return str(script_path)
        
    except Exception as e:
        print(f"❌ ไม่สามารถสร้าง Startup Script ได้: {e}")
        return None

def show_menu():
    """Show startup manager menu"""
    print("\n" + "="*80)
    print("WAWAGOT.AI - Auto Startup Manager")
    print("="*80)
    print()
    print("📋 เลือกการดำเนินการ:")
    print()
    print("1. เพิ่ม WAWAGOT.AI ลงใน Startup")
    print("2. ลบ WAWAGOT.AI ออกจาก Startup")
    print("3. ตรวจสอบสถานะ Startup")
    print("4. สร้าง Startup Script")
    print("5. ออกจากโปรแกรม")
    print()

def main():
    """Main function"""
    print("🚀 WAWAGOT.AI Auto Startup Manager")
    print("จัดการการรันระบบอัตโนมัติเมื่อเปิดเครื่อง")
    
    while True:
        show_menu()
        try:
            choice = input("กรุณาเลือก (1-5): ").strip()
            
            if choice == '1':
                add_to_startup()
            elif choice == '2':
                remove_from_startup()
            elif choice == '3':
                check_startup_status()
            elif choice == '4':
                create_startup_script()
            elif choice == '5':
                print("\n👋 ขอบคุณที่ใช้งาน WAWAGOT.AI Auto Startup Manager")
                break
            else:
                print("❌ กรุณาเลือก 1-5")
            
            input("\nกด Enter เพื่อกลับไปเมนู...")
            
        except KeyboardInterrupt:
            print("\n\n👋 ขอบคุณที่ใช้งาน WAWAGOT.AI Auto Startup Manager")
            break
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            input("กด Enter เพื่อกลับไปเมนู...")

if __name__ == '__main__':
    main() 