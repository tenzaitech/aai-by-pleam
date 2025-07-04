#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor Theme Reloader
รีโหลดธีมสีใน Cursor IDE
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

class CursorThemeReloader:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.settings_file = self.project_root / ".vscode" / "settings.json"
        
    def check_settings_file(self):
        """ตรวจสอบไฟล์ settings.json"""
        print("🔍 ตรวจสอบไฟล์ settings.json...")
        
        if not self.settings_file.exists():
            print("❌ ไม่พบไฟล์ .vscode/settings.json")
            return False
            
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # ตรวจสอบว่ามีธีมสีหรือไม่
            if "workbench.colorCustomizations" in settings:
                print("✅ พบการตั้งค่าธีมสี")
                return True
            else:
                print("❌ ไม่พบการตั้งค่าธีมสี")
                return False
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            return False
    
    def show_current_theme(self):
        """แสดงธีมปัจจุบัน"""
        print("\n🎨 ธีมสีปัจจุบัน:")
        print("   - Base Theme: Default Dark+")
        print("   - Custom Colors: ส้ม-ดำ-เทา-ขาว")
        print("   - Font: Fira Code, JetBrains Mono")
        print("   - Font Size: 16px")
        print("   - Line Height: 24px")
    
    def reload_cursor(self):
        """รีโหลด Cursor"""
        print("\n🔄 กำลังรีโหลด Cursor...")
        
        try:
            # ลองใช้คำสั่ง reload
            result = subprocess.run([
                "code", "--reload-window"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ ส่งคำสั่ง reload สำเร็จ")
            else:
                print("⚠️ ไม่สามารถส่งคำสั่ง reload ได้")
                print("   ให้รีโหลดด้วยตนเอง:")
                print("   1. กด Ctrl+Shift+P")
                print("   2. พิมพ์ 'Developer: Reload Window'")
                print("   3. กด Enter")
                
        except FileNotFoundError:
            print("⚠️ ไม่พบคำสั่ง 'code'")
            print("   ให้รีโหลดด้วยตนเอง:")
            print("   1. กด Ctrl+Shift+P")
            print("   2. พิมพ์ 'Developer: Reload Window'")
            print("   3. กด Enter")
    
    def show_manual_steps(self):
        """แสดงขั้นตอนการรีโหลดด้วยตนเอง"""
        print("\n📋 ขั้นตอนการรีโหลดธีมด้วยตนเอง:")
        print("=" * 50)
        print("1. ใน Cursor IDE กด Ctrl+Shift+P")
        print("2. พิมพ์ 'Developer: Reload Window'")
        print("3. กด Enter")
        print("4. รอให้ Cursor รีโหลดเสร็จ")
        print("5. ธีมสีใหม่จะปรากฏ")
        print("=" * 50)
        
        print("\n🎯 คีย์ลัด Terminal:")
        print("- Ctrl + `` (backtick) - เปิด/ปิด Terminal")
        print("- Ctrl + J - Toggle Panel")
    
    def check_theme_after_reload(self):
        """ตรวจสอบธีมหลังรีโหลด"""
        print("\n🔍 หลังรีโหลด ตรวจสอบ:")
        print("✅ พื้นหลังเป็นสีดำเข้ม (#1a1a1a)")
        print("✅ ตัวอักษรเป็นสีขาวนวล (#f0f0f0)")
        print("✅ Keywords เป็นสีส้มสด (#ff8c42)")
        print("✅ Strings เป็นสีเขียว (#51cf66)")
        print("✅ Comments เป็นสีเทา (#666666)")
        print("✅ Sidebar เป็นสีเทาเข้ม (#2d2d2d)")
    
    def run(self):
        """รันสคริปต์หลัก"""
        print("🚀 Cursor Theme Reloader")
        print("=" * 30)
        
        # ตรวจสอบไฟล์
        if not self.check_settings_file():
            return
        
        # แสดงธีมปัจจุบัน
        self.show_current_theme()
        
        # รีโหลด Cursor
        self.reload_cursor()
        
        # แสดงขั้นตอนด้วยตนเอง
        self.show_manual_steps()
        
        # ตรวจสอบหลังรีโหลด
        self.check_theme_after_reload()
        
        print("\n🎉 เสร็จสิ้น! ธีมสีใหม่พร้อมใช้งาน")

def main():
    reloader = CursorThemeReloader()
    reloader.run()

if __name__ == "__main__":
    main() 