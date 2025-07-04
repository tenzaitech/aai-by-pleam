"""
Performance Monitor for WAWAGOT.AI
ระบบติดตามประสิทธิภาพของระบบ
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque
import json
from pathlib import Path

class PerformanceMonitor:
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Performance thresholds
        self.cpu_threshold = 80.0  # %
        self.memory_threshold = 85.0  # %
        self.disk_threshold = 90.0  # %
        
        # Alert history
        self.alerts = deque(maxlen=100)
        
    def start_monitoring(self, interval: float = 5.0):
        """เริ่มการ monitor performance"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        print(f"🔍 Performance Monitor เริ่มต้น (interval: {interval}s)")
        
    def stop_monitoring(self):
        """หยุดการ monitor"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        print("⏹️ Performance Monitor หยุดแล้ว")
        
    def _monitor_loop(self, interval: float):
        """Loop หลักสำหรับ monitoring"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # ตรวจสอบ alerts
                self._check_alerts(metrics)
                
                time.sleep(interval)
            except Exception as e:
                print(f"❌ Performance Monitor Error: {e}")
                time.sleep(interval)
                
    def _collect_metrics(self) -> Dict:
        """เก็บ metrics ระบบ"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            # Process info
            current_process = psutil.Process()
            process_memory = current_process.memory_info()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'process': {
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'cpu_percent': current_process.cpu_percent()
                }
            }
            
            return metrics
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            
    def _check_alerts(self, metrics: Dict):
        """ตรวจสอบและสร้าง alerts"""
        alerts = []
        
        # CPU Alert
        if metrics.get('cpu', {}).get('percent', 0) > self.cpu_threshold:
            alerts.append({
                'type': 'cpu_high',
                'message': f"CPU usage สูง: {metrics['cpu']['percent']:.1f}%",
                'severity': 'warning',
                'timestamp': datetime.now().isoformat()
            })
            
        # Memory Alert
        if metrics.get('memory', {}).get('percent', 0) > self.memory_threshold:
            alerts.append({
                'type': 'memory_high',
                'message': f"Memory usage สูง: {metrics['memory']['percent']:.1f}%",
                'severity': 'warning',
                'timestamp': datetime.now().isoformat()
            })
            
        # Disk Alert
        if metrics.get('disk', {}).get('percent', 0) > self.disk_threshold:
            alerts.append({
                'type': 'disk_high',
                'message': f"Disk usage สูง: {metrics['disk']['percent']:.1f}%",
                'severity': 'critical',
                'timestamp': datetime.now().isoformat()
            })
            
        # เพิ่ม alerts ใหม่
        for alert in alerts:
            self.alerts.append(alert)
            print(f"⚠️ {alert['message']}")
            
    def get_current_metrics(self) -> Dict:
        """ดึง metrics ปัจจุบัน"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return self._collect_metrics()
        
    def get_metrics_summary(self, minutes: int = 5) -> Dict:
        """สรุป metrics ในช่วงเวลาที่กำหนด"""
        if not self.metrics_history:
            return {"error": "ไม่มีข้อมูล metrics"}
            
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": f"ไม่มีข้อมูลใน {minutes} นาทีที่ผ่านมา"}
            
        # คำนวณค่าเฉลี่ย
        cpu_values = [m.get('cpu', {}).get('percent', 0) for m in recent_metrics]
        memory_values = [m.get('memory', {}).get('percent', 0) for m in recent_metrics]
        disk_values = [m.get('disk', {}).get('percent', 0) for m in recent_metrics]
        
        summary = {
            'period_minutes': minutes,
            'data_points': len(recent_metrics),
            'cpu': {
                'average': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'average': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            },
            'disk': {
                'average': sum(disk_values) / len(disk_values),
                'max': max(disk_values),
                'min': min(disk_values)
            },
            'alerts_count': len([a for a in self.alerts if 
                datetime.fromisoformat(a['timestamp']) > cutoff_time])
        }
        
        return summary
        
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """ดึง alerts"""
        if severity:
            return [a for a in self.alerts if a['severity'] == severity]
        return list(self.alerts)
        
    def clear_alerts(self):
        """ล้าง alerts"""
        self.alerts.clear()
        
    def export_metrics(self, filepath: str):
        """ส่งออก metrics เป็นไฟล์ JSON"""
        try:
            data = {
                'exported_at': datetime.now().isoformat(),
                'metrics': list(self.metrics_history),
                'alerts': list(self.alerts)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"✅ ส่งออก metrics ไปยัง {filepath}")
            
        except Exception as e:
            print(f"❌ ไม่สามารถส่งออก metrics ได้: {e}")
            
    def get_system_health(self) -> Dict:
        """ประเมินสุขภาพระบบ"""
        current = self.get_current_metrics()
        
        health_score = 100
        
        # ลดคะแนนตาม usage
        cpu_percent = current.get('cpu', {}).get('percent', 0)
        memory_percent = current.get('memory', {}).get('percent', 0)
        disk_percent = current.get('disk', {}).get('percent', 0)
        
        if cpu_percent > 90:
            health_score -= 30
        elif cpu_percent > 70:
            health_score -= 15
            
        if memory_percent > 90:
            health_score -= 30
        elif memory_percent > 70:
            health_score -= 15
            
        if disk_percent > 95:
            health_score -= 20
        elif disk_percent > 80:
            health_score -= 10
            
        # กำหนดสถานะ
        if health_score >= 80:
            status = "excellent"
        elif health_score >= 60:
            status = "good"
        elif health_score >= 40:
            status = "fair"
        else:
            status = "poor"
            
        return {
            'health_score': health_score,
            'status': status,
            'current_metrics': current,
            'recent_alerts': list(self.alerts)[-5:]  # 5 alerts ล่าสุด
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor() 