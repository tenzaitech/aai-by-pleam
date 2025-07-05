#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test All New Systems - ทดสอบทุกระบบย่อยใหม่ 5 ระบบในครั้งเดียว
"""
import sys
import os
import time
import threading
sys.path.append('.')

def test_security_manager():
    """ทดสอบ SecurityManager"""
    print("=== 🔐 ทดสอบ SecurityManager ===")
    try:
        from security_manager import SecurityManager
        sm = SecurityManager()
        
        # ทดสอบ admin token
        result1 = sm.check_admin('changeme')
        result2 = sm.check_admin('wrong_token')
        
        if result1 and not result2:
            print("✅ SecurityManager: ผ่าน")
            return True
        else:
            print("❌ SecurityManager: ล้มเหลว")
            return False
    except Exception as e:
        print(f"❌ SecurityManager Error: {e}")
        return False

def test_monitoring_alert_system():
    """ทดสอบ MonitoringAlertSystem"""
    print("=== 📊 ทดสอบ MonitoringAlertSystem ===")
    try:
        from monitoring_alert_system import MonitoringAlertSystem
        mas = MonitoringAlertSystem(check_interval=1)
        
        # เริ่มระบบ
        mas.start()
        time.sleep(2)  # รอให้ทำงานสักครู่
        
        # ตรวจสอบสถานะ
        if mas.running:
            print("✅ MonitoringAlertSystem: ผ่าน")
            mas.stop()
            return True
        else:
            print("❌ MonitoringAlertSystem: ล้มเหลว")
            return False
    except Exception as e:
        print(f"❌ MonitoringAlertSystem Error: {e}")
        return False

def test_data_retention_manager():
    """ทดสอบ DataRetentionManager"""
    print("=== 🗂️ ทดสอบ DataRetentionManager ===")
    try:
        from data_retention_manager import DataRetentionManager
        drm = DataRetentionManager()
        
        # ตรวจสอบ config
        if drm.retention_days == 90 and drm.db_path == 'conversation_logs.db':
            print("✅ DataRetentionManager: ผ่าน")
            return True
        else:
            print("❌ DataRetentionManager: ล้มเหลว")
            return False
    except Exception as e:
        print(f"❌ DataRetentionManager Error: {e}")
        return False

def test_flexible_api_gateway():
    """ทดสอบ FlexibleAPIGateway"""
    print("=== 🌐 ทดสอบ FlexibleAPIGateway ===")
    try:
        from flexible_api_gateway import app, ADMIN_TOKEN, DB_PATH
        
        # ตรวจสอบ FastAPI app
        if app and ADMIN_TOKEN == 'changeme':
            print("✅ FlexibleAPIGateway: ผ่าน")
            return True
        else:
            print("❌ FlexibleAPIGateway: ล้มเหลว")
            return False
    except Exception as e:
        print(f"❌ FlexibleAPIGateway Error: {e}")
        return False

def test_web_dashboard_readme():
    """ทดสอบ WebDashboard README"""
    print("=== 📋 ทดสอบ WebDashboard README ===")
    try:
        readme_path = 'web_dashboard_README.md'
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'bolt.new' in content and 'export' in content:
                    print("✅ WebDashboard README: ผ่าน")
                    return True
                else:
                    print("❌ WebDashboard README: เนื้อหาไม่ครบ")
                    return False
        else:
            print("❌ WebDashboard README: ไม่พบไฟล์")
            return False
    except Exception as e:
        print(f"❌ WebDashboard README Error: {e}")
        return False

def main():
    """ทดสอบทุกระบบ"""
    print("🚀 เริ่มทดสอบทุกระบบย่อยใหม่ 5 ระบบ")
    print("=" * 50)
    
    results = {}
    
    # ทดสอบแต่ละระบบ
    results['SecurityManager'] = test_security_manager()
    results['MonitoringAlertSystem'] = test_monitoring_alert_system()
    results['DataRetentionManager'] = test_data_retention_manager()
    results['FlexibleAPIGateway'] = test_flexible_api_gateway()
    results['WebDashboard_README'] = test_web_dashboard_readme()
    
    # สรุปผล
    print("\n" + "=" * 50)
    print("📊 สรุปผลการทดสอบทุกระบบ")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for system, result in results.items():
        status = "✅ ผ่าน" if result else "❌ ล้มเหลว"
        print(f"{system}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 ผลรวม: {passed}/{total} ระบบผ่านการทดสอบ")
    
    if passed == total:
        print("🎉 ทุกระบบผ่านการทดสอบ! พร้อมใช้งาน")
    else:
        print("⚠️ มีระบบที่ต้องแก้ไข")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 ระบบย่อยใหม่ทั้งหมดพร้อมใช้งาน!")
    else:
        print("\n⚠️ ต้องแก้ไขระบบที่ล้มเหลว") 