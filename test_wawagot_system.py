#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบการทำงานของระบบ WAWAGOT.AI หลังจากสร้างตารางแล้ว
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv()

try:
    from supabase import create_client, Client
except ImportError as e:
    print(f"❌ ไม่สามารถ import supabase: {e}")
    print("กรุณารัน: pip install supabase")
    exit(1)

class WawagotSystemTester:
    """คลาสสำหรับทดสอบระบบ WAWAGOT.AI"""
    
    def __init__(self):
        """เริ่มต้นระบบทดสอบ"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("❌ ไม่พบ SUPABASE_URL หรือ SUPABASE_KEY ใน environment")
            exit(1)
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            print("✅ เชื่อมต่อ Supabase สำเร็จ")
        except Exception as e:
            print(f"❌ ไม่สามารถเชื่อมต่อ Supabase: {e}")
            exit(1)
        
        self.test_results = {}
    
    def test_conversation_logs(self):
        """ทดสอบตาราง conversation_logs"""
        print("\n🔍 ทดสอบตาราง conversation_logs")
        
        try:
            # สร้างข้อมูลทดสอบ
            test_data = {
                'session_id': f'test_session_{int(time.time())}',
                'user_id': 'test_user_001',
                'user_message': 'สวัสดีครับ ต้องการทดสอบระบบ',
                'ai_response': 'สวัสดีครับ! ยินดีให้บริการครับ ระบบทำงานปกติ',
                'model_used': 'gpt-4',
                'tokens_used': 75,
                'response_time_ms': 1200,
                'status': 'success',
                'metadata': {'test': True, 'timestamp': datetime.now().isoformat()}
            }
            
            # เพิ่มข้อมูล
            result = self.supabase.table('conversation_logs').insert(test_data).execute()
            
            if result.data:
                print("   ✅ เพิ่มข้อมูลสำเร็จ")
                
                # อ่านข้อมูล
                read_result = self.supabase.table('conversation_logs').select('*').eq('session_id', test_data['session_id']).execute()
                
                if read_result.data:
                    print("   ✅ อ่านข้อมูลสำเร็จ")
                    print(f"   📊 จำนวนข้อมูล: {len(read_result.data)}")
                    self.test_results['conversation_logs'] = 'success'
                else:
                    print("   ❌ ไม่สามารถอ่านข้อมูลได้")
                    self.test_results['conversation_logs'] = 'read_failed'
            else:
                print("   ❌ ไม่สามารถเพิ่มข้อมูลได้")
                self.test_results['conversation_logs'] = 'insert_failed'
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")
            self.test_results['conversation_logs'] = f'error_{str(e)[:50]}'
    
    def test_user_profiles(self):
        """ทดสอบตาราง user_profiles"""
        print("\n🔍 ทดสอบตาราง user_profiles")
        
        try:
            # สร้างข้อมูลทดสอบ
            test_data = {
                'user_id': 'test_user_001',
                'email': 'test@wawagot.ai',
                'username': 'testuser',
                'full_name': 'Test User',
                'avatar_url': 'https://example.com/avatar.jpg',
                'preferences': {
                    'theme': 'dark',
                    'language': 'th',
                    'notifications': True
                }
            }
            
            # เพิ่มข้อมูล
            result = self.supabase.table('user_profiles').insert(test_data).execute()
            
            if result.data:
                print("   ✅ เพิ่มข้อมูลสำเร็จ")
                
                # อ่านข้อมูล
                read_result = self.supabase.table('user_profiles').select('*').eq('user_id', test_data['user_id']).execute()
                
                if read_result.data:
                    print("   ✅ อ่านข้อมูลสำเร็จ")
                    print(f"   📊 ข้อมูลผู้ใช้: {read_result.data[0]['full_name']}")
                    self.test_results['user_profiles'] = 'success'
                else:
                    print("   ❌ ไม่สามารถอ่านข้อมูลได้")
                    self.test_results['user_profiles'] = 'read_failed'
            else:
                print("   ❌ ไม่สามารถเพิ่มข้อมูลได้")
                self.test_results['user_profiles'] = 'insert_failed'
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")
            self.test_results['user_profiles'] = f'error_{str(e)[:50]}'
    
    def test_system_logs(self):
        """ทดสอบตาราง system_logs"""
        print("\n🔍 ทดสอบตาราง system_logs")
        
        try:
            # สร้างข้อมูลทดสอบ
            test_data = {
                'level': 'INFO',
                'component': 'system_test',
                'message': 'ระบบทดสอบทำงานปกติ',
                'user_id': 'test_user_001',
                'session_id': f'test_session_{int(time.time())}',
                'metadata': {
                    'test': True,
                    'component': 'WawagotSystemTester',
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # เพิ่มข้อมูล
            result = self.supabase.table('system_logs').insert(test_data).execute()
            
            if result.data:
                print("   ✅ เพิ่มข้อมูลสำเร็จ")
                
                # อ่านข้อมูล
                read_result = self.supabase.table('system_logs').select('*').eq('component', 'system_test').execute()
                
                if read_result.data:
                    print("   ✅ อ่านข้อมูลสำเร็จ")
                    print(f"   📊 จำนวน log: {len(read_result.data)}")
                    self.test_results['system_logs'] = 'success'
                else:
                    print("   ❌ ไม่สามารถอ่านข้อมูลได้")
                    self.test_results['system_logs'] = 'read_failed'
            else:
                print("   ❌ ไม่สามารถเพิ่มข้อมูลได้")
                self.test_results['system_logs'] = 'insert_failed'
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")
            self.test_results['system_logs'] = f'error_{str(e)[:50]}'
    
    def test_knowledge_base(self):
        """ทดสอบตาราง knowledge_base"""
        print("\n🔍 ทดสอบตาราง knowledge_base")
        
        try:
            # สร้างข้อมูลทดสอบ
            test_data = {
                'title': 'คู่มือการทดสอบระบบ WAWAGOT.AI',
                'content': 'นี่คือคู่มือการทดสอบระบบ WAWAGOT.AI ที่ครอบคลุมการทดสอบทุกส่วนของระบบ',
                'category': 'testing',
                'tags': ['test', 'guide', 'system'],
                'source': 'system_test',
                'created_by': 'system_tester'
            }
            
            # เพิ่มข้อมูล
            result = self.supabase.table('knowledge_base').insert(test_data).execute()
            
            if result.data:
                print("   ✅ เพิ่มข้อมูลสำเร็จ")
                
                # อ่านข้อมูล
                read_result = self.supabase.table('knowledge_base').select('*').eq('category', 'testing').execute()
                
                if read_result.data:
                    print("   ✅ อ่านข้อมูลสำเร็จ")
                    print(f"   📊 จำนวนความรู้: {len(read_result.data)}")
                    self.test_results['knowledge_base'] = 'success'
                else:
                    print("   ❌ ไม่สามารถอ่านข้อมูลได้")
                    self.test_results['knowledge_base'] = 'read_failed'
            else:
                print("   ❌ ไม่สามารถเพิ่มข้อมูลได้")
                self.test_results['knowledge_base'] = 'insert_failed'
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")
            self.test_results['knowledge_base'] = f'error_{str(e)[:50]}'
    
    def test_system_config(self):
        """ทดสอบตาราง system_config"""
        print("\n🔍 ทดสอบตาราง system_config")
        
        try:
            # สร้างข้อมูลทดสอบ
            test_data = {
                'config_key': 'test_mode',
                'config_value': 'true',
                'config_type': 'boolean',
                'description': 'โหมดทดสอบระบบ',
                'updated_by': 'system_tester'
            }
            
            # เพิ่มข้อมูล
            result = self.supabase.table('system_config').insert(test_data).execute()
            
            if result.data:
                print("   ✅ เพิ่มข้อมูลสำเร็จ")
                
                # อ่านข้อมูล
                read_result = self.supabase.table('system_config').select('*').eq('config_key', 'test_mode').execute()
                
                if read_result.data:
                    print("   ✅ อ่านข้อมูลสำเร็จ")
                    print(f"   📊 ค่า config: {read_result.data[0]['config_value']}")
                    self.test_results['system_config'] = 'success'
                else:
                    print("   ❌ ไม่สามารถอ่านข้อมูลได้")
                    self.test_results['system_config'] = 'read_failed'
            else:
                print("   ❌ ไม่สามารถเพิ่มข้อมูลได้")
                self.test_results['system_config'] = 'insert_failed'
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")
            self.test_results['system_config'] = f'error_{str(e)[:50]}'
    
    def test_health_checks(self):
        """ทดสอบตาราง health_checks"""
        print("\n🔍 ทดสอบตาราง health_checks")
        
        try:
            # สร้างข้อมูลทดสอบ
            test_data = {
                'check_type': 'system_test',
                'status': 'success',
                'response_time_ms': 100,
                'details': {
                    'test': True,
                    'component': 'WawagotSystemTester',
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # เพิ่มข้อมูล
            result = self.supabase.table('health_checks').insert(test_data).execute()
            
            if result.data:
                print("   ✅ เพิ่มข้อมูลสำเร็จ")
                
                # อ่านข้อมูล
                read_result = self.supabase.table('health_checks').select('*').eq('check_type', 'system_test').execute()
                
                if read_result.data:
                    print("   ✅ อ่านข้อมูลสำเร็จ")
                    print(f"   📊 สถานะ: {read_result.data[0]['status']}")
                    self.test_results['health_checks'] = 'success'
                else:
                    print("   ❌ ไม่สามารถอ่านข้อมูลได้")
                    self.test_results['health_checks'] = 'read_failed'
            else:
                print("   ❌ ไม่สามารถเพิ่มข้อมูลได้")
                self.test_results['health_checks'] = 'insert_failed'
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")
            self.test_results['health_checks'] = f'error_{str(e)[:50]}'
    
    def test_views(self):
        """ทดสอบ Views"""
        print("\n🔍 ทดสอบ Views")
        
        try:
            # ทดสอบ system_summary view
            summary_result = self.supabase.table('system_summary').select('*').execute()
            
            if summary_result.data:
                print("   ✅ system_summary view ทำงานได้")
                summary = summary_result.data[0]
                print(f"   📊 สรุประบบ:")
                print(f"      - บทสนทนา: {summary.get('total_conversations', 0)}")
                print(f"      - ผู้ใช้: {summary.get('active_users', 0)}")
                print(f"      - ข้อผิดพลาด 24h: {summary.get('errors_last_24h', 0)}")
                print(f"      - การแจ้งเตือน: {summary.get('active_alerts', 0)}")
                print(f"      - สำรองข้อมูล 7d: {summary.get('successful_backups_7d', 0)}")
                self.test_results['views'] = 'success'
            else:
                print("   ❌ system_summary view ไม่ทำงาน")
                self.test_results['views'] = 'failed'
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")
            self.test_results['views'] = f'error_{str(e)[:50]}'
    
    def run_all_tests(self):
        """รันการทดสอบทั้งหมด"""
        print("🚀 เริ่มทดสอบระบบ WAWAGOT.AI")
        print("=" * 60)
        
        # ทดสอบตารางหลัก
        self.test_conversation_logs()
        self.test_user_profiles()
        self.test_system_logs()
        self.test_knowledge_base()
        self.test_system_config()
        self.test_health_checks()
        
        # ทดสอบ Views
        self.test_views()
        
        # สรุปผล
        self.print_summary()
    
    def print_summary(self):
        """พิมพ์สรุปผลการทดสอบ"""
        print("\n" + "=" * 60)
        print("📊 สรุปผลการทดสอบระบบ WAWAGOT.AI")
        print("=" * 60)
        
        success_count = sum(1 for result in self.test_results.values() if result == 'success')
        total_count = len(self.test_results)
        
        print(f"\n✅ สำเร็จ: {success_count}/{total_count} การทดสอบ")
        print(f"❌ ล้มเหลว: {total_count - success_count}/{total_count} การทดสอบ")
        
        if success_count > 0:
            print(f"\n✅ การทดสอบที่สำเร็จ:")
            for test, result in self.test_results.items():
                if result == 'success':
                    print(f"   - {test}")
        
        if total_count - success_count > 0:
            print(f"\n❌ การทดสอบที่มีปัญหา:")
            for test, result in self.test_results.items():
                if result != 'success':
                    print(f"   - {test}: {result}")
        
        # บันทึกผลการทดสอบ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': self.test_results,
                'summary': {
                    'total_tests': total_count,
                    'success_count': success_count,
                    'failure_count': total_count - success_count,
                    'success_rate': f"{(success_count/total_count)*100:.1f}%"
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 บันทึกผลการทดสอบในไฟล์: {filename}")
        
        if success_count == total_count:
            print("\n🎉 ระบบ WAWAGOT.AI ทำงานปกติทุกส่วน!")
        else:
            print(f"\n⚠️ ระบบมีปัญหา {total_count - success_count} ส่วน ต้องแก้ไข")

if __name__ == "__main__":
    tester = WawagotSystemTester()
    tester.run_all_tests() 