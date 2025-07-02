"""
Backup Controller - จัดการการ backup ข้อมูล
"""
import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class BackupController:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, source_path: str, backup_name: str = None):
        """สร้าง backup"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / backup_name
        shutil.copytree(source_path, backup_path)
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str, target_path: str):
        """กู้คืน backup"""
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        shutil.copytree(backup_path, target_path)
        
        return True
