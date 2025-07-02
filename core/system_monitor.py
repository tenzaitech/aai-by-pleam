"""
System Monitor - ตรวจสอบสถานะระบบ
"""
import psutil
import os
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.monitor_log = []
    
    def check_system_health(self):
        """ตรวจสอบสุขภาพระบบ"""
        health = {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat()
        }
        
        self.monitor_log.append(health)
        return health
