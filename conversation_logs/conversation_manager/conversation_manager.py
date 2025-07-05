#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI Conversation Manager System
ระบบจัดการข้อมูลการสนทนาแบบยืดหยุ่น
"""

import os
import json
import logging
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import re

class ConversationManager:
    """ระบบจัดการข้อมูลการสนทนา"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.db_path = self.config.get('manager_database_path', 'conversation_manager.db')
        self.init_database()
        
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """โหลดการตั้งค่า"""
        default_config = {
            'log_level': 'INFO',
            'manager_database_path': 'conversation_manager.db',
            'max_conversations_per_session': 1000,
            'auto_archive': True,
            'archive_days': 90,
            'search_enabled': True,
            'indexing_enabled': True,
            'export_formats': ['json', 'csv', 'txt'],
            'compression_enabled': True
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
                logging.FileHandler(log_dir / 'conversation_manager.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ConversationManager')
        
    def init_database(self):
        """สร้างฐานข้อมูลสำหรับ Conversation Manager"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ตารางการจัดการ session
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    title TEXT,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    metadata TEXT
                )
            ''')
            
            # ตารางการจัดการ tags
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#007bff',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ตารางความสัมพันธ์ session-tag
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_tags (
                    session_id INTEGER,
                    tag_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id),
                    FOREIGN KEY (tag_id) REFERENCES tags (id),
                    PRIMARY KEY (session_id, tag_id)
                )
            ''')
            
            # ตารางการค้นหา
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    session_id INTEGER,
                    content TEXT,
                    keywords TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ตารางการ export
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    format TEXT,
                    file_path TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("สร้างฐานข้อมูล Conversation Manager สำเร็จ")
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถสร้างฐานข้อมูล: {e}")
    
    def create_session(self, session_id: str, title: str = None, 
                      description: str = None, metadata: Dict[str, Any] = None) -> bool:
        """สร้าง session ใหม่"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (session_id, title, description, metadata)
                VALUES (?, ?, ?, ?)
            ''', (session_id, title, description, 
                  json.dumps(metadata) if metadata else None))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"สร้าง session สำเร็จ: {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถสร้าง session: {e}")
            return False
    
    def update_session_activity(self, session_id: str) -> bool:
        """อัปเดตกิจกรรมล่าสุดของ session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET last_activity = CURRENT_TIMESTAMP
                WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถอัปเดต session activity: {e}")
            return False
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """ดึงข้อมูล session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sessions WHERE session_id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'session_id': row[1],
                    'title': row[2],
                    'description': row[3],
                    'created_at': row[4],
                    'last_activity': row[5],
                    'status': row[6],
                    'metadata': json.loads(row[7]) if row[7] else None
                }
            return {}
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงข้อมูล session: {e}")
            return {}
    
    def list_sessions(self, status: str = 'active', limit: int = 100) -> List[Dict[str, Any]]:
        """รายการ sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sessions 
                WHERE status = ? 
                ORDER BY last_activity DESC 
                LIMIT ?
            ''', (status, limit))
            
            rows = cursor.fetchall()
            sessions = []
            
            for row in rows:
                sessions.append({
                    'id': row[0],
                    'session_id': row[1],
                    'title': row[2],
                    'description': row[3],
                    'created_at': row[4],
                    'last_activity': row[5],
                    'status': row[6],
                    'metadata': json.loads(row[7]) if row[7] else None
                })
            
            conn.close()
            return sessions
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงรายการ sessions: {e}")
            return []
    
    def add_tag(self, name: str, color: str = '#007bff') -> bool:
        """เพิ่ม tag ใหม่"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO tags (name, color)
                VALUES (?, ?)
            ''', (name, color))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"เพิ่ม tag สำเร็จ: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถเพิ่ม tag: {e}")
            return False
    
    def tag_session(self, session_id: str, tag_name: str) -> bool:
        """เพิ่ม tag ให้ session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # หา session_id และ tag_id
            cursor.execute('SELECT id FROM sessions WHERE session_id = ?', (session_id,))
            session_row = cursor.fetchone()
            
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
            tag_row = cursor.fetchone()
            
            if not session_row or not tag_row:
                conn.close()
                return False
            
            # เพิ่มความสัมพันธ์
            cursor.execute('''
                INSERT OR IGNORE INTO session_tags (session_id, tag_id)
                VALUES (?, ?)
            ''', (session_row[0], tag_row[0]))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"เพิ่ม tag {tag_name} ให้ session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถเพิ่ม tag ให้ session: {e}")
            return False
    
    def get_session_tags(self, session_id: str) -> List[str]:
        """ดึง tags ของ session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT t.name FROM tags t
                JOIN session_tags st ON t.id = st.tag_id
                JOIN sessions s ON st.session_id = s.id
                WHERE s.session_id = ?
            ''', (session_id,))
            
            tags = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return tags
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึง tags ของ session: {e}")
            return []
    
    def search_conversations(self, query: str, session_id: str = None, 
                           limit: int = 50) -> List[Dict[str, Any]]:
        """ค้นหาการสนทนา"""
        try:
            # ใช้ SQLite FTS หรือการค้นหาแบบง่าย
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute('''
                    SELECT * FROM search_index 
                    WHERE session_id = (SELECT id FROM sessions WHERE session_id = ?)
                    AND (content LIKE ? OR keywords LIKE ?)
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (session_id, f'%{query}%', f'%{query}%', limit))
            else:
                cursor.execute('''
                    SELECT * FROM search_index 
                    WHERE content LIKE ? OR keywords LIKE ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (f'%{query}%', f'%{query}%', limit))
            
            rows = cursor.fetchall()
            results = []
            
            for row in rows:
                results.append({
                    'id': row[0],
                    'conversation_id': row[1],
                    'session_id': row[2],
                    'content': row[3],
                    'keywords': row[4],
                    'created_at': row[5]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถค้นหาการสนทนา: {e}")
            return []
    
    def export_session(self, session_id: str, format: str = 'json', 
                      file_path: str = None) -> str:
        """export session"""
        try:
            if format not in self.config['export_formats']:
                raise ValueError(f"ไม่รองรับ format: {format}")
            
            if not file_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = f"exports/session_{session_id}_{timestamp}.{format}"
            
            # สร้างโฟลเดอร์ exports
            export_dir = Path('conversation_logs/exports')
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # ดึงข้อมูล session
            session_info = self.get_session_info(session_id)
            if not session_info:
                raise ValueError(f"ไม่พบ session: {session_id}")
            
            # ดึงการสนทนาทั้งหมด (ต้องเชื่อมต่อกับ AutoLogger)
            conversations = self._get_session_conversations(session_id)
            
            # สร้างข้อมูล export
            export_data = {
                'session_info': session_info,
                'conversations': conversations,
                'exported_at': datetime.now().isoformat(),
                'total_conversations': len(conversations)
            }
            
            # บันทึกไฟล์
            if format == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            elif format == 'txt':
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Session: {session_id}\n")
                    f.write(f"Title: {session_info.get('title', 'N/A')}\n")
                    f.write(f"Exported: {export_data['exported_at']}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for conv in conversations:
                        f.write(f"[{conv['timestamp']}] User: {conv['user_message']}\n")
                        f.write(f"[{conv['timestamp']}] AI: {conv['ai_response']}\n\n")
            
            # บันทึกข้อมูล export
            self._save_export_record(session_id, format, file_path)
            
            self.logger.info(f"Export session สำเร็จ: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถ export session: {e}")
            return ""
    
    def _get_session_conversations(self, session_id: str) -> List[Dict[str, Any]]:
        """ดึงการสนทนาของ session (ต้องเชื่อมต่อกับ AutoLogger)"""
        # นี้เป็น placeholder - ในระบบจริงต้องเชื่อมต่อกับ AutoLogger
        try:
            # ตัวอย่างการเชื่อมต่อกับ AutoLogger database
            auto_logger_db = 'conversation_logs.db'
            if os.path.exists(auto_logger_db):
                conn = sqlite3.connect(auto_logger_db)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM conversations 
                    WHERE session_id = ? 
                    ORDER BY timestamp
                ''', (session_id,))
                
                rows = cursor.fetchall()
                conversations = []
                
                for row in rows:
                    conversations.append({
                        'id': row[0],
                        'session_id': row[1],
                        'timestamp': row[2],
                        'user_message': row[3],
                        'ai_response': row[4],
                        'context': row[5],
                        'metadata': json.loads(row[6]) if row[6] else None
                    })
                
                conn.close()
                return conversations
            
            return []
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงการสนทนาของ session: {e}")
            return []
    
    def _save_export_record(self, session_id: str, format: str, file_path: str):
        """บันทึกข้อมูล export"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO exports (session_id, format, file_path, status)
                VALUES ((SELECT id FROM sessions WHERE session_id = ?), ?, ?, 'completed')
            ''', (session_id, format, file_path))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถบันทึกข้อมูล export: {e}")
    
    def get_export_history(self, session_id: str = None) -> List[Dict[str, Any]]:
        """ดึงประวัติการ export"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute('''
                    SELECT e.*, s.session_id FROM exports e
                    JOIN sessions s ON e.session_id = s.id
                    WHERE s.session_id = ?
                    ORDER BY e.created_at DESC
                ''', (session_id,))
            else:
                cursor.execute('''
                    SELECT e.*, s.session_id FROM exports e
                    JOIN sessions s ON e.session_id = s.id
                    ORDER BY e.created_at DESC
                ''')
            
            rows = cursor.fetchall()
            exports = []
            
            for row in rows:
                exports.append({
                    'id': row[0],
                    'session_id': row[6],  # session_id จาก JOIN
                    'format': row[2],
                    'file_path': row[3],
                    'created_at': row[4],
                    'status': row[5]
                })
            
            conn.close()
            return exports
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงประวัติการ export: {e}")
            return []
    
    def archive_session(self, session_id: str) -> bool:
        """archived session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET status = 'archived', last_activity = CURRENT_TIMESTAMP
                WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Archived session: {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถ archived session: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """ดึงสถิติ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # นับ sessions ตาม status
            cursor.execute('''
                SELECT status, COUNT(*) FROM sessions GROUP BY status
            ''')
            status_counts = dict(cursor.fetchall())
            
            # นับ tags ที่ใช้บ่อย
            cursor.execute('''
                SELECT t.name, COUNT(st.session_id) 
                FROM tags t
                LEFT JOIN session_tags st ON t.id = st.tag_id
                GROUP BY t.id, t.name
                ORDER BY COUNT(st.session_id) DESC
                LIMIT 10
            ''')
            popular_tags = dict(cursor.fetchall())
            
            # สถิติการ export
            cursor.execute('''
                SELECT format, COUNT(*) FROM exports GROUP BY format
            ''')
            export_stats = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'session_stats': status_counts,
                'popular_tags': popular_tags,
                'export_stats': export_stats,
                'total_sessions': sum(status_counts.values()),
                'total_exports': sum(export_stats.values())
            }
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงสถิติ: {e}")
            return {}

if __name__ == "__main__":
    # ทดสอบระบบ
    manager = ConversationManager()
    
    # สร้าง session ใหม่
    session_id = "test_session_001"
    manager.create_session(session_id, "Session ทดสอบ", "สำหรับทดสอบระบบ")
    
    # เพิ่ม tags
    manager.add_tag("การพัฒนา", "#28a745")
    manager.add_tag("การทดสอบ", "#ffc107")
    manager.tag_session(session_id, "การพัฒนา")
    manager.tag_session(session_id, "การทดสอบ")
    
    # แสดงข้อมูล session
    session_info = manager.get_session_info(session_id)
    print("ข้อมูล Session:")
    print(json.dumps(session_info, indent=2, ensure_ascii=False))
    
    # แสดง tags
    tags = manager.get_session_tags(session_id)
    print(f"\nTags: {tags}")
    
    # แสดงสถิติ
    stats = manager.get_statistics()
    print("\nสถิติ:")
    print(json.dumps(stats, indent=2, ensure_ascii=False)) 