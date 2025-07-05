#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI Security Manager System
ระบบจัดการความปลอดภัยแบบ admin-only
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

class SecurityManager:
    """ระบบจัดการความปลอดภัยแบบ admin-only"""
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.admin_token = self.config.get('admin_token', 'changeme')

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        default_config = {
            'log_level': 'INFO',
            'admin_token': 'changeme',
            'log_file': 'security_manager.log'
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
        self.logger = logging.getLogger('SecurityManager')

    def check_admin(self, token: str) -> bool:
        if token == self.admin_token:
            self.logger.info('Admin access granted')
            return True
        else:
            self.logger.warning('Admin access denied')
            return False

if __name__ == "__main__":
    sm = SecurityManager()
    token = input('กรุณาใส่ admin token: ')
    if sm.check_admin(token):
        print('เข้าถึงระบบได้')
    else:
        print('ปฏิเสธการเข้าถึง') 