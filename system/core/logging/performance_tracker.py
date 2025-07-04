#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Tracker - ระบบติดตามประสิทธิภาพระบบ
ติดตาม CPU, Memory, Disk, Network และประสิทธิภาพของเครื่องมือต่างๆ
"""

import time
import threading
import psutil
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque
import os

@dataclass
class SystemMetrics:
    """ข้อมูล metrics ของระบบ"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_processes: int
    load_average: Optional[float] = None

@dataclass
class ModuleMetrics:
    """ข้อมูล metrics ของ module"""
    timestamp: str
    module: str
    operation: str
    duration_ms: int
    memory_usage_mb: float
    cpu_usage_percent: float
    status: str
    metadata: Dict[str, Any] = None

class PerformanceTracker:
    """ระบบติดตามประสิทธิภาพระบบ"""
    
    def __init__(self, db_path: str = "logs/performance.db"):
        self.db_path = db_path
        self.metrics_buffer = deque(maxlen=1000)
        self.module_metrics_buffer = deque(maxlen=500)
        
        # สร้างโฟลเดอร์
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # ตั้งค่าฐานข้อมูล
        self._init_database()
        
        # Thread lock
        self.lock = threading.Lock()
        
        # เริ่ม background monitoring
        self._start_monitoring()
        
        print("📊 Performance Tracker initialized")
    
    def _init_database(self):
        """สร้างฐานข้อมูล SQLite สำหรับ performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ตาราง system metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL NOT NULL,
                memory_percent REAL NOT NULL,
                memory_used_gb REAL NOT NULL,
                memory_total_gb REAL NOT NULL,
                disk_usage_percent REAL NOT NULL,
                disk_used_gb REAL NOT NULL,
                disk_total_gb REAL NOT NULL,
                network_bytes_sent INTEGER NOT NULL,
                network_bytes_recv INTEGER NOT NULL,
                active_processes INTEGER NOT NULL,
                load_average REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตาราง module metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                module TEXT NOT NULL,
                operation TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                memory_usage_mb REAL NOT NULL,
                cpu_usage_percent REAL NOT NULL,
                status TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตาราง performance alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                threshold_value REAL NOT NULL,
                current_value REAL NOT NULL,
                module TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # สร้าง indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_module_metrics_timestamp ON module_metrics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_module_metrics_module ON module_metrics(module)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_alerts_timestamp ON performance_alerts(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_alerts_type ON performance_alerts(alert_type)')
        
        conn.commit()
        conn.close()
    
    def track_system_metrics(self) -> SystemMetrics:
        """ติดตาม metrics ของระบบ"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Disk
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            
            # Network
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            # Active processes
            active_processes = len(psutil.pids())
            
            # Load average (เฉพาะ Linux)
            load_average = None
            try:
                load_average = os.getloadavg()[0] if hasattr(os, 'getloadavg') else None
            except:
                pass
            
            metrics = SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_gb=memory_used_gb,
                memory_total_gb=memory_total_gb,
                disk_usage_percent=disk_usage_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                active_processes=active_processes,
                load_average=load_average
            )
            
            # บันทึกลงฐานข้อมูล
            self._save_system_metrics(metrics)
            
            # เพิ่มใน buffer
            with self.lock:
                self.metrics_buffer.append(metrics)
            
            # ตรวจสอบ alerts
            self._check_alerts(metrics)
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error tracking system metrics: {e}")
            return None
    
    def track_module_operation(self, module: str, operation: str, 
                             duration_ms: int, memory_usage_mb: float = None,
                             cpu_usage_percent: float = None, status: str = "completed",
                             metadata: Dict[str, Any] = None):
        """ติดตามการทำงานของ module"""
        try:
            # ถ้าไม่ได้ระบุ memory และ cpu ให้วัดจาก process ปัจจุบัน
            if memory_usage_mb is None:
                process = psutil.Process()
                memory_usage_mb = process.memory_info().rss / (1024**2)
            
            if cpu_usage_percent is None:
                process = psutil.Process()
                cpu_usage_percent = process.cpu_percent()
            
            module_metrics = ModuleMetrics(
                timestamp=datetime.now().isoformat(),
                module=module,
                operation=operation,
                duration_ms=duration_ms,
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent,
                status=status,
                metadata=metadata or {}
            )
            
            # บันทึกลงฐานข้อมูล
            self._save_module_metrics(module_metrics)
            
            # เพิ่มใน buffer
            with self.lock:
                self.module_metrics_buffer.append(module_metrics)
            
        except Exception as e:
            print(f"❌ Error tracking module operation: {e}")
    
    def _save_system_metrics(self, metrics: SystemMetrics):
        """บันทึก system metrics ลงฐานข้อมูล"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, memory_used_gb, memory_total_gb,
                 disk_usage_percent, disk_used_gb, disk_total_gb, network_bytes_sent,
                 network_bytes_recv, active_processes, load_average)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp,
                metrics.cpu_percent,
                metrics.memory_percent,
                metrics.memory_used_gb,
                metrics.memory_total_gb,
                metrics.disk_usage_percent,
                metrics.disk_used_gb,
                metrics.disk_total_gb,
                metrics.network_bytes_sent,
                metrics.network_bytes_recv,
                metrics.active_processes,
                metrics.load_average
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error saving system metrics: {e}")
    
    def _save_module_metrics(self, metrics: ModuleMetrics):
        """บันทึก module metrics ลงฐานข้อมูล"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO module_metrics 
                (timestamp, module, operation, duration_ms, memory_usage_mb,
                 cpu_usage_percent, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp,
                metrics.module,
                metrics.operation,
                metrics.duration_ms,
                metrics.memory_usage_mb,
                metrics.cpu_usage_percent,
                metrics.status,
                json.dumps(metrics.metadata) if metrics.metadata else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error saving module metrics: {e}")
    
    def _check_alerts(self, metrics: SystemMetrics):
        """ตรวจสอบ alerts"""
        alerts = []
        
        # CPU alert
        if metrics.cpu_percent > 80:
            alerts.append({
                "type": "high_cpu",
                "severity": "warning" if metrics.cpu_percent < 90 else "critical",
                "message": f"CPU usage is high: {metrics.cpu_percent:.1f}%",
                "threshold": 80,
                "current": metrics.cpu_percent
            })
        
        # Memory alert
        if metrics.memory_percent > 85:
            alerts.append({
                "type": "high_memory",
                "severity": "warning" if metrics.memory_percent < 95 else "critical",
                "message": f"Memory usage is high: {metrics.memory_percent:.1f}%",
                "threshold": 85,
                "current": metrics.memory_percent
            })
        
        # Disk alert
        if metrics.disk_usage_percent > 90:
            alerts.append({
                "type": "high_disk",
                "severity": "warning" if metrics.disk_usage_percent < 95 else "critical",
                "message": f"Disk usage is high: {metrics.disk_usage_percent:.1f}%",
                "threshold": 90,
                "current": metrics.disk_usage_percent
            })
        
        # บันทึก alerts
        for alert in alerts:
            self._save_alert(alert)
    
    def _save_alert(self, alert: Dict[str, Any]):
        """บันทึก alert ลงฐานข้อมูล"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_alerts 
                (timestamp, alert_type, severity, message, threshold_value, current_value)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                alert["type"],
                alert["severity"],
                alert["message"],
                alert["threshold"],
                alert["current"]
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error saving alert: {e}")
    
    def get_system_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """ดึง system metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT * FROM system_metrics 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (cutoff_time.isoformat(),))
            
            metrics = []
            for row in cursor.fetchall():
                metrics.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "cpu_percent": row[2],
                    "memory_percent": row[3],
                    "memory_used_gb": row[4],
                    "memory_total_gb": row[5],
                    "disk_usage_percent": row[6],
                    "disk_used_gb": row[7],
                    "disk_total_gb": row[8],
                    "network_bytes_sent": row[9],
                    "network_bytes_recv": row[10],
                    "active_processes": row[11],
                    "load_average": row[12]
                })
            
            conn.close()
            return metrics
            
        except Exception as e:
            print(f"❌ Error getting system metrics: {e}")
            return []
    
    def get_module_metrics(self, module: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """ดึง module metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            if module:
                cursor.execute('''
                    SELECT * FROM module_metrics 
                    WHERE module = ? AND timestamp > ? 
                    ORDER BY timestamp DESC
                ''', (module, cutoff_time.isoformat()))
            else:
                cursor.execute('''
                    SELECT * FROM module_metrics 
                    WHERE timestamp > ? 
                    ORDER BY timestamp DESC
                ''', (cutoff_time.isoformat(),))
            
            metrics = []
            for row in cursor.fetchall():
                metrics.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "module": row[2],
                    "operation": row[3],
                    "duration_ms": row[4],
                    "memory_usage_mb": row[5],
                    "cpu_usage_percent": row[6],
                    "status": row[7],
                    "metadata": json.loads(row[8]) if row[8] else None
                })
            
            conn.close()
            return metrics
            
        except Exception as e:
            print(f"❌ Error getting module metrics: {e}")
            return []
    
    def get_performance_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """ดึง performance alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT * FROM performance_alerts 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (cutoff_time.isoformat(),))
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "alert_type": row[2],
                    "severity": row[3],
                    "message": row[4],
                    "threshold_value": row[5],
                    "current_value": row[6],
                    "module": row[7]
                })
            
            conn.close()
            return alerts
            
        except Exception as e:
            print(f"❌ Error getting performance alerts: {e}")
            return []
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """ดึงสรุปประสิทธิภาพ"""
        try:
            # ข้อมูลล่าสุด
            recent_metrics = self.get_system_metrics(hours=1)
            recent_module_metrics = self.get_module_metrics(hours=1)
            recent_alerts = self.get_performance_alerts(hours=1)
            
            if not recent_metrics:
                return {}
            
            latest = recent_metrics[0]
            
            # คำนวณค่าเฉลี่ย
            avg_cpu = sum(m["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m["memory_percent"] for m in recent_metrics) / len(recent_metrics)
            avg_disk = sum(m["disk_usage_percent"] for m in recent_metrics) / len(recent_metrics)
            
            # สรุป module performance
            module_summary = {}
            for metric in recent_module_metrics:
                module = metric["module"]
                if module not in module_summary:
                    module_summary[module] = {
                        "operations": 0,
                        "total_duration": 0,
                        "avg_duration": 0,
                        "success_count": 0,
                        "fail_count": 0
                    }
                
                module_summary[module]["operations"] += 1
                module_summary[module]["total_duration"] += metric["duration_ms"]
                
                if metric["status"] == "completed":
                    module_summary[module]["success_count"] += 1
                else:
                    module_summary[module]["fail_count"] += 1
            
            # คำนวณค่าเฉลี่ย duration
            for module in module_summary:
                if module_summary[module]["operations"] > 0:
                    module_summary[module]["avg_duration"] = (
                        module_summary[module]["total_duration"] / 
                        module_summary[module]["operations"]
                    )
            
            return {
                "current": {
                    "cpu_percent": latest["cpu_percent"],
                    "memory_percent": latest["memory_percent"],
                    "disk_usage_percent": latest["disk_usage_percent"],
                    "active_processes": latest["active_processes"]
                },
                "average_1h": {
                    "cpu_percent": avg_cpu,
                    "memory_percent": avg_memory,
                    "disk_usage_percent": avg_disk
                },
                "module_performance": module_summary,
                "alerts_count": len(recent_alerts),
                "critical_alerts": len([a for a in recent_alerts if a["severity"] == "critical"]),
                "warning_alerts": len([a for a in recent_alerts if a["severity"] == "warning"])
            }
            
        except Exception as e:
            print(f"❌ Error getting performance summary: {e}")
            return {}
    
    def _start_monitoring(self):
        """เริ่ม background monitoring"""
        def monitor_system():
            while True:
                try:
                    self.track_system_metrics()
                    time.sleep(30)  # อัปเดตทุก 30 วินาที
                except Exception as e:
                    print(f"❌ System monitoring error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()


# Global performance tracker instance
_performance_tracker = None

def get_performance_tracker() -> PerformanceTracker:
    """ดึง global performance tracker instance"""
    global _performance_tracker
    if _performance_tracker is None:
        _performance_tracker = PerformanceTracker()
    return _performance_tracker

def track_operation(module: str, operation: str, duration_ms: int, 
                   memory_usage_mb: float = None, cpu_usage_percent: float = None,
                   status: str = "completed", metadata: Dict[str, Any] = None):
    """ติดตามการทำงานของ module (helper function)"""
    tracker = get_performance_tracker()
    tracker.track_module_operation(
        module=module,
        operation=operation,
        duration_ms=duration_ms,
        memory_usage_mb=memory_usage_mb,
        cpu_usage_percent=cpu_usage_percent,
        status=status,
        metadata=metadata
    ) 