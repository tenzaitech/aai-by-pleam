"""
Restore Controller - จัดการการกู้คืนข้อมูล
"""
import os
import shutil
from pathlib import Path

class RestoreController:
    def __init__(self):
        self.restore_log = []
    
    def restore_system(self, backup_path: str, target_path: str):
        """กู้คืนระบบ"""
        try:
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.copytree(backup_path, target_path)
            self.restore_log.append(f"Restored: {backup_path} -> {target_path}")
            return True
        except Exception as e:
            self.restore_log.append(f"Error: {e}")
            return False
