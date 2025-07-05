#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI Monitoring & Alert System
ระบบตรวจสอบและแจ้งเตือนสถานะระบบ
"""
import os
import logging
import threading
import time
from pathlib import Path
from typing import List

class MonitoringAlertSystem:
    """ระบบตรวจสอบและแจ้งเตือนสถานะระบบ"""
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.running = False
        self.setup_logging()
        self.alerts: List[str] = []

    def setup_logging(self):
        log_dir = Path('conversation_logs/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'monitoring_alert_system.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('MonitoringAlertSystem')

    def start(self):
        self.running = True
        t = threading.Thread(target=self._monitor_loop, daemon=True)
        t.start()
        self.logger.info('Monitoring started')

    def stop(self):
        self.running = False
        self.logger.info('Monitoring stopped')

    def _monitor_loop(self):
        while self.running:
            try:
                self.health_check()
            except Exception as e:
                self.send_alert(f'Error in health check: {e}')
            time.sleep(self.check_interval)

    def health_check(self):
        # ตัวอย่าง health check (สามารถเพิ่ม logic จริงได้)
        self.logger.info('Health check: OK')

    def send_alert(self, message: str):
        self.alerts.append(message)
        self.logger.warning(f'ALERT: {message}')
        # สามารถเพิ่ม webhook/email/LINE/Slack ได้ที่นี่

if __name__ == "__main__":
    mas = MonitoringAlertSystem(check_interval=5)
    mas.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mas.stop() 