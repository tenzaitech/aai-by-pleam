#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI Integration Manager System
ระบบเชื่อมต่อระบบทั้งหมดเข้าด้วยกันแบบยืดหยุ่น
"""

import os
import json
import logging
import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import sqlite3

# Import ระบบย่อย
import sys
sys.path.append('conversation_logs/auto_logger')
sys.path.append('conversation_logs/ai_filter')
sys.path.append('conversation_logs/conversation_manager')
sys.path.append('conversation_logs/auto_backup')

try:
    from auto_logger import AutoLogger
    from ai_filter import AIFilter
    from conversation_manager import ConversationManager
    from auto_backup import AutoBackup
except ImportError as e:
    print(f"ไม่สามารถ import ระบบย่อย: {e}")

class IntegrationManager:
    """ระบบเชื่อมต่อระบบทั้งหมดเข้าด้วยกัน"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.db_path = self.config.get('integration_database_path', 'integration.db')
        self.init_database()
        
        # ระบบย่อย
        self.auto_logger = None
        self.ai_filter = None
        self.conversation_manager = None
        self.auto_backup = None
        
        # สถานะการทำงาน
        self.running = False
        self.integration_thread = None
        
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """โหลดการตั้งค่า"""
        default_config = {
            'log_level': 'INFO',
            'integration_database_path': 'integration.db',
            'auto_start_services': True,
            'real_time_integration': True,
            'sync_interval': 30,  # 30 วินาที
            'error_retry_attempts': 3,
            'health_check_interval': 300,  # 5 นาที
            'services': {
                'auto_logger': True,
                'ai_filter': True,
                'conversation_manager': True,
                'auto_backup': True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logging.error(f"ไม่สามารถโหลด config: {e}")
                
        return default_config
    
    def setup_logging(self):
        """ตั้งค่าระบบ logging"""
        log_dir = Path('conversation_logs/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.config['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'integration_manager.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('IntegrationManager')
        
    def init_database(self):
        """สร้างฐานข้อมูลสำหรับ Integration Manager"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ตารางการเชื่อมต่อระบบ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    system_name TEXT NOT NULL,
                    status TEXT DEFAULT 'disconnected',
                    last_connected DATETIME,
                    connection_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ตารางการทำงานร่วมกัน
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS integration_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    source_system TEXT,
                    target_system TEXT,
                    event_data TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processed_at DATETIME
                )
            ''')
            
            # ตารางสถิติการทำงาน
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS integration_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    total_events INTEGER DEFAULT 0,
                    successful_events INTEGER DEFAULT 0,
                    failed_events INTEGER DEFAULT 0,
                    avg_processing_time REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("สร้างฐานข้อมูล Integration Manager สำเร็จ")
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถสร้างฐานข้อมูล: {e}")
    
    def initialize_services(self):
        """เริ่มต้นระบบย่อยทั้งหมด"""
        try:
            self.logger.info("เริ่มต้นระบบย่อย...")
            
            # เริ่มต้น AutoLogger
            if self.config['services']['auto_logger']:
                self.auto_logger = AutoLogger()
                self.auto_logger.start_background_logging()
                self._update_system_status('auto_logger', 'connected')
                self.logger.info("เริ่มต้น AutoLogger สำเร็จ")
            
            # เริ่มต้น AIFilter
            if self.config['services']['ai_filter']:
                self.ai_filter = AIFilter()
                self.ai_filter.setup_default_categories()
                self._update_system_status('ai_filter', 'connected')
                self.logger.info("เริ่มต้น AIFilter สำเร็จ")
            
            # เริ่มต้น ConversationManager
            if self.config['services']['conversation_manager']:
                self.conversation_manager = ConversationManager()
                self._update_system_status('conversation_manager', 'connected')
                self.logger.info("เริ่มต้น ConversationManager สำเร็จ")
            
            # เริ่มต้น AutoBackup
            if self.config['services']['auto_backup']:
                self.auto_backup = AutoBackup()
                self.auto_backup.start_background_backup()
                self._update_system_status('auto_backup', 'connected')
                self.logger.info("เริ่มต้น AutoBackup สำเร็จ")
            
            self.logger.info("เริ่มต้นระบบย่อยทั้งหมดสำเร็จ")
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถเริ่มต้นระบบย่อย: {e}")
            return False
    
    def start_integration(self):
        """เริ่มการเชื่อมต่อระบบ"""
        if self.running:
            self.logger.warning("ระบบเชื่อมต่อกำลังทำงานอยู่แล้ว")
            return False
        
        try:
            # เริ่มต้นระบบย่อย
            if not self.initialize_services():
                return False
            
            # เริ่มการทำงานแบบ background
            self.running = True
            self.integration_thread = threading.Thread(target=self._integration_worker, daemon=True)
            self.integration_thread.start()
            
            self.logger.info("เริ่มระบบเชื่อมต่อสำเร็จ")
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถเริ่มระบบเชื่อมต่อ: {e}")
            return False
    
    def stop_integration(self):
        """หยุดการเชื่อมต่อระบบ"""
        self.running = False
        
        try:
            # หยุดระบบย่อย
            if self.auto_logger:
                self.auto_logger.stop_background_logging()
            
            if self.auto_backup:
                self.auto_backup.stop_background_backup()
            
            # รอให้ thread จบการทำงาน
            if self.integration_thread:
                self.integration_thread.join()
            
            self.logger.info("หยุดระบบเชื่อมต่อสำเร็จ")
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถหยุดระบบเชื่อมต่อ: {e}")
    
    def _integration_worker(self):
        """worker สำหรับการเชื่อมต่อระบบ"""
        while self.running:
            try:
                # ตรวจสอบสถานะระบบ
                self._check_system_health()
                
                # ประมวลผล events ที่ค้างอยู่
                self._process_pending_events()
                
                # อัปเดตสถิติ
                self._update_integration_stats()
                
                time.sleep(self.config['sync_interval'])
                
            except Exception as e:
                self.logger.error(f"ข้อผิดพลาดใน integration worker: {e}")
                time.sleep(self.config['sync_interval'])
    
    def _check_system_health(self):
        """ตรวจสอบสถานะระบบ"""
        try:
            systems = [
                ('auto_logger', self.auto_logger),
                ('ai_filter', self.ai_filter),
                ('conversation_manager', self.conversation_manager),
                ('auto_backup', self.auto_backup)
            ]
            
            for system_name, system_obj in systems:
                if system_obj:
                    status = 'connected' if hasattr(system_obj, 'running') and system_obj.running else 'connected'
                    self._update_system_status(system_name, status)
                else:
                    self._update_system_status(system_name, 'disconnected')
                    
        except Exception as e:
            self.logger.error(f"ไม่สามารถตรวจสอบสถานะระบบ: {e}")
    
    def _process_pending_events(self):
        """ประมวลผล events ที่ค้างอยู่"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM integration_events 
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT 10
            ''')
            
            events = cursor.fetchall()
            
            for event in events:
                event_id, event_type, source_system, target_system, event_data, status, created_at, processed_at = event
                
                try:
                    # ประมวลผล event
                    success = self._process_event(event_type, source_system, target_system, event_data)
                    
                    # อัปเดตสถานะ
                    new_status = 'completed' if success else 'failed'
                    cursor.execute('''
                        UPDATE integration_events 
                        SET status = ?, processed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (new_status, event_id))
                    
                except Exception as e:
                    self.logger.error(f"ไม่สามารถประมวลผล event {event_id}: {e}")
                    cursor.execute('''
                        UPDATE integration_events 
                        SET status = 'failed', processed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (event_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถประมวลผล events: {e}")
    
    def _process_event(self, event_type: str, source_system: str, 
                      target_system: str, event_data: str) -> bool:
        """ประมวลผล event เดียว"""
        try:
            data = json.loads(event_data) if event_data else {}
            
            if event_type == 'conversation_logged':
                # การสนทนาถูกบันทึก - ส่งไปยัง AI Filter
                if self.ai_filter and target_system == 'ai_filter':
                    conversation_text = data.get('user_message', '') + ' ' + data.get('ai_response', '')
                    self.ai_filter.filter_conversation(conversation_text, data.get('conversation_id'))
                    return True
            
            elif event_type == 'conversation_filtered':
                # การสนทนาถูกกรอง - ส่งไปยัง Conversation Manager
                if self.conversation_manager and target_system == 'conversation_manager':
                    session_id = data.get('session_id')
                    if session_id:
                        self.conversation_manager.update_session_activity(session_id)
                    return True
            
            elif event_type == 'backup_created':
                # สร้าง backup - บันทึกข้อมูล
                if self.conversation_manager and target_system == 'conversation_manager':
                    # บันทึกข้อมูล backup
                    return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถประมวลผล event {event_type}: {e}")
            return False
    
    def log_conversation(self, session_id: str, user_message: str, 
                        ai_response: str, context: str = None, 
                        metadata: Dict[str, Any] = None) -> bool:
        """บันทึกการสนทนาผ่านระบบเชื่อมต่อ"""
        try:
            # บันทึกผ่าน AutoLogger
            if self.auto_logger:
                success = self.auto_logger.log_conversation(
                    session_id, user_message, ai_response, context, metadata
                )
                
                if success:
                    # สร้าง event สำหรับ AI Filter
                    self._create_integration_event(
                        'conversation_logged',
                        'auto_logger',
                        'ai_filter',
                        {
                            'session_id': session_id,
                            'user_message': user_message,
                            'ai_response': ai_response,
                            'conversation_id': metadata.get('conversation_id') if metadata else None
                        }
                    )
                    
                    # อัปเดต session ใน Conversation Manager
                    if self.conversation_manager:
                        self.conversation_manager.update_session_activity(session_id)
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถบันทึกการสนทนา: {e}")
            return False
    
    def search_conversations(self, query: str, session_id: str = None) -> List[Dict[str, Any]]:
        """ค้นหาการสนทนาผ่านระบบเชื่อมต่อ"""
        try:
            results = []
            
            # ค้นหาจาก Conversation Manager
            if self.conversation_manager:
                manager_results = self.conversation_manager.search_conversations(query, session_id)
                results.extend(manager_results)
            
            # ค้นหาจาก AutoLogger
            if self.auto_logger:
                logger_results = self.auto_logger.get_conversation_history(session_id)
                # กรองผลลัพธ์ตาม query
                filtered_results = [
                    conv for conv in logger_results
                    if query.lower() in conv.get('user_message', '').lower() or
                       query.lower() in conv.get('ai_response', '').lower()
                ]
                results.extend(filtered_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถค้นหาการสนทนา: {e}")
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """ดึงสถานะระบบทั้งหมด"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM system_connections')
            rows = cursor.fetchall()
            
            status = {}
            for row in rows:
                status[row[1]] = {
                    'status': row[2],
                    'last_connected': row[3],
                    'connection_count': row[4],
                    'error_count': row[5]
                }
            
            conn.close()
            return status
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงสถานะระบบ: {e}")
            return {}
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """ดึงสถิติการเชื่อมต่อ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # สถิติ events
            cursor.execute('''
                SELECT status, COUNT(*) FROM integration_events 
                WHERE created_at >= datetime('now', '-7 days')
                GROUP BY status
            ''')
            event_stats = dict(cursor.fetchall())
            
            # สถิติการทำงาน
            cursor.execute('''
                SELECT * FROM integration_stats 
                WHERE date >= date('now', '-7 days')
                ORDER BY date DESC
            ''')
            rows = cursor.fetchall()
            
            total_events = sum(event_stats.values())
            successful_events = event_stats.get('completed', 0)
            failed_events = event_stats.get('failed', 0)
            
            conn.close()
            
            return {
                'event_stats': event_stats,
                'total_events': total_events,
                'successful_events': successful_events,
                'failed_events': failed_events,
                'success_rate': (successful_events / total_events * 100) if total_events > 0 else 0,
                'daily_stats': [
                    {
                        'date': row[1],
                        'total_events': row[2],
                        'successful_events': row[3],
                        'failed_events': row[4],
                        'avg_processing_time': row[5]
                    }
                    for row in rows
                ]
            }
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงสถิติการเชื่อมต่อ: {e}")
            return {}
    
    def _update_system_status(self, system_name: str, status: str):
        """อัปเดตสถานะระบบ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO system_connections 
                (system_name, status, last_connected, connection_count, error_count)
                VALUES (?, ?, CURRENT_TIMESTAMP, 
                       COALESCE((SELECT connection_count FROM system_connections WHERE system_name = ?), 0) + 1,
                       COALESCE((SELECT error_count FROM system_connections WHERE system_name = ?), 0))
            ''', (system_name, status, system_name, system_name))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถอัปเดตสถานะระบบ: {e}")
    
    def _create_integration_event(self, event_type: str, source_system: str, 
                                target_system: str, event_data: Dict[str, Any]):
        """สร้าง integration event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO integration_events 
                (event_type, source_system, target_system, event_data)
                VALUES (?, ?, ?, ?)
            ''', (event_type, source_system, target_system, json.dumps(event_data)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถสร้าง integration event: {e}")
    
    def _update_integration_stats(self):
        """อัปเดตสถิติการเชื่อมต่อ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # นับ events วันนี้
            cursor.execute('''
                SELECT COUNT(*), 
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END)
                FROM integration_events 
                WHERE DATE(created_at) = DATE('now')
            ''')
            
            row = cursor.fetchone()
            total_events = row[0] or 0
            successful_events = row[1] or 0
            failed_events = row[2] or 0
            
            # อัปเดตหรือเพิ่มสถิติวันนี้
            cursor.execute('''
                INSERT OR REPLACE INTO integration_stats 
                (date, total_events, successful_events, failed_events)
                VALUES (DATE('now'), ?, ?, ?)
            ''', (total_events, successful_events, failed_events))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถอัปเดตสถิติการเชื่อมต่อ: {e}")

if __name__ == "__main__":
    # ทดสอบระบบ
    integration = IntegrationManager()
    
    # เริ่มระบบเชื่อมต่อ
    if integration.start_integration():
        print("เริ่มระบบเชื่อมต่อสำเร็จ!")
        
        # ทดสอบบันทึกการสนทนา
        integration.log_conversation(
            session_id="test_session_001",
            user_message="สวัสดีครับ",
            ai_response="สวัสดีครับ! มีอะไรให้ช่วยเหลือไหมครับ?",
            metadata={"source": "test"}
        )
        
        # แสดงสถานะระบบ
        status = integration.get_system_status()
        print("\nสถานะระบบ:")
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        # แสดงสถิติ
        stats = integration.get_integration_statistics()
        print("\nสถิติการเชื่อมต่อ:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        input("กด Enter เพื่อหยุด...")
        integration.stop_integration()
    else:
        print("ไม่สามารถเริ่มระบบเชื่อมต่อได้") 