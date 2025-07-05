#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สร้างตารางผ่าน Supabase REST API โดยตรง
"""

import os
import requests
import json
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv()

def create_tables_via_api():
    """สร้างตารางผ่าน Supabase REST API"""
    print("🚀 สร้างตารางผ่าน Supabase REST API")
    print("=" * 60)
    
    # อ่านค่า environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ ไม่พบ SUPABASE_URL หรือ SUPABASE_KEY ใน environment")
        return
    
    print(f"📡 URL: {supabase_url}")
    print(f"🔑 Key: {supabase_key[:20]}...")
    print()
    
    # Headers สำหรับ API
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # ข้อมูลตัวอย่างสำหรับสร้างตาราง
    sample_data = {
        'conversation_logs': {
            'session_id': 'test_session_001',
            'user_id': 'test_user_001',
            'user_message': 'สวัสดีครับ',
            'ai_response': 'สวัสดีครับ! มีอะไรให้ช่วยเหลือไหมครับ?',
            'model_used': 'gpt-4',
            'tokens_used': 50,
            'response_time_ms': 1500,
            'status': 'success',
            'metadata': {'source': 'test'}
        },
        'user_profiles': {
            'user_id': 'test_user_001',
            'email': 'test@example.com',
            'username': 'testuser',
            'full_name': 'Test User',
            'preferences': {'theme': 'dark', 'language': 'th'}
        },
        'system_logs': {
            'level': 'INFO',
            'component': 'test_system',
            'message': 'ระบบทดสอบทำงานปกติ',
            'user_id': 'test_user_001',
            'session_id': 'test_session_001',
            'metadata': {'test': True}
        },
        'knowledge_base': {
            'title': 'คู่มือการใช้งานระบบ',
            'content': 'นี่คือคู่มือการใช้งานระบบ WAWAGOT.AI',
            'category': 'guide',
            'tags': ['guide', 'manual'],
            'source': 'system',
            'created_by': 'system'
        },
        'backup_logs': {
            'backup_type': 'full',
            'status': 'success',
            'file_path': '/backups/test_backup.zip',
            'file_size': 1024000,
            'duration_seconds': 300,
            'records_backed_up': 1000,
            'metadata': {'test': True}
        },
        'health_checks': {
            'check_type': 'database',
            'status': 'success',
            'response_time_ms': 150,
            'details': {'database': 'supabase', 'connection': 'stable'}
        },
        'alerts': {
            'alert_type': 'system',
            'severity': 'info',
            'title': 'ระบบทำงานปกติ',
            'message': 'ระบบ WAWAGOT.AI ทำงานปกติ',
            'metadata': {'test': True}
        },
        'environment_data': {
            'component': 'system',
            'metric_name': 'cpu_usage',
            'metric_value': '25',
            'unit': 'percent',
            'metadata': {'test': True}
        },
        'file_management': {
            'file_name': 'test_file.txt',
            'file_path': '/uploads/test_file.txt',
            'file_size': 1024,
            'file_type': 'text',
            'mime_type': 'text/plain',
            'uploaded_by': 'test_user_001',
            'processing_status': 'completed',
            'metadata': {'test': True}
        },
        'system_config': {
            'config_key': 'test_config',
            'config_value': 'test_value',
            'config_type': 'string',
            'description': 'การตั้งค่าทดสอบ',
            'updated_by': 'system'
        }
    }
    
    # ทดสอบสร้างข้อมูลในแต่ละตาราง
    results = {}
    
    for table_name, data in sample_data.items():
        try:
            print(f"🔨 ทดสอบสร้างข้อมูลในตาราง: {table_name}")
            
            # URL สำหรับ API
            api_url = f"{supabase_url}/rest/v1/{table_name}"
            
            # ส่ง POST request
            response = requests.post(
                api_url,
                headers=headers,
                json=data
            )
            
            if response.status_code in [201, 200]:
                print(f"   ✅ สำเร็จ: สร้างข้อมูลในตาราง {table_name}")
                results[table_name] = "success"
            else:
                print(f"   ❌ ล้มเหลว: {response.status_code} - {response.text[:100]}")
                results[table_name] = f"error_{response.status_code}"
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {str(e)[:100]}")
            results[table_name] = f"exception_{str(e)[:50]}"
    
    # สรุปผล
    print("\n" + "=" * 60)
    print("📊 สรุปผลการสร้างข้อมูล")
    print("=" * 60)
    
    success_count = sum(1 for result in results.values() if result == "success")
    total_count = len(results)
    
    print(f"\n✅ สำเร็จ: {success_count}/{total_count} ตาราง")
    print(f"❌ ล้มเหลว: {total_count - success_count}/{total_count} ตาราง")
    
    if success_count > 0:
        print(f"\n✅ ตารางที่สร้างสำเร็จ:")
        for table, result in results.items():
            if result == "success":
                print(f"   - {table}")
    
    if total_count - success_count > 0:
        print(f"\n❌ ตารางที่มีปัญหา:")
        for table, result in results.items():
            if result != "success":
                print(f"   - {table}: {result}")
    
    return results

def check_table_structure():
    """ตรวจสอบโครงสร้างตาราง"""
    print("\n" + "=" * 60)
    print("🔍 ตรวจสอบโครงสร้างตาราง")
    print("=" * 60)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # รายชื่อตารางที่ต้องการตรวจสอบ
    tables = [
        'conversation_logs',
        'user_profiles', 
        'system_logs',
        'knowledge_base',
        'backup_logs',
        'health_checks',
        'alerts',
        'environment_data',
        'file_management',
        'system_config'
    ]
    
    existing_tables = []
    missing_tables = []
    
    for table in tables:
        try:
            api_url = f"{supabase_url}/rest/v1/{table}?select=*&limit=1"
            response = requests.get(api_url, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ ตาราง {table} มีอยู่")
                existing_tables.append(table)
            else:
                print(f"❌ ตาราง {table} ไม่มี")
                missing_tables.append(table)
                
        except Exception as e:
            print(f"❌ ไม่สามารถตรวจสอบตาราง {table}: {e}")
            missing_tables.append(table)
    
    print(f"\n📊 สรุป: มีตาราง {len(existing_tables)}/{len(tables)} ตาราง")
    
    if missing_tables:
        print(f"\n💡 ตารางที่ต้องสร้าง: {', '.join(missing_tables)}")
        print("\n📝 วิธีสร้างตาราง:")
        print("   1. ไปที่ https://supabase.com/dashboard")
        print("   2. เลือกโปรเจค TENZAITECH-DATABASE")
        print("   3. ไปที่ SQL Editor")
        print("   4. รันไฟล์ wawagot_tables.sql")
    
    return existing_tables, missing_tables

if __name__ == "__main__":
    # ตรวจสอบโครงสร้างตารางก่อน
    existing, missing = check_table_structure()
    
    if missing:
        print(f"\n🚀 เริ่มสร้างข้อมูลในตารางที่มีอยู่...")
        create_tables_via_api()
    else:
        print(f"\n✅ ตารางทั้งหมดมีอยู่แล้ว เริ่มสร้างข้อมูล...")
        create_tables_via_api()
    
    print("\n✅ เสร็จสิ้นการตรวจสอบและสร้างข้อมูล") 