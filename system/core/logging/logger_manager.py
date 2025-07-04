#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger Manager - ระบบจัดการ log แบบรวมศูนย์
จัดการ log สำหรับทุกเครื่องมือในระบบ WAWAGOT V.2
"""

import os
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import sqlite3
from collections import deque
import queue

class LoggerManager:
    """ระบบจัดการ log แบบรวมศูนย์"""
    
    def __init__(self, base_path: str = "logs"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "wawagot_logs.db"
        self.log_retention_days = 1  # เก็บ log 1 วัน
        
        # สร้างโฟลเดอร์
        self.base_path.mkdir(exist_ok=True)
        
        # ตั้งค่าฐานข้อมูล
        self._init_database()
        
        # ตั้งค่า logging
        self._setup_logging()
        
        # Thread-safe queues สำหรับ real-time updates
        self.log_queue = queue.Queue()
        self.workflow_queue = queue.Queue()
        
        # In-memory log buffer (เก็บ log ล่าสุด 1000 entries)
        self.log_buffer = deque(maxlen=1000)
        self.workflow_buffer = deque(maxlen=100)
        
        # Thread lock
        self.lock = threading.Lock()
        
        # เริ่ม background threads
        self._start_background_threads()
        
        # สถานะ reset
        self.last_reset_time = datetime.now()
        self.reset_status = "ready"
        
        print("📝 Logger Manager initialized")
    
    def _init_database(self):
        """สร้างฐานข้อมูล SQLite สำหรับ log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ตาราง logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                module TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                workflow_id TEXT,
                step TEXT,
                duration_ms INTEGER,
                status TEXT,
                context TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตาราง workflows
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT UNIQUE NOT NULL,
                workflow_type TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT NOT NULL,
                total_steps INTEGER DEFAULT 0,
                completed_steps INTEGER DEFAULT 0,
                failed_steps INTEGER DEFAULT 0,
                total_duration_ms INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตาราง workflow_steps
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                step_id TEXT NOT NULL,
                step_name TEXT NOT NULL,
                module TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_ms INTEGER DEFAULT 0,
                logs TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows (workflow_id)
            )
        ''')
        
        # ตาราง performance_metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                module TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_value REAL NOT NULL,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # สร้าง indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_module ON logs(module)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_workflow ON logs(workflow_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflows_type ON workflows(workflow_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics(timestamp)')
        
        conn.commit()
        conn.close()
    
    def _setup_logging(self):
        """ตั้งค่า logging สำหรับแต่ละ module"""
        # สร้างโฟลเดอร์สำหรับแต่ละ module
        modules = [
            'auto_learning_manager',
            'knowledge_manager', 
            'chrome_controller',
            'ai_integration',
            'smart_command_processor',
            'supabase_integration',
            'visual_recognition',
            'backup_controller',
            'system_monitor',
            'thai_processor',
            'direct_control',
            'advanced_screen_reader',
            'master_controller',
            'environment_cards',
            'config_manager'
        ]
        
        for module in modules:
            module_path = self.base_path / module
            module_path.mkdir(exist_ok=True)
    
    def get_logger(self, module_name: str) -> logging.Logger:
        """สร้าง logger สำหรับ module"""
        logger = logging.getLogger(f"wawagot.{module_name}")
        
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)
            
            # File handler
            log_file = self.base_path / module_name / f"{module_name}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            
            # Custom handler สำหรับ database
            db_handler = DatabaseLogHandler(self)
            db_handler.setLevel(logging.DEBUG)
            logger.addHandler(db_handler)
        
        return logger
    
    def log(self, module: str, level: str, message: str, 
            workflow_id: str = None, step: str = None, 
            duration_ms: int = None, status: str = None,
            context: Dict[str, Any] = None, metadata: Dict[str, Any] = None):
        """บันทึก log ลงฐานข้อมูล"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "module": module,
                "level": level,
                "message": message,
                "workflow_id": workflow_id,
                "step": step,
                "duration_ms": duration_ms,
                "status": status,
                "context": json.dumps(context) if context else None,
                "metadata": json.dumps(metadata) if metadata else None
            }
            
            # บันทึกลงฐานข้อมูล
            self._save_log_to_db(log_entry)
            
            # เพิ่มใน buffer
            with self.lock:
                self.log_buffer.append(log_entry)
            
            # ส่งไปยัง queue สำหรับ real-time updates
            self.log_queue.put(log_entry)
            
        except Exception as e:
            print(f"❌ Error logging: {e}")
    
    def _save_log_to_db(self, log_entry: Dict[str, Any]):
        """บันทึก log ลงฐานข้อมูล"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO logs 
                (timestamp, module, level, message, workflow_id, step, 
                 duration_ms, status, context, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_entry["timestamp"],
                log_entry["module"],
                log_entry["level"],
                log_entry["message"],
                log_entry["workflow_id"],
                log_entry["step"],
                log_entry["duration_ms"],
                log_entry["status"],
                log_entry["context"],
                log_entry["metadata"]
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error saving log to DB: {e}")
    
    def start_workflow(self, workflow_id: str, workflow_type: str) -> str:
        """เริ่มต้น workflow ใหม่"""
        try:
            workflow = {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type,
                "start_time": datetime.now().isoformat(),
                "status": "running",
                "total_steps": 0,
                "completed_steps": 0,
                "failed_steps": 0,
                "total_duration_ms": 0
            }
            
            # บันทึกลงฐานข้อมูล
            self._save_workflow_to_db(workflow)
            
            # เพิ่มใน buffer
            with self.lock:
                self.workflow_buffer.append(workflow)
            
            # ส่งไปยัง queue
            self.workflow_queue.put(workflow)
            
            return workflow_id
            
        except Exception as e:
            print(f"❌ Error starting workflow: {e}")
            return None
    
    def update_workflow_step(self, workflow_id: str, step_id: str, step_name: str,
                           module: str, status: str, duration_ms: int = None,
                           logs: List[Dict] = None):
        """อัปเดต workflow step"""
        try:
            step = {
                "workflow_id": workflow_id,
                "step_id": step_id,
                "step_name": step_name,
                "module": module,
                "status": status,
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat() if status in ["completed", "failed"] else None,
                "duration_ms": duration_ms,
                "logs": json.dumps(logs) if logs else None
            }
            
            # บันทึกลงฐานข้อมูล
            self._save_workflow_step_to_db(step)
            
            # อัปเดต workflow status
            self._update_workflow_status(workflow_id, status)
            
        except Exception as e:
            print(f"❌ Error updating workflow step: {e}")
    
    def _save_workflow_to_db(self, workflow: Dict[str, Any]):
        """บันทึก workflow ลงฐานข้อมูล"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO workflows 
                (workflow_id, workflow_type, start_time, status, 
                 total_steps, completed_steps, failed_steps, total_duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                workflow["workflow_id"],
                workflow["workflow_type"],
                workflow["start_time"],
                workflow["status"],
                workflow["total_steps"],
                workflow["completed_steps"],
                workflow["failed_steps"],
                workflow["total_duration_ms"]
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error saving workflow to DB: {e}")
    
    def _save_workflow_step_to_db(self, step: Dict[str, Any]):
        """บันทึก workflow step ลงฐานข้อมูล"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO workflow_steps 
                (workflow_id, step_id, step_name, module, status, 
                 start_time, end_time, duration_ms, logs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                step["workflow_id"],
                step["step_id"],
                step["step_name"],
                step["module"],
                step["status"],
                step["start_time"],
                step["end_time"],
                step["duration_ms"],
                step["logs"]
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error saving workflow step to DB: {e}")
    
    def _update_workflow_status(self, workflow_id: str, step_status: str):
        """อัปเดตสถานะ workflow"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # นับ steps ตามสถานะ
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM workflow_steps 
                WHERE workflow_id = ?
            ''', (workflow_id,))
            
            result = cursor.fetchone()
            total_steps, completed_steps, failed_steps = result
            
            # ตรวจสอบสถานะ workflow
            if failed_steps > 0:
                workflow_status = "failed"
            elif completed_steps == total_steps and total_steps > 0:
                workflow_status = "completed"
            else:
                workflow_status = "running"
            
            # อัปเดต workflow
            cursor.execute('''
                UPDATE workflows 
                SET status = ?, total_steps = ?, completed_steps = ?, failed_steps = ?
                WHERE workflow_id = ?
            ''', (workflow_status, total_steps, completed_steps, failed_steps, workflow_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error updating workflow status: {e}")
    
    def get_recent_logs(self, limit: int = 100, module: str = None, level: str = None) -> List[Dict[str, Any]]:
        """ดึง log ล่าสุด"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM logs WHERE 1=1"
            params = []
            
            if module:
                query += " AND module = ?"
                params.append(module)
            
            if level:
                query += " AND level = ?"
                params.append(level)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "module": row[2],
                    "level": row[3],
                    "message": row[4],
                    "workflow_id": row[5],
                    "step": row[6],
                    "duration_ms": row[7],
                    "status": row[8],
                    "context": json.loads(row[9]) if row[9] else None,
                    "metadata": json.loads(row[10]) if row[10] else None
                })
            
            conn.close()
            return logs
            
        except Exception as e:
            print(f"❌ Error getting recent logs: {e}")
            return []
    
    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """ดึง workflows ที่กำลังทำงานอยู่"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM workflows 
                WHERE status IN ('running', 'pending')
                ORDER BY start_time DESC
            ''')
            
            workflows = []
            for row in cursor.fetchall():
                workflows.append({
                    "id": row[0],
                    "workflow_id": row[1],
                    "workflow_type": row[2],
                    "start_time": row[3],
                    "end_time": row[4],
                    "status": row[5],
                    "total_steps": row[6],
                    "completed_steps": row[7],
                    "failed_steps": row[8],
                    "total_duration_ms": row[9]
                })
            
            conn.close()
            return workflows
            
        except Exception as e:
            print(f"❌ Error getting active workflows: {e}")
            return []
    
    def cleanup_old_logs(self):
        """ลบ log เก่า (เกิน 1 วัน)"""
        try:
            cutoff_time = datetime.now() - timedelta(days=self.log_retention_days)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ลบ logs เก่า
            cursor.execute('DELETE FROM logs WHERE timestamp < ?', (cutoff_time.isoformat(),))
            deleted_logs = cursor.rowcount
            
            # ลบ workflows เก่า
            cursor.execute('DELETE FROM workflows WHERE start_time < ?', (cutoff_time.isoformat(),))
            deleted_workflows = cursor.rowcount
            
            # ลบ workflow steps เก่า
            cursor.execute('DELETE FROM workflow_steps WHERE start_time < ?', (cutoff_time.isoformat(),))
            deleted_steps = cursor.rowcount
            
            # ลบ performance metrics เก่า
            cursor.execute('DELETE FROM performance_metrics WHERE timestamp < ?', (cutoff_time.isoformat(),))
            deleted_metrics = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            # อัปเดตสถานะ reset
            self.last_reset_time = datetime.now()
            self.reset_status = "completed"
            
            print(f"🧹 Cleaned up: {deleted_logs} logs, {deleted_workflows} workflows, {deleted_steps} steps, {deleted_metrics} metrics")
            
        except Exception as e:
            print(f"❌ Error cleaning up old logs: {e}")
            self.reset_status = "failed"
    
    def get_reset_status(self) -> Dict[str, Any]:
        """ดึงสถานะ reset"""
        return {
            "last_reset_time": self.last_reset_time.isoformat(),
            "reset_status": self.reset_status,
            "retention_days": self.log_retention_days
        }
    
    def _start_background_threads(self):
        """เริ่ม background threads"""
        # Thread สำหรับ cleanup
        def cleanup_thread():
            while True:
                try:
                    time.sleep(3600)  # ตรวจสอบทุก 1 ชั่วโมง
                    self.cleanup_old_logs()
                except Exception as e:
                    print(f"❌ Cleanup thread error: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_thread, daemon=True)
        cleanup_thread.start()


class DatabaseLogHandler(logging.Handler):
    """Custom log handler สำหรับบันทึกลงฐานข้อมูล"""
    
    def __init__(self, logger_manager: LoggerManager):
        super().__init__()
        self.logger_manager = logger_manager
    
    def emit(self, record):
        try:
            # แยก module name จาก logger name
            module = record.name.split('.')[-1] if '.' in record.name else record.name
            
            # สร้าง context จาก record
            context = {
                "filename": record.filename,
                "lineno": record.lineno,
                "funcName": record.funcName
            }
            
            # บันทึก log
            self.logger_manager.log(
                module=module,
                level=record.levelname,
                message=record.getMessage(),
                context=context
            )
            
        except Exception as e:
            print(f"❌ Error in DatabaseLogHandler: {e}")


# Global logger manager instance
_logger_manager = None

def get_logger_manager() -> LoggerManager:
    """ดึง global logger manager instance"""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager

def get_logger(module_name: str) -> logging.Logger:
    """ดึง logger สำหรับ module"""
    return get_logger_manager().get_logger(module_name) 