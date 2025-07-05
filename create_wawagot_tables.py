#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สร้างตารางที่จำเป็นสำหรับระบบ WAWAGOT.AI ใน Supabase
"""

import os
from dotenv import load_dotenv
import json
from datetime import datetime

# โหลด environment variables
load_dotenv()

try:
    from supabase import create_client, Client
except ImportError as e:
    print(f"❌ ไม่สามารถ import supabase: {e}")
    print("กรุณารัน: pip install supabase")
    exit(1)

def create_wawagot_tables():
    """สร้างตารางที่จำเป็นสำหรับระบบ WAWAGOT.AI"""
    print("🏗️ สร้างตารางที่จำเป็นสำหรับระบบ WAWAGOT.AI")
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
    
    try:
        # สร้าง Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ เชื่อมต่อ Supabase สำเร็จ")
        
        # กำหนด SQL สำหรับสร้างตาราง
        tables_sql = {
            # 1. ตารางบันทึกบทสนทนา
            'conversation_logs': """
            CREATE TABLE IF NOT EXISTS conversation_logs (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255),
                user_message TEXT NOT NULL,
                ai_response TEXT,
                timestamp TIMESTAMP DEFAULT NOW(),
                model_used VARCHAR(100),
                tokens_used INTEGER,
                response_time_ms INTEGER,
                status VARCHAR(50) DEFAULT 'success',
                metadata JSONB
            );
            """,
            
            # 2. ตารางข้อมูลผู้ใช้
            'user_profiles': """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255),
                username VARCHAR(100),
                full_name VARCHAR(200),
                avatar_url TEXT,
                preferences JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            );
            """,
            
            # 3. ตารางบันทึกระบบ
            'system_logs': """
            CREATE TABLE IF NOT EXISTS system_logs (
                id SERIAL PRIMARY KEY,
                level VARCHAR(20) NOT NULL,
                component VARCHAR(100),
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW(),
                user_id VARCHAR(255),
                session_id VARCHAR(255),
                metadata JSONB,
                stack_trace TEXT
            );
            """,
            
            # 4. ตารางฐานความรู้
            'knowledge_base': """
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                category VARCHAR(100),
                tags TEXT[],
                source VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                created_by VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                metadata JSONB
            );
            """,
            
            # 5. ตารางบันทึกการสำรองข้อมูล
            'backup_logs': """
            CREATE TABLE IF NOT EXISTS backup_logs (
                id SERIAL PRIMARY KEY,
                backup_type VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                file_path TEXT,
                file_size BIGINT,
                start_time TIMESTAMP DEFAULT NOW(),
                end_time TIMESTAMP,
                duration_seconds INTEGER,
                records_backed_up INTEGER,
                error_message TEXT,
                metadata JSONB
            );
            """,
            
            # 6. ตารางการตรวจสอบระบบ
            'health_checks': """
            CREATE TABLE IF NOT EXISTS health_checks (
                id SERIAL PRIMARY KEY,
                check_type VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL,
                response_time_ms INTEGER,
                timestamp TIMESTAMP DEFAULT NOW(),
                details JSONB,
                error_message TEXT
            );
            """,
            
            # 7. ตารางการแจ้งเตือน
            'alerts': """
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                alert_type VARCHAR(100) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW(),
                is_resolved BOOLEAN DEFAULT FALSE,
                resolved_at TIMESTAMP,
                resolved_by VARCHAR(255),
                metadata JSONB
            );
            """,
            
            # 8. ตารางข้อมูลสภาพแวดล้อม
            'environment_data': """
            CREATE TABLE IF NOT EXISTS environment_data (
                id SERIAL PRIMARY KEY,
                component VARCHAR(100) NOT NULL,
                metric_name VARCHAR(100) NOT NULL,
                metric_value TEXT NOT NULL,
                unit VARCHAR(50),
                timestamp TIMESTAMP DEFAULT NOW(),
                metadata JSONB
            );
            """,
            
            # 9. ตารางการจัดการไฟล์
            'file_management': """
            CREATE TABLE IF NOT EXISTS file_management (
                id SERIAL PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                file_path TEXT NOT NULL,
                file_size BIGINT,
                file_type VARCHAR(100),
                mime_type VARCHAR(100),
                uploaded_by VARCHAR(255),
                uploaded_at TIMESTAMP DEFAULT NOW(),
                is_processed BOOLEAN DEFAULT FALSE,
                processing_status VARCHAR(50),
                metadata JSONB
            );
            """,
            
            # 10. ตารางการตั้งค่าระบบ
            'system_config': """
            CREATE TABLE IF NOT EXISTS system_config (
                id SERIAL PRIMARY KEY,
                config_key VARCHAR(255) UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                config_type VARCHAR(50) DEFAULT 'string',
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                updated_by VARCHAR(255)
            );
            """
        }
        
        # สร้างตารางทีละตัว
        created_tables = []
        failed_tables = []
        
        for table_name, sql in tables_sql.items():
            try:
                print(f"🔨 สร้างตาราง: {table_name}")
                
                # ใช้ raw SQL query ผ่าน REST API
                # เนื่องจาก Supabase Python client ไม่รองรับ DDL โดยตรง
                # เราจะใช้วิธีอื่นในการสร้างตาราง
                
                # สำหรับตอนนี้ เราจะสร้างตารางผ่านการทดสอบการเชื่อมต่อ
                # และให้คำแนะนำในการสร้างผ่าน Supabase Dashboard
                
                print(f"   ⚠️ ต้องสร้างผ่าน Supabase Dashboard")
                print(f"   📝 SQL: {sql.strip()[:100]}...")
                
                # ทดสอบว่าสามารถเข้าถึงตารางได้หรือไม่
                try:
                    result = supabase.table(table_name).select('*').limit(1).execute()
                    print(f"   ✅ ตาราง {table_name} มีอยู่แล้ว")
                    created_tables.append(table_name)
                except Exception as e:
                    if "does not exist" in str(e) or "42P01" in str(e):
                        print(f"   ❌ ตาราง {table_name} ยังไม่มี")
                        failed_tables.append(table_name)
                    else:
                        print(f"   ⚠️ ไม่แน่ใจ: {str(e)[:50]}...")
                        failed_tables.append(table_name)
                
            except Exception as e:
                print(f"   ❌ ไม่สามารถสร้างตาราง {table_name}: {e}")
                failed_tables.append(table_name)
        
        # สรุปผล
        print("\n" + "=" * 60)
        print("📊 สรุปผลการสร้างตาราง")
        print("=" * 60)
        
        if created_tables:
            print(f"\n✅ ตารางที่มีอยู่แล้ว ({len(created_tables)} ตาราง):")
            for table in created_tables:
                print(f"   - {table}")
        
        if failed_tables:
            print(f"\n❌ ตารางที่ต้องสร้าง ({len(failed_tables)} ตาราง):")
            for table in failed_tables:
                print(f"   - {table}")
        
        print(f"\n💡 แนะนำ: สร้างตารางผ่าน Supabase Dashboard")
        print("   1. ไปที่ https://supabase.com/dashboard")
        print("   2. เลือกโปรเจค TENZAITECH-DATABASE")
        print("   3. ไปที่ SQL Editor")
        print("   4. รัน SQL ที่แสดงด้านล่าง")
        
        # แสดง SQL สำหรับสร้างตาราง
        print("\n" + "=" * 60)
        print("📝 SQL สำหรับสร้างตารางทั้งหมด")
        print("=" * 60)
        
        for table_name, sql in tables_sql.items():
            if table_name in failed_tables:
                print(f"\n-- สร้างตาราง: {table_name}")
                print(sql)
        
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ Supabase: {e}")

def insert_sample_data():
    """เพิ่มข้อมูลตัวอย่าง"""
    print("\n" + "=" * 60)
    print("📝 เพิ่มข้อมูลตัวอย่าง")
    print("=" * 60)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # ข้อมูลตัวอย่างสำหรับ system_config
        sample_configs = [
            {
                'config_key': 'system_name',
                'config_value': 'WAWAGOT.AI',
                'config_type': 'string',
                'description': 'ชื่อระบบ'
            },
            {
                'config_key': 'version',
                'config_value': '2.0.0',
                'config_type': 'string',
                'description': 'เวอร์ชันระบบ'
            },
            {
                'config_key': 'max_conversation_length',
                'config_value': '1000',
                'config_type': 'integer',
                'description': 'ความยาวสูงสุดของบทสนทนา'
            },
            {
                'config_key': 'ai_model',
                'config_value': 'gpt-4',
                'config_type': 'string',
                'description': 'โมเดล AI ที่ใช้'
            }
        ]
        
        for config in sample_configs:
            try:
                result = supabase.table('system_config').insert(config).execute()
                print(f"✅ เพิ่ม config: {config['config_key']}")
            except Exception as e:
                print(f"❌ ไม่สามารถเพิ่ม config {config['config_key']}: {e}")
        
        # ข้อมูลตัวอย่างสำหรับ knowledge_base
        sample_knowledge = [
            {
                'title': 'การใช้งานระบบ WAWAGOT.AI',
                'content': 'WAWAGOT.AI เป็นระบบ AI ที่ช่วยในการจัดการข้อมูลและบทสนทนา',
                'category': 'system',
                'tags': ['ai', 'system', 'guide'],
                'source': 'system',
                'created_by': 'system'
            }
        ]
        
        for knowledge in sample_knowledge:
            try:
                result = supabase.table('knowledge_base').insert(knowledge).execute()
                print(f"✅ เพิ่ม knowledge: {knowledge['title']}")
            except Exception as e:
                print(f"❌ ไม่สามารถเพิ่ม knowledge {knowledge['title']}: {e}")
        
    except Exception as e:
        print(f"❌ ไม่สามารถเพิ่มข้อมูลตัวอย่าง: {e}")

if __name__ == "__main__":
    create_wawagot_tables()
    
    # ถามว่าต้องการเพิ่มข้อมูลตัวอย่างหรือไม่
    print("\n" + "=" * 60)
    response = input("ต้องการเพิ่มข้อมูลตัวอย่างหรือไม่? (y/n): ").lower().strip()
    if response in ['y', 'yes', 'ใช่']:
        insert_sample_data()
    
    print("\n✅ เสร็จสิ้นการสร้างตารางสำหรับระบบ WAWAGOT.AI") 