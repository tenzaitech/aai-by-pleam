#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI Auto Backup System
ระบบสำรองข้อมูลอัตโนมัติแบบยืดหยุ่น
"""

import os
import json
import shutil
import logging
import sqlite3
import zipfile
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time

class AutoBackup:
    """ระบบสำรองข้อมูลอัตโนมัติ"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.db_path = self.config.get('backup_database_path', 'auto_backup.db')
        self.init_database()
        self.running = False
        self.backup_thread = None
        
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """โหลดการตั้งค่า"""
        default_config = {
            'log_level': 'INFO',
            'backup_database_path': 'auto_backup.db',
            'backup_interval': 3600,  # 1 ชั่วโมง
            'max_backups': 10,
            'backup_paths': [
                'conversation_logs/',
                'config/',
                'privateoption-bypleam/'
            ],
            'exclude_patterns': [
                '*.log',
                '*.tmp',
                '__pycache__/',
                '*.pyc'
            ],
            'compression_enabled': True,
            'encryption_enabled': False,
            'cloud_backup_enabled': False,
            'cloud_provider': 'local'
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
                logging.FileHandler(log_dir / 'auto_backup.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AutoBackup')
        
    def init_database(self):
        """สร้างฐานข้อมูลสำหรับ Auto Backup"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ตารางประวัติการ backup
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backup_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id TEXT UNIQUE NOT NULL,
                    backup_path TEXT NOT NULL,
                    backup_size INTEGER,
                    file_count INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    error_message TEXT
                )
            ''')
            
            # ตารางไฟล์ที่ backup
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backup_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    file_hash TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (backup_id) REFERENCES backup_history (backup_id)
                )
            ''')
            
            # ตารางการตั้งค่า backup
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backup_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("สร้างฐานข้อมูล Auto Backup สำเร็จ")
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถสร้างฐานข้อมูล: {e}")
    
    def start_background_backup(self):
        """เริ่มการ backup แบบ background"""
        if self.running:
            self.logger.warning("ระบบ backup กำลังทำงานอยู่แล้ว")
            return
            
        self.running = True
        self.backup_thread = threading.Thread(target=self._background_backup_worker, daemon=True)
        self.backup_thread.start()
        self.logger.info("เริ่มระบบ backup แบบ background")
    
    def stop_background_backup(self):
        """หยุดการ backup แบบ background"""
        self.running = False
        if self.backup_thread:
            self.backup_thread.join()
        self.logger.info("หยุดระบบ backup แบบ background")
    
    def _background_backup_worker(self):
        """worker สำหรับ background backup"""
        while self.running:
            try:
                # ตรวจสอบว่าถึงเวลาที่ต้อง backup หรือไม่
                if self._should_create_backup():
                    self.create_backup()
                
                # ทำความสะอาด backup เก่า
                self._cleanup_old_backups()
                
                time.sleep(60)  # ตรวจสอบทุก 1 นาที
                
            except Exception as e:
                self.logger.error(f"ข้อผิดพลาดใน background backup worker: {e}")
                time.sleep(60)
    
    def _should_create_backup(self) -> bool:
        """ตรวจสอบว่าควรสร้าง backup หรือไม่"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ดู backup ล่าสุด
            cursor.execute('''
                SELECT created_at FROM backup_history 
                WHERE status = 'completed'
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return True  # ยังไม่มี backup เลย
            
            last_backup_time = datetime.fromisoformat(row[0])
            current_time = datetime.now()
            time_diff = current_time - last_backup_time
            
            # ตรวจสอบว่าผ่านเวลาที่กำหนดแล้วหรือไม่
            backup_interval = timedelta(seconds=self.config['backup_interval'])
            return time_diff >= backup_interval
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถตรวจสอบเวลาการ backup: {e}")
            return False
    
    def create_backup(self) -> str:
        """สร้าง backup"""
        try:
            backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir = Path('conversation_logs/backups')
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # สร้างโฟลเดอร์สำหรับ backup นี้
            backup_path = backup_dir / backup_id
            backup_path.mkdir(exist_ok=True)
            
            # บันทึกข้อมูล backup
            self._save_backup_record(backup_id, str(backup_path), 'pending')
            
            total_size = 0
            file_count = 0
            
            # backup ไฟล์ตามที่กำหนด
            for path in self.config['backup_paths']:
                if os.path.exists(path):
                    path_size, path_count = self._backup_path(path, backup_path)
                    total_size += path_size
                    file_count += path_count
            
            # สร้างไฟล์ zip ถ้าเปิดใช้งานการบีบอัด
            if self.config['compression_enabled']:
                zip_path = backup_path.with_suffix('.zip')
                self._create_zip_backup(backup_path, zip_path)
                backup_path = zip_path
            
            # อัปเดตสถานะ backup
            self._update_backup_status(backup_id, 'completed', total_size, file_count)
            
            self.logger.info(f"สร้าง backup สำเร็จ: {backup_id} ({total_size} bytes, {file_count} files)")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถสร้าง backup: {e}")
            if 'backup_id' in locals():
                self._update_backup_status(backup_id, 'failed', error_message=str(e))
            return ""
    
    def _backup_path(self, source_path: str, backup_dir: Path) -> tuple[int, int]:
        """backup path เดียว"""
        total_size = 0
        file_count = 0
        
        try:
            source_path_obj = Path(source_path)
            if source_path_obj.is_file():
                # backup ไฟล์เดียว
                dest_path = backup_dir / source_path_obj.name
                if self._should_backup_file(source_path):
                    shutil.copy2(source_path, dest_path)
                    file_size = source_path_obj.stat().st_size
                    total_size += file_size
                    file_count += 1
                    
                    # บันทึกข้อมูลไฟล์
                    self._save_file_record(source_path, file_size)
                    
            elif source_path_obj.is_dir():
                # backup โฟลเดอร์
                for root, dirs, files in os.walk(source_path):
                    # สร้างโฟลเดอร์ใน backup
                    rel_path = os.path.relpath(root, source_path)
                    backup_subdir = backup_dir / source_path_obj.name / rel_path
                    backup_subdir.mkdir(parents=True, exist_ok=True)
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self._should_backup_file(file_path):
                            rel_file_path = os.path.relpath(file_path, source_path)
                            dest_file_path = backup_dir / source_path_obj.name / rel_file_path
                            
                            shutil.copy2(file_path, dest_file_path)
                            file_size = os.path.getsize(file_path)
                            total_size += file_size
                            file_count += 1
                            
                            # บันทึกข้อมูลไฟล์
                            self._save_file_record(file_path, file_size)
                            
        except Exception as e:
            self.logger.error(f"ไม่สามารถ backup path {source_path}: {e}")
            
        return total_size, file_count
    
    def _should_backup_file(self, file_path: str) -> bool:
        """ตรวจสอบว่าควร backup ไฟล์นี้หรือไม่"""
        file_name = os.path.basename(file_path)
        
        for pattern in self.config['exclude_patterns']:
            if pattern.endswith('/'):
                # โฟลเดอร์
                if pattern[:-1] in file_path:
                    return False
            else:
                # ไฟล์
                if file_name.endswith(pattern[1:]) if pattern.startswith('*') else file_name == pattern:
                    return False
        
        return True
    
    def _create_zip_backup(self, source_dir: Path, zip_path: Path):
        """สร้างไฟล์ zip backup"""
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arc_name)
            
            # ลบโฟลเดอร์ต้นฉบับ
            shutil.rmtree(source_dir)
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถสร้าง zip backup: {e}")
    
    def _save_backup_record(self, backup_id: str, backup_path: str, status: str):
        """บันทึกข้อมูล backup"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO backup_history (backup_id, backup_path, status)
                VALUES (?, ?, ?)
            ''', (backup_id, backup_path, status))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถบันทึกข้อมูล backup: {e}")
    
    def _update_backup_status(self, backup_id: str, status: str, 
                            backup_size: int = 0, file_count: int = 0, 
                            error_message: str = None):
        """อัปเดตสถานะ backup"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE backup_history 
                SET status = ?, backup_size = ?, file_count = ?, 
                    completed_at = CURRENT_TIMESTAMP, error_message = ?
                WHERE backup_id = ?
            ''', (status, backup_size, file_count, error_message, backup_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถอัปเดตสถานะ backup: {e}")
    
    def _save_file_record(self, file_path: str, file_size: int):
        """บันทึกข้อมูลไฟล์"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # คำนวณ hash ของไฟล์
            file_hash = self._calculate_file_hash(file_path)
            
            cursor.execute('''
                INSERT INTO backup_files (file_path, file_size, file_hash)
                VALUES (?, ?, ?)
            ''', (file_path, file_size, file_hash))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถบันทึกข้อมูลไฟล์: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """คำนวณ hash ของไฟล์"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"ไม่สามารถคำนวณ hash ของไฟล์ {file_path}: {e}")
            return ""
    
    def _cleanup_old_backups(self):
        """ทำความสะอาด backup เก่า"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # นับจำนวน backup ที่สำเร็จ
            cursor.execute('''
                SELECT COUNT(*) FROM backup_history 
                WHERE status = 'completed'
            ''')
            backup_count = cursor.fetchone()[0]
            
            if backup_count > self.config['max_backups']:
                # หา backup เก่าที่สุดที่ต้องลบ
                cursor.execute('''
                    SELECT backup_id, backup_path FROM backup_history 
                    WHERE status = 'completed'
                    ORDER BY created_at ASC
                    LIMIT ?
                ''', (backup_count - self.config['max_backups'],))
                
                old_backups = cursor.fetchall()
                
                for backup_id, backup_path in old_backups:
                    # ลบไฟล์ backup
                    if os.path.exists(backup_path):
                        if backup_path.endswith('.zip'):
                            os.remove(backup_path)
                        else:
                            shutil.rmtree(backup_path)
                    
                    # ลบข้อมูลจากฐานข้อมูล
                    cursor.execute('DELETE FROM backup_files WHERE backup_id = ?', (backup_id,))
                    cursor.execute('DELETE FROM backup_history WHERE backup_id = ?', (backup_id,))
                    
                    self.logger.info(f"ลบ backup เก่า: {backup_id}")
                
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถทำความสะอาด backup เก่า: {e}")
    
    def restore_backup(self, backup_id: str, restore_path: str = None) -> bool:
        """กู้คืน backup"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ดึงข้อมูล backup
            cursor.execute('''
                SELECT backup_path, status FROM backup_history 
                WHERE backup_id = ?
            ''', (backup_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                self.logger.error(f"ไม่พบ backup: {backup_id}")
                return False
            
            backup_path, status = row
            
            if status != 'completed':
                self.logger.error(f"Backup {backup_id} ไม่สำเร็จ")
                return False
            
            if not os.path.exists(backup_path):
                self.logger.error(f"ไม่พบไฟล์ backup: {backup_path}")
                return False
            
            # กำหนด path สำหรับกู้คืน
            if not restore_path:
                restore_path = f"restored_{backup_id}"
            
            # กู้คืนไฟล์
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(restore_path)
            else:
                shutil.copytree(backup_path, restore_path)
            
            self.logger.info(f"กู้คืน backup สำเร็จ: {backup_id} -> {restore_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถกู้คืน backup: {e}")
            return False
    
    def get_backup_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """ดึงประวัติการ backup"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM backup_history 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            backups = []
            
            for row in rows:
                backups.append({
                    'id': row[0],
                    'backup_id': row[1],
                    'backup_path': row[2],
                    'backup_size': row[3],
                    'file_count': row[4],
                    'status': row[5],
                    'created_at': row[6],
                    'completed_at': row[7],
                    'error_message': row[8]
                })
            
            conn.close()
            return backups
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงประวัติการ backup: {e}")
            return []
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """ดึงสถิติการ backup"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # นับ backup ตามสถานะ
            cursor.execute('''
                SELECT status, COUNT(*) FROM backup_history GROUP BY status
            ''')
            status_counts = dict(cursor.fetchall())
            
            # ขนาด backup รวม
            cursor.execute('''
                SELECT SUM(backup_size) FROM backup_history 
                WHERE status = 'completed'
            ''')
            total_size = cursor.fetchone()[0] or 0
            
            # จำนวนไฟล์รวม
            cursor.execute('''
                SELECT SUM(file_count) FROM backup_history 
                WHERE status = 'completed'
            ''')
            total_files = cursor.fetchone()[0] or 0
            
            # backup ล่าสุด
            cursor.execute('''
                SELECT created_at FROM backup_history 
                WHERE status = 'completed'
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            last_backup = cursor.fetchone()
            
            conn.close()
            
            return {
                'status_counts': status_counts,
                'total_size': total_size,
                'total_files': total_files,
                'last_backup': last_backup[0] if last_backup else None,
                'total_backups': sum(status_counts.values())
            }
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงสถิติการ backup: {e}")
            return {}

if __name__ == "__main__":
    # ทดสอบระบบ
    backup_system = AutoBackup()
    
    # สร้าง backup ทันที
    backup_id = backup_system.create_backup()
    print(f"สร้าง backup สำเร็จ: {backup_id}")
    
    # แสดงประวัติ
    history = backup_system.get_backup_history()
    print("\nประวัติการ backup:")
    for backup in history:
        print(f"- {backup['backup_id']}: {backup['status']} ({backup['backup_size']} bytes)")
    
    # แสดงสถิติ
    stats = backup_system.get_backup_statistics()
    print("\nสถิติการ backup:")
    print(json.dumps(stats, indent=2, ensure_ascii=False)) 