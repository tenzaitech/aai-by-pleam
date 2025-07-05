#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI - Enhanced Monitoring System
ระบบ Monitoring ที่เหมาะสมและครบถ้วน
"""

import os
import psutil
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import logging
from core.logger import get_logger
import schedule

class EnhancedMonitoringSystem:
    def __init__(self):
        self.logger = get_logger("monitoring_system")
        self.project_root = Path(__file__).parent
        self.monitoring_dir = self.project_root / "monitoring"
        self.monitoring_dir.mkdir(exist_ok=True)
        
        # Monitoring configuration
        self.config = {
            "monitoring_enabled": True,
            "check_interval": 60,  # seconds
            "alert_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 85,
                "disk_usage": 90,
                "chrome_processes": 20,
                "python_processes": 10
            },
            "monitoring_types": {
                "system": True,
                "processes": True,
                "network": True,
                "disk": True,
                "services": True,
                "performance": True
            },
            "alert_channels": {
                "log": True,
                "file": True,
                "email": False,
                "webhook": False
            }
        }
        
        # Load configuration
        self.load_config()
        
        # Initialize monitoring data
        self.monitoring_data = {
            "system_status": {},
            "alerts": [],
            "performance_history": [],
            "last_check": None
        }
        
        # Start monitoring
        self.start_monitoring()

    def load_config(self):
        """Load monitoring configuration"""
        config_file = self.project_root / "config" / "monitoring_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                self.logger.info("Loaded monitoring configuration")
            except Exception as e:
                self.logger.error(f"Error loading monitoring config: {e}")

    def save_config(self):
        """Save monitoring configuration"""
        config_file = self.project_root / "config" / "monitoring_config.json"
        config_file.parent.mkdir(exist_ok=True)
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info("Saved monitoring configuration")
        except Exception as e:
            self.logger.error(f"Error saving monitoring config: {e}")

    def start_monitoring(self):
        """Start monitoring system"""
        if self.config["monitoring_enabled"]:
            # Initial check
            self.perform_monitoring_check()
            
            # Schedule regular checks
            schedule.every(self.config["check_interval"]).seconds.do(self.perform_monitoring_check)
            
            def run_monitoring():
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            
            monitoring_thread = threading.Thread(target=run_monitoring, daemon=True)
            monitoring_thread.start()
            self.logger.info("Monitoring system started")

    def perform_monitoring_check(self):
        """Perform comprehensive monitoring check"""
        try:
            timestamp = datetime.now()
            self.logger.info("Performing monitoring check...")
            
            # System monitoring
            if self.config["monitoring_types"]["system"]:
                self._monitor_system()
            
            # Process monitoring
            if self.config["monitoring_types"]["processes"]:
                self._monitor_processes()
            
            # Network monitoring
            if self.config["monitoring_types"]["network"]:
                self._monitor_network()
            
            # Disk monitoring
            if self.config["monitoring_types"]["disk"]:
                self._monitor_disk()
            
            # Services monitoring
            if self.config["monitoring_types"]["services"]:
                self._monitor_services()
            
            # Performance monitoring
            if self.config["monitoring_types"]["performance"]:
                self._monitor_performance()
            
            # Update last check time
            self.monitoring_data["last_check"] = timestamp.isoformat()
            
            # Save monitoring data
            self._save_monitoring_data()
            
            # Check for alerts
            self._check_alerts()
            
            self.logger.info("Monitoring check completed")
            
        except Exception as e:
            self.logger.error(f"Error during monitoring check: {e}")

    def _monitor_system(self):
        """Monitor system resources"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # System load (Windows equivalent)
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            self.monitoring_data["system_status"] = {
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent,
                "memory_available": memory.available / (1024**3),  # GB
                "memory_total": memory.total / (1024**3),  # GB
                "load_average": load_avg,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring system: {e}")

    def _monitor_processes(self):
        """Monitor running processes"""
        try:
            processes = []
            chrome_processes = []
            python_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    process_data = {
                        "pid": proc_info['pid'],
                        "name": proc_info['name'],
                        "cpu_percent": proc_info['cpu_percent'],
                        "memory_mb": proc_info['memory_info'].rss / (1024**2)
                    }
                    processes.append(process_data)
                    
                    # Categorize processes
                    if 'chrome' in proc_info['name'].lower():
                        chrome_processes.append(process_data)
                    elif 'python' in proc_info['name'].lower():
                        python_processes.append(process_data)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.monitoring_data["processes"] = {
                "total_processes": len(processes),
                "chrome_processes": chrome_processes,
                "python_processes": python_processes,
                "chrome_count": len(chrome_processes),
                "python_count": len(python_processes)
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring processes: {e}")

    def _monitor_network(self):
        """Monitor network activity"""
        try:
            # Network interfaces
            network_interfaces = psutil.net_if_addrs()
            
            # Network connections
            network_connections = []
            for conn in psutil.net_connections():
                try:
                    conn_data = {
                        "family": conn.family,
                        "type": conn.type,
                        "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status
                    }
                    network_connections.append(conn_data)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Network I/O
            network_io = psutil.net_io_counters()
            
            self.monitoring_data["network"] = {
                "interfaces": list(network_interfaces.keys()),
                "connections": network_connections,
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring network: {e}")

    def _monitor_disk(self):
        """Monitor disk usage"""
        try:
            disk_usage = {}
            disk_io = {}
            
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        "total": usage.total / (1024**3),  # GB
                        "used": usage.used / (1024**3),    # GB
                        "free": usage.free / (1024**3),    # GB
                        "percent": usage.percent
                    }
                except (OSError, PermissionError):
                    continue
            
            # Disk I/O
            try:
                disk_io_stats = psutil.disk_io_counters()
                disk_io = {
                    "read_count": disk_io_stats.read_count,
                    "write_count": disk_io_stats.write_count,
                    "read_bytes": disk_io_stats.read_bytes,
                    "write_bytes": disk_io_stats.write_bytes
                }
            except Exception:
                disk_io = {}
            
            self.monitoring_data["disk"] = {
                "usage": disk_usage,
                "io": disk_io
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring disk: {e}")

    def _monitor_services(self):
        """Monitor system services"""
        try:
            services = []
            
            # Check for specific services
            service_names = [
                "WawagotService",  # Our custom service
                "PythonService",
                "ChromeService"
            ]
            
            for service_name in service_names:
                try:
                    service = psutil.win_service_get(service_name)
                    services.append({
                        "name": service.name(),
                        "display_name": service.display_name(),
                        "status": service.status(),
                        "start_type": service.start_type()
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.monitoring_data["services"] = services
            
        except Exception as e:
            self.logger.error(f"Error monitoring services: {e}")

    def _monitor_performance(self):
        """Monitor performance metrics"""
        try:
            # Performance history
            performance_data = {
                "timestamp": datetime.now().isoformat(),
                "cpu_usage": self.monitoring_data.get("system_status", {}).get("cpu_usage", 0),
                "memory_usage": self.monitoring_data.get("system_status", {}).get("memory_usage", 0),
                "chrome_processes": self.monitoring_data.get("processes", {}).get("chrome_count", 0),
                "python_processes": self.monitoring_data.get("processes", {}).get("python_count", 0)
            }
            
            self.monitoring_data["performance_history"].append(performance_data)
            
            # Keep only last 100 entries
            if len(self.monitoring_data["performance_history"]) > 100:
                self.monitoring_data["performance_history"] = self.monitoring_data["performance_history"][-100:]
            
        except Exception as e:
            self.logger.error(f"Error monitoring performance: {e}")

    def _check_alerts(self):
        """Check for alert conditions"""
        try:
            thresholds = self.config["alert_thresholds"]
            alerts = []
            
            # CPU usage alert
            cpu_usage = self.monitoring_data.get("system_status", {}).get("cpu_usage", 0)
            if cpu_usage > thresholds["cpu_usage"]:
                alerts.append({
                    "type": "high_cpu_usage",
                    "message": f"CPU usage is high: {cpu_usage:.1f}%",
                    "severity": "warning",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Memory usage alert
            memory_usage = self.monitoring_data.get("system_status", {}).get("memory_usage", 0)
            if memory_usage > thresholds["memory_usage"]:
                alerts.append({
                    "type": "high_memory_usage",
                    "message": f"Memory usage is high: {memory_usage:.1f}%",
                    "severity": "warning",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Chrome processes alert
            chrome_count = self.monitoring_data.get("processes", {}).get("chrome_count", 0)
            if chrome_count > thresholds["chrome_processes"]:
                alerts.append({
                    "type": "too_many_chrome_processes",
                    "message": f"Too many Chrome processes: {chrome_count}",
                    "severity": "info",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Python processes alert
            python_count = self.monitoring_data.get("processes", {}).get("python_count", 0)
            if python_count > thresholds["python_processes"]:
                alerts.append({
                    "type": "too_many_python_processes",
                    "message": f"Too many Python processes: {python_count}",
                    "severity": "info",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Add new alerts
            self.monitoring_data["alerts"].extend(alerts)
            
            # Keep only last 50 alerts
            if len(self.monitoring_data["alerts"]) > 50:
                self.monitoring_data["alerts"] = self.monitoring_data["alerts"][-50:]
            
            # Log alerts
            for alert in alerts:
                if alert["severity"] == "warning":
                    self.logger.warning(alert["message"])
                else:
                    self.logger.info(alert["message"])
            
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")

    def _save_monitoring_data(self):
        """Save monitoring data to file"""
        try:
            data_file = self.monitoring_dir / "monitoring_data.json"
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.monitoring_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving monitoring data: {e}")

    def get_monitoring_status(self):
        """Get current monitoring status"""
        try:
            return {
                "monitoring_enabled": self.config["monitoring_enabled"],
                "last_check": self.monitoring_data.get("last_check"),
                "system_status": self.monitoring_data.get("system_status", {}),
                "processes": self.monitoring_data.get("processes", {}),
                "alerts_count": len(self.monitoring_data.get("alerts", [])),
                "performance_history_count": len(self.monitoring_data.get("performance_history", []))
            }
        except Exception as e:
            self.logger.error(f"Error getting monitoring status: {e}")
            return {"error": str(e)}

    def get_alerts(self, limit=10):
        """Get recent alerts"""
        try:
            alerts = self.monitoring_data.get("alerts", [])
            return alerts[-limit:] if limit else alerts
        except Exception as e:
            self.logger.error(f"Error getting alerts: {e}")
            return []

    def clear_alerts(self):
        """Clear all alerts"""
        try:
            self.monitoring_data["alerts"] = []
            self._save_monitoring_data()
            self.logger.info("Alerts cleared")
        except Exception as e:
            self.logger.error(f"Error clearing alerts: {e}")

    def get_performance_history(self, hours=24):
        """Get performance history for specified hours"""
        try:
            history = self.monitoring_data.get("performance_history", [])
            if not history:
                return []
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            filtered_history = []
            
            for entry in history:
                try:
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if entry_time >= cutoff_time:
                        filtered_history.append(entry)
                except Exception:
                    continue
            
            return filtered_history
            
        except Exception as e:
            self.logger.error(f"Error getting performance history: {e}")
            return []

if __name__ == "__main__":
    monitoring_system = EnhancedMonitoringSystem()
    
    # Test monitoring
    print("Starting monitoring test...")
    time.sleep(5)  # Wait for initial check
    
    # Show status
    status = monitoring_system.get_monitoring_status()
    print("Monitoring Status:", json.dumps(status, indent=2))
    
    # Show alerts
    alerts = monitoring_system.get_alerts()
    print("Recent Alerts:", json.dumps(alerts, indent=2)) 