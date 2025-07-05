#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for SecurityManager - Auto Test
"""
import sys
import os
sys.path.append('.')

from security_manager import SecurityManager

def test_security_manager():
    print("=== 🔐 ทดสอบ SecurityManager แบบอัตโนมัติ ===")
    
    try:
        # สร้าง instance
        sm = SecurityManager()
        print("✅ สร้าง SecurityManager สำเร็จ")
        
        # ทดสอบ admin token ถูกต้อง (default: changeme)
        result1 = sm.check_admin('changeme')
        print(f"✅ ทดสอบ admin token ถูกต้อง: {result1}")
        
        # ทดสอบ admin token ผิด
        result2 = sm.check_admin('wrong_token')
        print(f"✅ ทดสอบ admin token ผิด: {result2}")
        
        # ทดสอบ config
        print(f"✅ Admin token ใน config: {sm.admin_token}")
        print(f"✅ Log level: {sm.config.get('log_level')}")
        
        print("\n=== 📊 ผลการทดสอบ ===")
        if result1 and not result2:
            print("🎉 SecurityManager ทำงานได้ปกติ!")
            print("✅ Admin token: 'changeme'")
            print("✅ ระบบพร้อมใช้งาน")
            return True
        else:
            print("❌ มีปัญหาในการทดสอบ")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    success = test_security_manager()
    if success:
        print("\n🎯 SecurityManager พร้อมใช้งาน!")
    else:
        print("\n⚠️ ต้องแก้ไขปัญหาใน SecurityManager") 