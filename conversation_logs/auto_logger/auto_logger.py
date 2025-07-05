#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI Auto Logger System
ระบบบันทึกการสนทนาอัตโนมัติแบบยืดหยุ่น
"""

import os
import json
import time
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import sqlite3
import hashlib
import base64

class AutoLogger:
    """ระบบบันทึกการสนทนาอัตโนมัติ"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.db_path = self.config.get('database_path', 'conversation_logs.db')
        self.init_database()
        self.running = False
        self.log_thread = None
        
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """โหลดการตั้งค่าจากไฟล์"""
        default_config = {
            'log_level': 'INFO',
            'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'database_path': 'conversation_logs.db',
            'backup_interval': 3600,  # 1 ชั่วโมง
            'max_log_size': 1000000,  # 1MB
            'encryption_enabled': True,
            'auto_cleanup': True,
            'cleanup_days': 30
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
            format=self.config['log_format'],
            handlers=[
                logging.FileHandler(log_dir / 'auto_logger.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AutoLogger')
        
    def init_database(self):
        """สร้างฐานข้อมูล SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ตารางการสนทนา
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_message TEXT,
                    ai_response TEXT,
                    context TEXT,
                    metadata TEXT,
                    encrypted INTEGER DEFAULT 0
                )
            ''')
            
            # ตาราง metadata
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    key TEXT NOT NULL,
                    value TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')
            
            # ตารางสถิติ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    total_conversations INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    avg_response_time REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("สร้างฐานข้อมูลสำเร็จ")
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถสร้างฐานข้อมูล: {e}")
            
    def encrypt_data(self, data: str) -> str:
        """เข้ารหัสข้อมูล"""
        if not self.config['encryption_enabled']:
            return data
            
        try:
            # ใช้ base64 encoding แบบง่าย (ในระบบจริงควรใช้ encryption ที่แข็งแกร่งกว่า)
            encoded = base64.b64encode(data.encode('utf-8'))
            return encoded.decode('utf-8')
        except Exception as e:
            self.logger.error(f"ไม่สามารถเข้ารหัสข้อมูล: {e}")
            return data
            
    def decrypt_data(self, encrypted_data: str) -> str:
        """ถอดรหัสข้อมูล"""
        if not self.config['encryption_enabled']:
            return encrypted_data
            
        try:
            decoded = base64.b64decode(encrypted_data.encode('utf-8'))
            return decoded.decode('utf-8')
        except Exception as e:
            self.logger.error(f"ไม่สามารถถอดรหัสข้อมูล: {e}")
            return encrypted_data
    
    def log_conversation(self, session_id: str, user_message: str, 
                        ai_response: str, context: str = None, 
                        metadata: Dict[str, Any] = None) -> bool:
        """บันทึกการสนทนา"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # เข้ารหัสข้อมูล
            encrypted_user = self.encrypt_data(user_message)
            encrypted_ai = self.encrypt_data(ai_response)
            encrypted_context = self.encrypt_data(context) if context else None
            encrypted_metadata = self.encrypt_data(json.dumps(metadata)) if metadata else None
            
            cursor.execute('''
                INSERT INTO conversations 
                (session_id, user_message, ai_response, context, metadata, encrypted)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, encrypted_user, encrypted_ai, encrypted_context, 
                  encrypted_metadata, 1 if self.config['encryption_enabled'] else 0))
            
            conversation_id = cursor.lastrowid
            
            # บันทึก metadata
            if metadata:
                for key, value in metadata.items():
                    cursor.execute('''
                        INSERT INTO metadata (conversation_id, key, value)
                        VALUES (?, ?, ?)
                    ''', (conversation_id, key, str(value)))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"บันทึกการสนทนาสำเร็จ: Session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถบันทึกการสนทนา: {e}")
            return False
    
    def get_conversation_history(self, session_id: str = None, 
                                limit: int = 100) -> List[Dict[str, Any]]:
        """ดึงประวัติการสนทนา"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute('''
                    SELECT * FROM conversations 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (session_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM conversations 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conversations = []
            
            for row in rows:
                conversation = {
                    'id': row[0],
                    'session_id': row[1],
                    'timestamp': row[2],
                    'user_message': self.decrypt_data(row[3]) if row[6] else row[3],
                    'ai_response': self.decrypt_data(row[4]) if row[6] else row[4],
                    'context': self.decrypt_data(row[5]) if row[5] and row[6] else row[5],
                    'metadata': json.loads(self.decrypt_data(row[6])) if row[6] and row[6] else None
                }
                conversations.append(conversation)
            
            conn.close()
            return conversations
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงประวัติการสนทนา: {e}")
            return []
    
    def start_background_logging(self):
        """เริ่มการบันทึกแบบ background"""
        if self.running:
            self.logger.warning("ระบบบันทึกกำลังทำงานอยู่แล้ว")
            return
            
        self.running = True
        self.log_thread = threading.Thread(target=self._background_worker, daemon=True)
        self.log_thread.start()
        self.logger.info("เริ่มระบบบันทึกแบบ background")
    
    def stop_background_logging(self):
        """หยุดการบันทึกแบบ background"""
        self.running = False
        if self.log_thread:
            self.log_thread.join()
        self.logger.info("หยุดระบบบันทึกแบบ background")
    
    def _background_worker(self):
        """worker สำหรับ background processing"""
        while self.running:
            try:
                # ทำความสะอาดข้อมูลเก่า
                if self.config['auto_cleanup']:
                    self._cleanup_old_data()
                
                # อัปเดตสถิติ
                self._update_statistics()
                
                time.sleep(60)  # ตรวจสอบทุก 1 นาที
                
            except Exception as e:
                self.logger.error(f"ข้อผิดพลาดใน background worker: {e}")
                time.sleep(60)
    
    def _cleanup_old_data(self):
        """ทำความสะอาดข้อมูลเก่า"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ลบข้อมูลเก่ากว่า 30 วัน
            cleanup_days = self.config.get('cleanup_days', 30)
            cursor.execute('''
                DELETE FROM conversations 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(cleanup_days))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                self.logger.info(f"ทำความสะอาดข้อมูลเก่า {deleted_count} รายการ")
                
        except Exception as e:
            self.logger.error(f"ไม่สามารถทำความสะอาดข้อมูล: {e}")
    
    def _update_statistics(self):
        """อัปเดตสถิติ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # นับจำนวนการสนทนาวันนี้
            cursor.execute('''
                SELECT COUNT(*) FROM conversations 
                WHERE DATE(timestamp) = DATE('now')
            ''')
            today_conversations = cursor.fetchone()[0]
            
            # นับจำนวนข้อความวันนี้
            cursor.execute('''
                SELECT COUNT(*) FROM conversations 
                WHERE DATE(timestamp) = DATE('now') 
                AND user_message IS NOT NULL
            ''')
            today_messages = cursor.fetchone()[0]
            
            # อัปเดตหรือเพิ่มสถิติวันนี้
            cursor.execute('''
                INSERT OR REPLACE INTO statistics 
                (date, total_conversations, total_messages)
                VALUES (DATE('now'), ?, ?)
            ''', (today_conversations, today_messages))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถอัปเดตสถิติ: {e}")
    
    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """ดึงสถิติ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM statistics 
                WHERE date >= DATE('now', '-{} days')
                ORDER BY date DESC
            '''.format(days))
            
            rows = cursor.fetchall()
            stats = {
                'total_conversations': sum(row[2] for row in rows),
                'total_messages': sum(row[3] for row in rows),
                'daily_stats': []
            }
            
            for row in rows:
                stats['daily_stats'].append({
                    'date': row[1],
                    'conversations': row[2],
                    'messages': row[3],
                    'avg_response_time': row[4]
                })
            
            conn.close()
            return stats
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงสถิติ: {e}")
            return {}

if __name__ == "__main__":
    # ทดสอบระบบ
    logger = AutoLogger()
    logger.start_background_logging()
    
    # ทดสอบบันทึกการสนทนา
    logger.log_conversation(
        session_id="test_session_001",
        user_message="สวัสดีครับ",
        ai_response="สวัสดีครับ! มีอะไรให้ช่วยเหลือไหมครับ?",
        metadata={"source": "test", "user_id": "test_user"}
    )
    
    print("ระบบ AutoLogger พร้อมใช้งาน!")
    input("กด Enter เพื่อหยุด...")
    logger.stop_background_logging() 