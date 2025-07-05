#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI - Enhanced Backup Manager
ระบบ Auto-Backup ที่เหมาะสมและครบถ้วน
"""

import os
import shutil
import zipfile
import json
import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import logging
from core.logger import get_logger

class EnhancedBackupManager:
    def __init__(self):
        self.logger = get_logger("backup_manager")
        self.project_root = Path(__file__).parent
        self.backup_dir = self.project_root / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup configuration
        self.config = {
            "backup_enabled": True,
            "backup_schedule": "0 2 * * *",  # ทุกวันเวลา 02:00
            "retention_days": 30,
            "compression": True,
            "max_backup_size": "1GB",
            "backup_types": {
                "full": True,
                "incremental": True,
                "database": True,
                "config": True,
                "logs": True
            }
        }
        
        # Load configuration from file
        self.load_config()
        
        # Start backup scheduler
        self.start_scheduler()

    def load_config(self):
        """Load backup configuration"""
        config_file = self.project_root / "config" / "backup_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                self.logger.info("Loaded backup configuration")
            except Exception as e:
                self.logger.error(f"Error loading backup config: {e}")

    def save_config(self):
        """Save backup configuration"""
        config_file = self.project_root / "config" / "backup_config.json"
        config_file.parent.mkdir(exist_ok=True)
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info("Saved backup configuration")
        except Exception as e:
            self.logger.error(f"Error saving backup config: {e}")

    def should_backup(self):
        """Check if backup should be performed"""
        if not self.config["backup_enabled"]:
            return False
            
        # Check if last backup was more than 24 hours ago
        last_backup_file = self.backup_dir / "last_backup.txt"
        if last_backup_file.exists():
            try:
                with open(last_backup_file, 'r') as f:
                    last_backup_time = datetime.fromisoformat(f.read().strip())
                if datetime.now() - last_backup_time < timedelta(hours=24):
                    return False
            except Exception as e:
                self.logger.error(f"Error reading last backup time: {e}")
        
        return True

    def create_backup(self, backup_type="full"):
        """Create backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"wawagot_backup_{backup_type}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            self.logger.info(f"Starting {backup_type} backup: {backup_name}")
            
            if backup_type == "full":
                self._create_full_backup(backup_path)
            elif backup_type == "incremental":
                self._create_incremental_backup(backup_path)
            elif backup_type == "database":
                self._create_database_backup(backup_path)
            elif backup_type == "config":
                self._create_config_backup(backup_path)
            elif backup_type == "logs":
                self._create_logs_backup(backup_path)
            
            # Update last backup time
            with open(self.backup_dir / "last_backup.txt", 'w') as f:
                f.write(datetime.now().isoformat())
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            self.logger.info(f"Backup completed: {backup_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False

    def _create_full_backup(self, backup_path):
        """Create full backup"""
        backup_path.mkdir(exist_ok=True)
        
        # Files and directories to backup
        items_to_backup = [
            "core/",
            "config/",
            "conversation_logs/",
            "dashboard/",
            "data/",
            "pleamthinking/",
            "*.py",
            "*.md",
            "*.txt",
            "*.json",
            "*.env"
        ]
        
        # Exclude items
        exclude_items = [
            "__pycache__/",
            "*.pyc",
            "*.log",
            "backups/",
            "node_modules/",
            ".git/",
            "venv/",
            "env/"
        ]
        
        for item in items_to_backup:
            if item.endswith("/"):
                # Directory
                src_dir = self.project_root / item.rstrip("/")
                if src_dir.exists():
                    dst_dir = backup_path / item.rstrip("/")
                    self._copy_directory(src_dir, dst_dir, exclude_items)
            else:
                # File pattern
                for file_path in self.project_root.glob(item):
                    if self._should_include_file(file_path, exclude_items):
                        dst_file = backup_path / file_path.name
                        shutil.copy2(file_path, dst_file)

    def _create_incremental_backup(self, backup_path):
        """Create incremental backup"""
        # Find last backup
        last_backup = self._get_last_backup()
        if not last_backup:
            self._create_full_backup(backup_path)
            return
        
        backup_path.mkdir(exist_ok=True)
        
        # Get files modified since last backup
        last_backup_time = datetime.fromtimestamp(last_backup.stat().st_mtime)
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.stat().st_mtime > last_backup_time.timestamp():
                relative_path = file_path.relative_to(self.project_root)
                dst_file = backup_path / relative_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dst_file)

    def _create_database_backup(self, backup_path):
        """Create database backup"""
        backup_path.mkdir(exist_ok=True)
        
        # Backup SQLite database
        db_files = [
            "conversation_logs/conversation_logs.db",
            "*.db",
            "*.sqlite",
            "*.sqlite3"
        ]
        
        for pattern in db_files:
            for db_file in self.project_root.glob(pattern):
                if db_file.is_file():
                    dst_file = backup_path / f"database_{db_file.name}"
                    shutil.copy2(db_file, dst_file)

    def _create_config_backup(self, backup_path):
        """Create configuration backup"""
        backup_path.mkdir(exist_ok=True)
        
        config_items = [
            "config/",
            "*.json",
            "*.env",
            "*.yaml",
            "*.yml"
        ]
        
        for item in config_items:
            if item.endswith("/"):
                src_dir = self.project_root / item.rstrip("/")
                if src_dir.exists():
                    dst_dir = backup_path / item.rstrip("/")
                    self._copy_directory(src_dir, dst_dir)
            else:
                for file_path in self.project_root.glob(item):
                    if file_path.is_file():
                        dst_file = backup_path / file_path.name
                        shutil.copy2(file_path, dst_file)

    def _create_logs_backup(self, backup_path):
        """Create logs backup"""
        backup_path.mkdir(exist_ok=True)
        
        log_items = [
            "logs/",
            "*.log",
            "conversation_logs/logs/"
        ]
        
        for item in log_items:
            if item.endswith("/"):
                src_dir = self.project_root / item.rstrip("/")
                if src_dir.exists():
                    dst_dir = backup_path / item.rstrip("/")
                    self._copy_directory(src_dir, dst_dir)
            else:
                for file_path in self.project_root.glob(item):
                    if file_path.is_file():
                        dst_file = backup_path / file_path.name
                        shutil.copy2(file_path, dst_file)

    def _copy_directory(self, src_dir, dst_dir, exclude_items=None):
        """Copy directory with exclusions"""
        if exclude_items is None:
            exclude_items = []
        
        dst_dir.mkdir(parents=True, exist_ok=True)
        
        for item in src_dir.iterdir():
            if self._should_include_file(item, exclude_items):
                if item.is_dir():
                    self._copy_directory(item, dst_dir / item.name, exclude_items)
                else:
                    shutil.copy2(item, dst_dir / item.name)

    def _should_include_file(self, file_path, exclude_items):
        """Check if file should be included in backup"""
        for exclude in exclude_items:
            if exclude.endswith("/"):
                if file_path.name == exclude.rstrip("/") or str(file_path).endswith(exclude):
                    return False
            else:
                if file_path.match(exclude):
                    return False
        return True

    def _get_last_backup(self):
        """Get last backup directory"""
        backups = [d for d in self.backup_dir.iterdir() if d.is_dir() and d.name.startswith("wawagot_backup")]
        if backups:
            return max(backups, key=lambda x: x.stat().st_mtime)
        return None

    def cleanup_old_backups(self):
        """Clean up old backups"""
        try:
            retention_days = self.config["retention_days"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir() and backup_dir.name.startswith("wawagot_backup"):
                    backup_time = datetime.fromtimestamp(backup_dir.stat().st_mtime)
                    if backup_time < cutoff_date:
                        shutil.rmtree(backup_dir)
                        self.logger.info(f"Removed old backup: {backup_dir.name}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {e}")

    def start_scheduler(self):
        """Start backup scheduler"""
        if self.config["backup_enabled"]:
            schedule.every().day.at("02:00").do(self.scheduled_backup)
            
            def run_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(60)
            
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            self.logger.info("Backup scheduler started")

    def scheduled_backup(self):
        """Scheduled backup task"""
        if self.should_backup():
            self.create_backup("full")

    def get_backup_status(self):
        """Get backup status"""
        try:
            last_backup_file = self.backup_dir / "last_backup.txt"
            if last_backup_file.exists():
                with open(last_backup_file, 'r') as f:
                    last_backup_time = datetime.fromisoformat(f.read().strip())
                return {
                    "last_backup": last_backup_time.isoformat(),
                    "backup_count": len([d for d in self.backup_dir.iterdir() if d.is_dir()]),
                    "backup_size": self._get_backup_size(),
                    "next_backup": "02:00 daily"
                }
            else:
                return {
                    "last_backup": "Never",
                    "backup_count": 0,
                    "backup_size": "0 MB",
                    "next_backup": "02:00 daily"
                }
        except Exception as e:
            self.logger.error(f"Error getting backup status: {e}")
            return {"error": str(e)}

    def _get_backup_size(self):
        """Get total backup size"""
        total_size = 0
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                for file_path in backup_dir.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
        
        # Convert to MB
        return f"{total_size / (1024*1024):.1f} MB"

if __name__ == "__main__":
    backup_manager = EnhancedBackupManager()
    
    # Test backup
    print("Creating test backup...")
    backup_manager.create_backup("config")
    
    # Show status
    status = backup_manager.get_backup_status()
    print("Backup Status:", json.dumps(status, indent=2)) 