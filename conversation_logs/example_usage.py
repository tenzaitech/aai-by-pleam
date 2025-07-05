#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ตัวอย่างการใช้งานระบบย่อยทั้งหมด WAWAGOT.AI
พร้อม Python Auto Import ใน Cursor
"""

# ตัวอย่างการ import แบบง่าย (Auto Import จะช่วยแนะนำ)
from conversation_logs import (
    SecurityManager,
    MonitoringAlertSystem,
    DataRetentionManager,
    AutoLogger,
    AIFilter,
    ConversationManager,
    AutoBackup,
    IntegrationManager
)

def example_usage():
    """ตัวอย่างการใช้งานระบบย่อยทั้งหมด"""
    
    print("=== 🚀 ตัวอย่างการใช้งานระบบย่อย WAWAGOT.AI ===")
    
    # 1. SecurityManager
    print("\n1. 🔐 SecurityManager")
    sm = SecurityManager()
    if sm.check_admin('changeme'):
        print("   ✅ Admin access granted")
    
    # 2. MonitoringAlertSystem
    print("\n2. 📊 MonitoringAlertSystem")
    mas = MonitoringAlertSystem(check_interval=5)
    mas.start()
    print("   ✅ Monitoring started")
    mas.stop()
    
    # 3. DataRetentionManager
    print("\n3. 🗂️ DataRetentionManager")
    drm = DataRetentionManager()
    print(f"   ✅ Retention days: {drm.retention_days}")
    
    # 4. AutoLogger
    print("\n4. 📝 AutoLogger")
    al = AutoLogger()
    print("   ✅ AutoLogger initialized")
    
    # 5. AIFilter
    print("\n5. 🧠 AIFilter")
    af = AIFilter()
    print("   ✅ AIFilter initialized")
    
    # 6. ConversationManager
    print("\n6. 💬 ConversationManager")
    cm = ConversationManager()
    print("   ✅ ConversationManager initialized")
    
    # 7. AutoBackup
    print("\n7. 💾 AutoBackup")
    ab = AutoBackup()
    print("   ✅ AutoBackup initialized")
    
    # 8. IntegrationManager
    print("\n8. 🔗 IntegrationManager")
    im = IntegrationManager()
    print("   ✅ IntegrationManager initialized")
    
    print("\n🎉 ทุกระบบย่อยพร้อมใช้งาน!")

if __name__ == "__main__":
    example_usage() 