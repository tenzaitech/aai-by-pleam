#!/usr/bin/env python3
"""
God Mode Knowledge Manager
ระบบจัดการความรู้สำหรับ God Mode แบบถาวร
"""

import json
import os
import pickle
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib
import shutil

class GodModeKnowledgeManager:
    """จัดการความรู้สำหรับ God Mode แบบถาวร"""
    
    def __init__(self, base_path: str = "alldata_godmode"):
        self.base_path = base_path
        self.db_path = os.path.join(base_path, "godmode_knowledge.db")
        self.sessions_path = os.path.join(base_path, "sessions")
        self.commands_path = os.path.join(base_path, "commands")
        self.results_path = os.path.join(base_path, "results")
        self.patterns_path = os.path.join(base_path, "patterns")
        self.learnings_path = os.path.join(base_path, "learnings")
        
        # สร้างโฟลเดอร์ทั้งหมด
        self._create_directories()
        
        # สร้างฐานข้อมูล
        self._init_database()
    
    def _create_directories(self):
        """สร้างโฟลเดอร์ทั้งหมดที่จำเป็น"""
        directories = [
            self.base_path,
            self.sessions_path,
            self.commands_path,
            self.results_path,
            self.patterns_path,
            self.learnings_path
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
    
    def _init_database(self):
        """สร้างฐานข้อมูล SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ตาราง sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT,
                commands_count INTEGER,
                results_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตาราง commands
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                command_hash TEXT,
                command_text TEXT,
                command_type TEXT,
                execution_time TIMESTAMP,
                success BOOLEAN,
                result_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # ตาราง results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                command_hash TEXT,
                result_type TEXT,
                result_data TEXT,
                file_path TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # ตาราง patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT,
                pattern_type TEXT,
                pattern_data TEXT,
                success_rate REAL,
                usage_count INTEGER,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตาราง learnings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                learning_type TEXT,
                learning_data TEXT,
                context TEXT,
                importance_score REAL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Initialized database: {self.db_path}")
    
    def start_session(self, session_id: str = None) -> str:
        """เริ่มต้น session ใหม่"""
        if session_id is None:
            session_id = f"godmode_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO sessions 
            (session_id, start_time, status, commands_count, results_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, datetime.now(), 'active', 0, 0))
        
        conn.commit()
        conn.close()
        
        print(f"🚀 Started God Mode session: {session_id}")
        return session_id
    
    def end_session(self, session_id: str):
        """จบ session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions 
            SET end_time = ?, status = 'completed'
            WHERE session_id = ?
        ''', (datetime.now(), session_id))
        
        conn.commit()
        conn.close()
        
        print(f"🏁 Ended God Mode session: {session_id}")
    
    def save_command(self, session_id: str, command: str, command_type: str = "general", 
                    success: bool = True, result_summary: str = ""):
        """บันทึกคำสั่งที่ใช้"""
        command_hash = hashlib.md5(command.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO commands 
            (session_id, command_hash, command_text, command_type, execution_time, success, result_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, command_hash, command, command_type, datetime.now(), success, result_summary))
        
        # อัปเดตจำนวนคำสั่งใน session
        cursor.execute('''
            UPDATE sessions 
            SET commands_count = commands_count + 1
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        
        # บันทึกไฟล์คำสั่ง
        command_file = os.path.join(self.commands_path, f"{command_hash}.json")
        command_data = {
            "session_id": session_id,
            "command": command,
            "command_type": command_type,
            "success": success,
            "result_summary": result_summary,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(command_file, 'w', encoding='utf-8') as f:
            json.dump(command_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved command: {command[:50]}...")
    
    def save_result(self, session_id: str, command_hash: str, result_type: str, 
                   result_data: Any, file_path: str = None, metadata: Dict = None):
        """บันทึกผลลัพธ์"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # บันทึกผลลัพธ์ลงฐานข้อมูล
        cursor.execute('''
            INSERT INTO results 
            (session_id, command_hash, result_type, result_data, file_path, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, command_hash, result_type, json.dumps(result_data), 
              file_path, json.dumps(metadata) if metadata else None))
        
        # อัปเดตจำนวนผลลัพธ์ใน session
        cursor.execute('''
            UPDATE sessions 
            SET results_count = results_count + 1
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        
        # บันทึกไฟล์ผลลัพธ์
        result_file = os.path.join(self.results_path, f"{command_hash}_{result_type}.json")
        result_data_full = {
            "session_id": session_id,
            "command_hash": command_hash,
            "result_type": result_type,
            "result_data": result_data,
            "file_path": file_path,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data_full, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved result: {result_type}")
    
    def save_pattern(self, pattern_name: str, pattern_type: str, pattern_data: Dict, 
                    success_rate: float = 0.0, usage_count: int = 1):
        """บันทึก pattern ที่ใช้บ่อย"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO patterns 
            (pattern_name, pattern_type, pattern_data, success_rate, usage_count, last_used)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (pattern_name, pattern_type, json.dumps(pattern_data), 
              success_rate, usage_count, datetime.now()))
        
        conn.commit()
        conn.close()
        
        # บันทึกไฟล์ pattern
        pattern_file = os.path.join(self.patterns_path, f"{pattern_name}.json")
        pattern_data_full = {
            "pattern_name": pattern_name,
            "pattern_type": pattern_type,
            "pattern_data": pattern_data,
            "success_rate": success_rate,
            "usage_count": usage_count,
            "last_used": datetime.now().isoformat()
        }
        
        with open(pattern_file, 'w', encoding='utf-8') as f:
            json.dump(pattern_data_full, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved pattern: {pattern_name}")
    
    def save_learning(self, learning_type: str, learning_data: Dict, context: str = "", 
                     importance_score: float = 1.0, tags: List[str] = None):
        """บันทึกการเรียนรู้ใหม่"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learnings 
            (learning_type, learning_data, context, importance_score, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (learning_type, json.dumps(learning_data), context, 
              importance_score, json.dumps(tags) if tags else None))
        
        conn.commit()
        conn.close()
        
        # บันทึกไฟล์การเรียนรู้
        learning_file = os.path.join(self.learnings_path, f"{learning_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        learning_data_full = {
            "learning_type": learning_type,
            "learning_data": learning_data,
            "context": context,
            "importance_score": importance_score,
            "tags": tags,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(learning_file, 'w', encoding='utf-8') as f:
            json.dump(learning_data_full, f, ensure_ascii=False, indent=2)
        
        print(f"🧠 Saved learning: {learning_type}")
    
    def get_session_history(self, session_id: str = None, limit: int = 10) -> List[Dict]:
        """ดึงประวัติ session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('''
                SELECT * FROM sessions WHERE session_id = ?
                ORDER BY created_at DESC
            ''', (session_id,))
        else:
            cursor.execute('''
                SELECT * FROM sessions 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "id": row[0],
                "session_id": row[1],
                "start_time": row[2],
                "end_time": row[3],
                "status": row[4],
                "commands_count": row[5],
                "results_count": row[6],
                "created_at": row[7]
            })
        
        conn.close()
        return sessions
    
    def get_command_history(self, session_id: str = None, limit: int = 50) -> List[Dict]:
        """ดึงประวัติคำสั่ง"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute('''
                SELECT * FROM commands WHERE session_id = ?
                ORDER BY execution_time DESC
                LIMIT ?
            ''', (session_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM commands 
                ORDER BY execution_time DESC 
                LIMIT ?
            ''', (limit,))
        
        commands = []
        for row in cursor.fetchall():
            commands.append({
                "id": row[0],
                "session_id": row[1],
                "command_hash": row[2],
                "command_text": row[3],
                "command_type": row[4],
                "execution_time": row[5],
                "success": row[6],
                "result_summary": row[7],
                "created_at": row[8]
            })
        
        conn.close()
        return commands
    
    def get_patterns(self, pattern_type: str = None) -> List[Dict]:
        """ดึง patterns ที่ใช้บ่อย"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if pattern_type:
            cursor.execute('''
                SELECT * FROM patterns WHERE pattern_type = ?
                ORDER BY usage_count DESC, last_used DESC
            ''', (pattern_type,))
        else:
            cursor.execute('''
                SELECT * FROM patterns 
                ORDER BY usage_count DESC, last_used DESC
            ''')
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                "id": row[0],
                "pattern_name": row[1],
                "pattern_type": row[2],
                "pattern_data": json.loads(row[3]),
                "success_rate": row[4],
                "usage_count": row[5],
                "last_used": row[6],
                "created_at": row[7]
            })
        
        conn.close()
        return patterns
    
    def get_learnings(self, learning_type: str = None, min_importance: float = 0.5) -> List[Dict]:
        """ดึงการเรียนรู้ที่สำคัญ"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if learning_type:
            cursor.execute('''
                SELECT * FROM learnings 
                WHERE learning_type = ? AND importance_score >= ?
                ORDER BY importance_score DESC, created_at DESC
            ''', (learning_type, min_importance))
        else:
            cursor.execute('''
                SELECT * FROM learnings 
                WHERE importance_score >= ?
                ORDER BY importance_score DESC, created_at DESC
            ''', (min_importance,))
        
        learnings = []
        for row in cursor.fetchall():
            learnings.append({
                "id": row[0],
                "learning_type": row[1],
                "learning_data": json.loads(row[2]),
                "context": row[3],
                "importance_score": row[4],
                "tags": json.loads(row[5]) if row[5] else None,
                "created_at": row[6]
            })
        
        conn.close()
        return learnings
    
    def search_knowledge(self, query: str, search_type: str = "all") -> List[Dict]:
        """ค้นหาความรู้"""
        results = []
        
        if search_type in ["all", "commands"]:
            commands = self.get_command_history(limit=100)
            for cmd in commands:
                if query.lower() in cmd["command_text"].lower():
                    results.append({
                        "type": "command",
                        "data": cmd,
                        "relevance": cmd["command_text"].lower().count(query.lower())
                    })
        
        if search_type in ["all", "patterns"]:
            patterns = self.get_patterns()
            for pattern in patterns:
                pattern_text = json.dumps(pattern["pattern_data"]).lower()
                if query.lower() in pattern_text:
                    results.append({
                        "type": "pattern",
                        "data": pattern,
                        "relevance": pattern_text.count(query.lower())
                    })
        
        if search_type in ["all", "learnings"]:
            learnings = self.get_learnings()
            for learning in learnings:
                learning_text = json.dumps(learning["learning_data"]).lower()
                if query.lower() in learning_text:
                    results.append({
                        "type": "learning",
                        "data": learning,
                        "relevance": learning_text.count(query.lower())
                    })
        
        # เรียงตามความเกี่ยวข้อง
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results
    
    def get_statistics(self) -> Dict:
        """ดึงสถิติของ knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # จำนวน sessions
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]
        
        # จำนวน commands
        cursor.execute("SELECT COUNT(*) FROM commands")
        total_commands = cursor.fetchone()[0]
        
        # จำนวน results
        cursor.execute("SELECT COUNT(*) FROM results")
        total_results = cursor.fetchone()[0]
        
        # จำนวน patterns
        cursor.execute("SELECT COUNT(*) FROM patterns")
        total_patterns = cursor.fetchone()[0]
        
        # จำนวน learnings
        cursor.execute("SELECT COUNT(*) FROM learnings")
        total_learnings = cursor.fetchone()[0]
        
        # success rate
        cursor.execute("SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) FROM commands")
        success_rate = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "total_sessions": total_sessions,
            "total_commands": total_commands,
            "total_results": total_results,
            "total_patterns": total_patterns,
            "total_learnings": total_learnings,
            "success_rate": success_rate * 100,
            "database_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        }
    
    def backup_knowledge_base(self, backup_path: str = None):
        """สำรองข้อมูล knowledge base"""
        if backup_path is None:
            backup_path = f"backup_godmode_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # สร้างโฟลเดอร์ backup
        os.makedirs(backup_path, exist_ok=True)
        
        # คัดลอกฐานข้อมูล
        if os.path.exists(self.db_path):
            shutil.copy2(self.db_path, os.path.join(backup_path, "godmode_knowledge.db"))
        
        # คัดลอกโฟลเดอร์ทั้งหมด
        for folder in ["sessions", "commands", "results", "patterns", "learnings"]:
            src = os.path.join(self.base_path, folder)
            dst = os.path.join(backup_path, folder)
            if os.path.exists(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
        
        print(f"💾 Knowledge base backed up to: {backup_path}")
        return backup_path

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    # สร้าง knowledge manager
    km = GodModeKnowledgeManager()
    
    # เริ่ม session
    session_id = km.start_session()
    
    # บันทึกคำสั่ง
    km.save_command(session_id, "python system_status_check.py", "system_check", True, "System status checked successfully")
    
    # บันทึก pattern
    km.save_pattern("system_check", "command", {
        "command": "python system_status_check.py",
        "description": "Check system status",
        "expected_output": "System status report"
    }, 0.95, 5)
    
    # บันทึกการเรียนรู้
    km.save_learning("system_optimization", {
        "observation": "Chrome processes accumulate over time",
        "solution": "Use taskkill to cleanup - DISABLED BY USER PREFERENCE",
        "command": "# taskkill /f /im chrome.exe  # DISABLED"
    }, "Chrome automation optimization", 0.8, ["chrome", "optimization", "cleanup"])
    
    # แสดงสถิติ
    stats = km.get_statistics()
    print("📊 Knowledge Base Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # จบ session
    km.end_session(session_id) 