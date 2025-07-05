#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ตรวจสอบชื่อตารางใน Supabase Database
"""

import os
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv()

try:
    from supabase import create_client, Client
    import json
except ImportError as e:
    print(f"❌ ไม่สามารถ import supabase: {e}")
    print("กรุณารัน: pip install supabase")
    exit(1)

def check_supabase_tables():
    """ตรวจสอบชื่อตารางใน Supabase"""
    print("🔍 ตรวจสอบชื่อตารางใน Supabase Database")
    print("=" * 50)
    
    # อ่านค่า environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ ไม่พบ SUPABASE_URL หรือ SUPABASE_KEY ใน environment")
        return
    
    print(f"📡 URL: {supabase_url}")
    print(f"🔑 Key: {supabase_key[:20]}...")
    print()
    
    try:
        # สร้าง Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ เชื่อมต่อ Supabase สำเร็จ")
        
        # วิธีที่ 1: ใช้ SQL query เพื่อดูชื่อตาราง
        print("\n📋 รายชื่อตารางทั้งหมด:")
        print("-" * 30)
        
        try:
            # Query เพื่อดูชื่อตารางใน schema public
            result = supabase.rpc('get_tables').execute()
            tables = result.data
            if tables:
                for i, table in enumerate(tables, 1):
                    print(f"{i:2d}. {table}")
            else:
                print("ไม่พบตารางใน database")
        except Exception as e:
            print(f"⚠️ ไม่สามารถใช้ RPC get_tables: {e}")
            
            # วิธีที่ 2: ลองดูตารางที่อาจมีอยู่
            print("\n🔍 ลองตรวจสอบตารางที่อาจมีอยู่:")
            possible_tables = [
                'users', 'user_profiles', 'profiles',
                'conversations', 'conversation_logs', 'logs',
                'ai_responses', 'chat_history', 'messages',
                'system_logs', 'error_logs', 'audit_logs',
                'knowledge_base', 'documents', 'files',
                'backup_logs', 'monitoring_data', 'alerts',
                'environment_data', 'system_status', 'health_checks'
            ]
            
            existing_tables = []
            for table_name in possible_tables:
                try:
                    # ลอง query ตาราง
                    result = supabase.table(table_name).select('*').limit(1).execute()
                    existing_tables.append(table_name)
                    print(f"✅ {table_name} - มีอยู่")
                except Exception as e:
                    if "does not exist" in str(e) or "42P01" in str(e):
                        print(f"❌ {table_name} - ไม่มี")
                    else:
                        print(f"⚠️ {table_name} - ไม่แน่ใจ: {str(e)[:50]}...")
            
            if existing_tables:
                print(f"\n📊 พบตารางที่ใช้งานได้: {len(existing_tables)} ตาราง")
                print("ตารางที่พบ:")
                for i, table in enumerate(existing_tables, 1):
                    print(f"  {i}. {table}")
            else:
                print("\n⚠️ ไม่พบตารางใดๆ ที่ใช้งานได้")
                print("💡 แนะนำ: สร้างตารางใหม่หรือตรวจสอบสิทธิ์การเข้าถึง")
        
        # วิธีที่ 3: ตรวจสอบข้อมูล schema
        print("\n🔧 ข้อมูล Schema:")
        print("-" * 20)
        try:
            # ลองดูข้อมูล schema
            result = supabase.rpc('get_schema_info').execute()
            print("✅ สามารถเข้าถึง schema information ได้")
        except Exception as e:
            print(f"⚠️ ไม่สามารถเข้าถึง schema info: {str(e)[:50]}...")
        
        # วิธีที่ 4: ตรวจสอบสิทธิ์การเข้าถึง
        print("\n🔐 ตรวจสอบสิทธิ์การเข้าถึง:")
        print("-" * 30)
        try:
            # ลองสร้างตารางทดสอบ (จะลบทิ้งทันที)
            test_table_name = "test_table_check"
            result = supabase.table(test_table_name).select('*').limit(1).execute()
            print("✅ มีสิทธิ์อ่านข้อมูล")
        except Exception as e:
            if "does not exist" in str(e):
                print("✅ มีสิทธิ์เข้าถึง database (ตารางไม่มีอยู่)")
            else:
                print(f"⚠️ ปัญหาสิทธิ์การเข้าถึง: {str(e)[:50]}...")
        
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ Supabase: {e}")
        print("\n🔍 ตรวจสอบ:")
        print("1. SUPABASE_URL ถูกต้องหรือไม่")
        print("2. SUPABASE_KEY ถูกต้องหรือไม่")
        print("3. การเชื่อมต่ออินเทอร์เน็ต")
        print("4. สิทธิ์การเข้าถึง database")

def create_test_table():
    """สร้างตารางทดสอบ (ถ้าต้องการ)"""
    print("\n" + "=" * 50)
    print("🔧 สร้างตารางทดสอบ")
    print("=" * 50)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # สร้างตารางทดสอบผ่าน SQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            name TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        print("✅ สร้างตาราง test_table สำเร็จ")
        
        # ทดสอบเพิ่มข้อมูล
        test_data = {'name': 'Test Entry'}
        result = supabase.table('test_table').insert(test_data).execute()
        print("✅ เพิ่มข้อมูลทดสอบสำเร็จ")
        
        # ทดสอบอ่านข้อมูล
        result = supabase.table('test_table').select('*').execute()
        print(f"✅ อ่านข้อมูลสำเร็จ: {len(result.data)} รายการ")
        
        # ลบตารางทดสอบ
        drop_table_sql = "DROP TABLE IF EXISTS test_table;"
        result = supabase.rpc('exec_sql', {'sql': drop_table_sql}).execute()
        print("✅ ลบตารางทดสอบสำเร็จ")
        
    except Exception as e:
        print(f"❌ ไม่สามารถสร้างตารางทดสอบ: {e}")

if __name__ == "__main__":
    check_supabase_tables()
    
    # ถามว่าต้องการสร้างตารางทดสอบหรือไม่
    print("\n" + "=" * 50)
    response = input("ต้องการสร้างตารางทดสอบหรือไม่? (y/n): ").lower().strip()
    if response in ['y', 'yes', 'ใช่']:
        create_test_table()
    
    print("\n✅ เสร็จสิ้นการตรวจสอบ Supabase Tables") 