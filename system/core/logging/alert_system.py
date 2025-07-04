#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alert System - ระบบจัดการ alerts และ notifications
จัดการ alerts แบบ real-time และส่ง notifications ไปยัง dashboard
"""

import json
import threading
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import queue

class AlertSeverity(Enum):
    """ระดับความรุนแรงของ alert"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(Enum):
    """ประเภทของ alert"""
    SYSTEM = "system"
    PERFORMANCE = "performance"
    WORKFLOW = "workflow"
    SECURITY = "security"
    USER_ACTION = "user_action"
    AI_LEARNING = "ai_learning"
    CHROME_AUTOMATION = "chrome_automation"
    DATABASE = "database"
    NETWORK = "network"
    CUSTOM = "custom"

@dataclass
class Alert:
    """ข้อมูล alert"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: str
    module: str = None
    workflow_id: str = None
    metadata: Dict[str, Any] = None
    acknowledged: bool = False
    acknowledged_by: str = None
    acknowledged_at: str = None
    expires_at: str = None
    auto_dismiss: bool = True
    dismiss_after_hours: int = 24

class AlertSystem:
    """ระบบจัดการ alerts และ notifications"""
    
    def __init__(self, db_path: str = "logs/alerts.db"):
        self.db_path = db_path
        self.alerts_buffer = deque(maxlen=1000)
        self.alert_queue = queue.Queue()
        
        # สร้างโฟลเดอร์
        import os
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # ตั้งค่าฐานข้อมูล
        self._init_database()
        
        # Thread lock
        self.lock = threading.Lock()
        
        # Callbacks สำหรับ real-time updates
        self.callbacks: Dict[str, List[Callable]] = {
            "alert_created": [],
            "alert_acknowledged": [],
            "alert_expired": []
        }
        
        # Alert rules
        self.alert_rules = self._load_alert_rules()
        
        # เริ่ม background processing
        self._start_background_processing()
        
        print("🚨 Alert System initialized")
    
    def _init_database(self):
        """สร้างฐานข้อมูล SQLite สำหรับ alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ตาราง alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                module TEXT,
                workflow_id TEXT,
                metadata TEXT,
                acknowledged BOOLEAN DEFAULT FALSE,
                acknowledged_by TEXT,
                acknowledged_at TEXT,
                expires_at TEXT,
                auto_dismiss BOOLEAN DEFAULT TRUE,
                dismiss_after_hours INTEGER DEFAULT 24,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตาราง alert rules
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT UNIQUE NOT NULL,
                rule_type TEXT NOT NULL,
                conditions TEXT NOT NULL,
                actions TEXT NOT NULL,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตาราง alert history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL,
                action TEXT NOT NULL,
                user TEXT,
                timestamp TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # สร้าง indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_module ON alerts(module)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_rules_enabled ON alert_rules(enabled)')
        
        conn.commit()
        conn.close()
    
    def _load_alert_rules(self) -> List[Dict[str, Any]]:
        """โหลด alert rules จากฐานข้อมูล"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM alert_rules WHERE enabled = TRUE')
            
            rules = []
            for row in cursor.fetchall():
                rules.append({
                    "id": row[0],
                    "rule_name": row[1],
                    "rule_type": row[2],
                    "conditions": json.loads(row[3]),
                    "actions": json.loads(row[4]),
                    "enabled": row[5]
                })
            
            conn.close()
            return rules
            
        except Exception as e:
            print(f"❌ Error loading alert rules: {e}")
            return self._get_default_rules()
    
    def _get_default_rules(self) -> List[Dict[str, Any]]:
        """สร้าง default alert rules"""
        return [
            {
                "rule_name": "high_cpu_usage",
                "rule_type": "performance",
                "conditions": {
                    "metric": "cpu_percent",
                    "threshold": 80,
                    "duration_minutes": 5
                },
                "actions": {
                    "create_alert": True,
                    "severity": "warning",
                    "auto_dismiss": True,
                    "dismiss_after_hours": 2
                }
            },
            {
                "rule_name": "high_memory_usage",
                "rule_type": "performance",
                "conditions": {
                    "metric": "memory_percent",
                    "threshold": 85,
                    "duration_minutes": 3
                },
                "actions": {
                    "create_alert": True,
                    "severity": "warning",
                    "auto_dismiss": True,
                    "dismiss_after_hours": 2
                }
            },
            {
                "rule_name": "workflow_failure",
                "rule_type": "workflow",
                "conditions": {
                    "status": "failed",
                    "consecutive_failures": 3
                },
                "actions": {
                    "create_alert": True,
                    "severity": "error",
                    "auto_dismiss": False
                }
            },
            {
                "rule_name": "chrome_automation_error",
                "rule_type": "chrome_automation",
                "conditions": {
                    "error_type": "timeout",
                    "frequency": "high"
                },
                "actions": {
                    "create_alert": True,
                    "severity": "warning",
                    "auto_dismiss": True,
                    "dismiss_after_hours": 1
                }
            }
        ]
    
    def create_alert(self, alert_type: AlertType, severity: AlertSeverity, 
                    title: str, message: str, module: str = None,
                    workflow_id: str = None, metadata: Dict[str, Any] = None,
                    auto_dismiss: bool = True, dismiss_after_hours: int = 24) -> str:
        """สร้าง alert ใหม่"""
        try:
            import uuid
            alert_id = str(uuid.uuid4())
            
            # คำนวณเวลาหมดอายุ
            expires_at = None
            if auto_dismiss:
                expires_at = (datetime.now() + timedelta(hours=dismiss_after_hours)).isoformat()
            
            alert = Alert(
                id=alert_id,
                type=alert_type,
                severity=severity,
                title=title,
                message=message,
                timestamp=datetime.now().isoformat(),
                module=module,
                workflow_id=workflow_id,
                metadata=metadata or {},
                auto_dismiss=auto_dismiss,
                dismiss_after_hours=dismiss_after_hours,
                expires_at=expires_at
            )
            
            # บันทึกลงฐานข้อมูล
            self._save_alert(alert)
            
            # เพิ่มใน buffer
            with self.lock:
                self.alerts_buffer.append(alert)
            
            # ส่งไปยัง queue
            self.alert_queue.put(alert)
            
            # เรียก callbacks
            self._trigger_callbacks("alert_created", alert)
            
            return alert_id
            
        except Exception as e:
            print(f"❌ Error creating alert: {e}")
            return None
    
    def _save_alert(self, alert: Alert):
        """บันทึก alert ลงฐานข้อมูล"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts 
                (id, type, severity, title, message, timestamp, module, workflow_id,
                 metadata, auto_dismiss, dismiss_after_hours, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.id,
                alert.type.value,
                alert.severity.value,
                alert.title,
                alert.message,
                alert.timestamp,
                alert.module,
                alert.workflow_id,
                json.dumps(alert.metadata) if alert.metadata else None,
                alert.auto_dismiss,
                alert.dismiss_after_hours,
                alert.expires_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error saving alert: {e}")
    
    def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """ยืนยันการรับทราบ alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET acknowledged = TRUE, acknowledged_by = ?, acknowledged_at = ?
                WHERE id = ?
            ''', (user, datetime.now().isoformat(), alert_id))
            
            if cursor.rowcount > 0:
                # บันทึกประวัติ
                cursor.execute('''
                    INSERT INTO alert_history 
                    (alert_id, action, user, timestamp, details)
                    VALUES (?, ?, ?, ?, ?)
                ''', (alert_id, "acknowledged", user, datetime.now().isoformat(), None))
                
                conn.commit()
                conn.close()
                
                # อัปเดต buffer
                with self.lock:
                    for alert in self.alerts_buffer:
                        if alert.id == alert_id:
                            alert.acknowledged = True
                            alert.acknowledged_by = user
                            alert.acknowledged_at = datetime.now().isoformat()
                            break
                
                # เรียก callbacks
                self._trigger_callbacks("alert_acknowledged", alert_id, user)
                
                return True
            
            conn.close()
            return False
            
        except Exception as e:
            print(f"❌ Error acknowledging alert: {e}")
            return False
    
    def dismiss_alert(self, alert_id: str, user: str = "system") -> bool:
        """ปิด alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM alerts WHERE id = ?', (alert_id,))
            
            if cursor.rowcount > 0:
                # บันทึกประวัติ
                cursor.execute('''
                    INSERT INTO alert_history 
                    (alert_id, action, user, timestamp, details)
                    VALUES (?, ?, ?, ?, ?)
                ''', (alert_id, "dismissed", user, datetime.now().isoformat(), None))
                
                conn.commit()
                conn.close()
                
                # ลบออกจาก buffer
                with self.lock:
                    self.alerts_buffer = deque(
                        [alert for alert in self.alerts_buffer if alert.id != alert_id],
                        maxlen=1000
                    )
                
                return True
            
            conn.close()
            return False
            
        except Exception as e:
            print(f"❌ Error dismissing alert: {e}")
            return False
    
    def get_active_alerts(self, severity: AlertSeverity = None, 
                         alert_type: AlertType = None, module: str = None) -> List[Dict[str, Any]]:
        """ดึง alerts ที่ยังไม่หมดอายุ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM alerts WHERE (expires_at IS NULL OR expires_at > ?)"
            params = [datetime.now().isoformat()]
            
            if severity:
                query += " AND severity = ?"
                params.append(severity.value)
            
            if alert_type:
                query += " AND type = ?"
                params.append(alert_type.value)
            
            if module:
                query += " AND module = ?"
                params.append(module)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    "id": row[0],
                    "type": row[1],
                    "severity": row[2],
                    "title": row[3],
                    "message": row[4],
                    "timestamp": row[5],
                    "module": row[6],
                    "workflow_id": row[7],
                    "metadata": json.loads(row[8]) if row[8] else None,
                    "acknowledged": bool(row[9]),
                    "acknowledged_by": row[10],
                    "acknowledged_at": row[11],
                    "expires_at": row[12],
                    "auto_dismiss": bool(row[13]),
                    "dismiss_after_hours": row[14]
                })
            
            conn.close()
            return alerts
            
        except Exception as e:
            print(f"❌ Error getting active alerts: {e}")
            return []
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """ดึงประวัติ alerts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT * FROM alert_history 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (cutoff_time.isoformat(),))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "id": row[0],
                    "alert_id": row[1],
                    "action": row[2],
                    "user": row[3],
                    "timestamp": row[4],
                    "details": row[5]
                })
            
            conn.close()
            return history
            
        except Exception as e:
            print(f"❌ Error getting alert history: {e}")
            return []
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """ดึงสรุป alerts"""
        try:
            active_alerts = self.get_active_alerts()
            alert_history = self.get_alert_history(hours=1)
            
            # นับตาม severity
            severity_counts = {}
            for alert in active_alerts:
                severity = alert["severity"]
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # นับตาม type
            type_counts = {}
            for alert in active_alerts:
                alert_type = alert["type"]
                type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
            
            # นับตาม module
            module_counts = {}
            for alert in active_alerts:
                module = alert["module"] or "unknown"
                module_counts[module] = module_counts.get(module, 0) + 1
            
            return {
                "total_active": len(active_alerts),
                "total_acknowledged": len([a for a in active_alerts if a["acknowledged"]]),
                "total_unacknowledged": len([a for a in active_alerts if not a["acknowledged"]]),
                "severity_breakdown": severity_counts,
                "type_breakdown": type_counts,
                "module_breakdown": module_counts,
                "recent_actions": len(alert_history)
            }
            
        except Exception as e:
            print(f"❌ Error getting alert summary: {e}")
            return {}
    
    def add_alert_rule(self, rule_name: str, rule_type: str, 
                      conditions: Dict[str, Any], actions: Dict[str, Any]) -> bool:
        """เพิ่ม alert rule ใหม่"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO alert_rules 
                (rule_name, rule_type, conditions, actions)
                VALUES (?, ?, ?, ?)
            ''', (
                rule_name,
                rule_type,
                json.dumps(conditions),
                json.dumps(actions)
            ))
            
            conn.commit()
            conn.close()
            
            # อัปเดต rules ใน memory
            self.alert_rules = self._load_alert_rules()
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding alert rule: {e}")
            return False
    
    def evaluate_rules(self, data: Dict[str, Any]) -> List[Alert]:
        """ประเมิน alert rules"""
        triggered_alerts = []
        
        for rule in self.alert_rules:
            try:
                if self._evaluate_rule(rule, data):
                    # สร้าง alert ตาม rule
                    alert = self._create_alert_from_rule(rule, data)
                    if alert:
                        triggered_alerts.append(alert)
            except Exception as e:
                print(f"❌ Error evaluating rule {rule['rule_name']}: {e}")
        
        return triggered_alerts
    
    def _evaluate_rule(self, rule: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """ประเมิน rule เดียว"""
        conditions = rule["conditions"]
        rule_type = rule["rule_type"]
        
        if rule_type == "performance":
            return self._evaluate_performance_rule(conditions, data)
        elif rule_type == "workflow":
            return self._evaluate_workflow_rule(conditions, data)
        elif rule_type == "chrome_automation":
            return self._evaluate_chrome_rule(conditions, data)
        else:
            return False
    
    def _evaluate_performance_rule(self, conditions: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """ประเมิน performance rule"""
        metric = conditions.get("metric")
        threshold = conditions.get("threshold")
        
        if metric in data and threshold is not None:
            return data[metric] >= threshold
        
        return False
    
    def _evaluate_workflow_rule(self, conditions: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """ประเมิน workflow rule"""
        status = conditions.get("status")
        consecutive_failures = conditions.get("consecutive_failures", 1)
        
        if status and "workflow_status" in data:
            if data["workflow_status"] == status:
                # ตรวจสอบ consecutive failures
                if "failure_count" in data:
                    return data["failure_count"] >= consecutive_failures
        
        return False
    
    def _evaluate_chrome_rule(self, conditions: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """ประเมิน chrome automation rule"""
        error_type = conditions.get("error_type")
        frequency = conditions.get("frequency", "low")
        
        if error_type and "chrome_error" in data:
            if data["chrome_error"] == error_type:
                # ตรวจสอบ frequency
                if "error_count" in data:
                    if frequency == "high" and data["error_count"] >= 5:
                        return True
                    elif frequency == "medium" and data["error_count"] >= 3:
                        return True
                    elif frequency == "low" and data["error_count"] >= 1:
                        return True
        
        return False
    
    def _create_alert_from_rule(self, rule: Dict[str, Any], data: Dict[str, Any]) -> Optional[Alert]:
        """สร้าง alert จาก rule"""
        actions = rule["actions"]
        
        if not actions.get("create_alert", False):
            return None
        
        severity = AlertSeverity(actions.get("severity", "warning"))
        auto_dismiss = actions.get("auto_dismiss", True)
        dismiss_after_hours = actions.get("dismiss_after_hours", 24)
        
        # สร้าง alert
        alert_id = self.create_alert(
            alert_type=AlertType(rule["rule_type"]),
            severity=severity,
            title=f"Alert: {rule['rule_name']}",
            message=f"Rule '{rule['rule_name']}' triggered",
            module=data.get("module"),
            workflow_id=data.get("workflow_id"),
            metadata=data,
            auto_dismiss=auto_dismiss,
            dismiss_after_hours=dismiss_after_hours
        )
        
        return alert_id
    
    def add_callback(self, event: str, callback: Callable):
        """เพิ่ม callback สำหรับ event"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, *args):
        """เรียก callbacks"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(*args)
            except Exception as e:
                print(f"❌ Callback error for {event}: {e}")
    
    def _start_background_processing(self):
        """เริ่ม background processing"""
        def process_alerts():
            while True:
                try:
                    # ตรวจสอบ alerts ที่หมดอายุ
                    self._cleanup_expired_alerts()
                    
                    # ประมวลผล alert queue
                    while not self.alert_queue.empty():
                        alert = self.alert_queue.get_nowait()
                        # สามารถเพิ่มการประมวลผลเพิ่มเติมได้ที่นี่
                    
                    time.sleep(60)  # ตรวจสอบทุก 1 นาที
                    
                except Exception as e:
                    print(f"❌ Alert processing error: {e}")
                    time.sleep(120)
        
        process_thread = threading.Thread(target=process_alerts, daemon=True)
        process_thread.start()
    
    def _cleanup_expired_alerts(self):
        """ลบ alerts ที่หมดอายุ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = datetime.now().isoformat()
            
            # ดึง alerts ที่หมดอายุ
            cursor.execute('''
                SELECT id FROM alerts 
                WHERE expires_at IS NOT NULL AND expires_at <= ?
            ''', (current_time,))
            
            expired_alerts = cursor.fetchall()
            
            # ลบ alerts ที่หมดอายุ
            cursor.execute('''
                DELETE FROM alerts 
                WHERE expires_at IS NOT NULL AND expires_at <= ?
            ''', (current_time,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                print(f"🧹 Cleaned up {deleted_count} expired alerts")
                
                # ลบออกจาก buffer
                with self.lock:
                    self.alerts_buffer = deque(
                        [alert for alert in self.alerts_buffer 
                         if not alert.expires_at or alert.expires_at > current_time],
                        maxlen=1000
                    )
                
                # เรียก callbacks
                for alert_id, in expired_alerts:
                    self._trigger_callbacks("alert_expired", alert_id)
            
        except Exception as e:
            print(f"❌ Error cleaning up expired alerts: {e}")


# Global alert system instance
_alert_system = None

def get_alert_system() -> AlertSystem:
    """ดึง global alert system instance"""
    global _alert_system
    if _alert_system is None:
        _alert_system = AlertSystem()
    return _alert_system

def create_alert(alert_type: AlertType, severity: AlertSeverity, 
                title: str, message: str, module: str = None,
                workflow_id: str = None, metadata: Dict[str, Any] = None,
                auto_dismiss: bool = True, dismiss_after_hours: int = 24) -> str:
    """สร้าง alert (helper function)"""
    alert_system = get_alert_system()
    return alert_system.create_alert(
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        module=module,
        workflow_id=workflow_id,
        metadata=metadata,
        auto_dismiss=auto_dismiss,
        dismiss_after_hours=dismiss_after_hours
    ) 