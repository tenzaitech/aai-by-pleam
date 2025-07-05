#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI Data Retention Manager
ระบบจัดการอายุข้อมูลและการลบ/Archive อัตโนมัติ
"""
import os
import json
import logging
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

class DataRetentionManager:
    """ระบบจัดการอายุข้อมูลและการลบ/Archive อัตโนมัติ"""
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.db_path = self.config.get('target_db', 'conversation_logs.db')
        self.retention_days = self.config.get('retention_days', 90)
        self.running = False

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        default_config = {
            'log_level': 'INFO',
            'target_db': 'conversation_logs.db',
            'retention_days': 90,
            'log_file': 'data_retention_manager.log'
        }
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"ไม่สามารถโหลด config: {e}")
        return default_config

    def setup_logging(self):
        log_dir = Path('conversation_logs/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=getattr(logging, self.config['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / self.config['log_file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('DataRetentionManager')

    def start(self):
        self.running = True
        t = threading.Thread(target=self._retention_loop, daemon=True)
        t.start()
        self.logger.info('Data retention manager started')

    def stop(self):
        self.running = False
        self.logger.info('Data retention manager stopped')

    def _retention_loop(self):
        while self.running:
            try:
                self.cleanup_old_data()
            except Exception as e:
                self.logger.error(f'Error in data retention: {e}')
            time.sleep(3600)  # ตรวจสอบทุก 1 ชั่วโมง

    def cleanup_old_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cutoff = (datetime.now() - timedelta(days=self.retention_days)).isoformat()
            cursor.execute('DELETE FROM conversations WHERE timestamp < ?', (cutoff,))
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            self.logger.info(f'ลบข้อมูลเก่ากว่า {self.retention_days} วัน จำนวน {deleted} รายการ')
        except Exception as e:
            self.logger.error(f'ไม่สามารถลบข้อมูลเก่า: {e}')

if __name__ == "__main__":
    drm = DataRetentionManager()
    drm.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        drm.stop() 