#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI - Enhanced Integration Manager
ระบบ Integration Manager ที่รวม Backup และ Monitoring เข้าด้วยกัน
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
import logging
from core.logger import get_logger

# Import our enhanced systems
from enhanced_backup_manager import EnhancedBackupManager
from enhanced_monitoring_system import EnhancedMonitoringSystem

class EnhancedIntegrationManager:
    def __init__(self):
        self.logger = get_logger("integration_manager")
        self.project_root = Path(__file__).parent
        
        # Initialize systems
        self.backup_manager = None
        self.monitoring_system = None
        
        # Integration configuration
        self.config = {
            "integration_enabled": True,
            "auto_start": True,
            "health_check_interval": 300,  # 5 minutes
            "integration_features": {
                "backup_on_high_usage": True,
                "monitoring_alert_backup": True,
                "performance_optimization": True,
                "system_health_monitoring": True
            },
            "notification_settings": {
                "enable_notifications": True,
                "notification_level": "warning",  # info, warning, error
                "notification_channels": ["log", "file"]
            }
        }
        
        # Load configuration
        self.load_config()
        
        # Initialize systems
        self.initialize_systems()
        
        # Start integration
        if self.config["auto_start"]:
            self.start_integration()

    def load_config(self):
        """Load integration configuration"""
        config_file = self.project_root / "config" / "integration_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                self.logger.info("Loaded integration configuration")
            except Exception as e:
                self.logger.error(f"Error loading integration config: {e}")

    def save_config(self):
        """Save integration configuration"""
        config_file = self.project_root / "config" / "integration_config.json"
        config_file.parent.mkdir(exist_ok=True)
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info("Saved integration configuration")
        except Exception as e:
            self.logger.error(f"Error saving integration config: {e}")

    def initialize_systems(self):
        """Initialize backup and monitoring systems"""
        try:
            self.logger.info("Initializing backup and monitoring systems...")
            
            # Initialize backup manager
            self.backup_manager = EnhancedBackupManager()
            self.logger.info("Backup manager initialized")
            
            # Initialize monitoring system
            self.monitoring_system = EnhancedMonitoringSystem()
            self.logger.info("Monitoring system initialized")
            
            self.logger.info("All systems initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing systems: {e}")

    def start_integration(self):
        """Start integration services"""
        if not self.config["integration_enabled"]:
            self.logger.info("Integration disabled in configuration")
            return
        
        try:
            self.logger.info("Starting integration services...")
            
            # Start health check scheduler
            self.start_health_check_scheduler()
            
            # Start integration features
            if self.config["integration_features"]["backup_on_high_usage"]:
                self.start_backup_on_high_usage()
            
            if self.config["integration_features"]["monitoring_alert_backup"]:
                self.start_monitoring_alert_backup()
            
            if self.config["integration_features"]["performance_optimization"]:
                self.start_performance_optimization()
            
            self.logger.info("Integration services started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting integration services: {e}")

    def start_health_check_scheduler(self):
        """Start health check scheduler"""
        try:
            import schedule
            
            # Schedule health checks
            schedule.every(self.config["health_check_interval"]).seconds.do(self.perform_health_check)
            
            def run_health_check_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            
            health_check_thread = threading.Thread(target=run_health_check_scheduler, daemon=True)
            health_check_thread.start()
            self.logger.info("Health check scheduler started")
            
        except Exception as e:
            self.logger.error(f"Error starting health check scheduler: {e}")

    def start_backup_on_high_usage(self):
        """Start backup on high usage feature"""
        try:
            def check_and_backup():
                if not self.monitoring_system or not self.backup_manager:
                    return
                
                # Get system status
                status = self.monitoring_system.get_monitoring_status()
                system_status = status.get("system_status", {})
                
                # Check if backup is needed
                cpu_usage = system_status.get("cpu_usage", 0)
                memory_usage = system_status.get("memory_usage", 0)
                
                # Trigger backup if usage is high
                if cpu_usage > 90 or memory_usage > 90:
                    self.logger.warning(f"High system usage detected - CPU: {cpu_usage}%, Memory: {memory_usage}%")
                    self.logger.info("Triggering emergency backup...")
                    self.backup_manager.create_backup("config")
            
            # Schedule backup check every 10 minutes
            import schedule
            schedule.every(10).minutes.do(check_and_backup)
            
            self.logger.info("Backup on high usage feature started")
            
        except Exception as e:
            self.logger.error(f"Error starting backup on high usage: {e}")

    def start_monitoring_alert_backup(self):
        """Start monitoring alert backup feature"""
        try:
            def check_alerts_and_backup():
                if not self.monitoring_system or not self.backup_manager:
                    return
                
                # Get recent alerts
                alerts = self.monitoring_system.get_alerts(limit=5)
                
                # Check for critical alerts
                critical_alerts = [alert for alert in alerts if alert.get("severity") == "warning"]
                
                if len(critical_alerts) >= 3:
                    self.logger.warning(f"Multiple critical alerts detected: {len(critical_alerts)}")
                    self.logger.info("Triggering alert-based backup...")
                    self.backup_manager.create_backup("logs")
            
            # Schedule alert check every 5 minutes
            import schedule
            schedule.every(5).minutes.do(check_alerts_and_backup)
            
            self.logger.info("Monitoring alert backup feature started")
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring alert backup: {e}")

    def start_performance_optimization(self):
        """Start performance optimization feature"""
        try:
            def optimize_performance():
                if not self.monitoring_system:
                    return
                
                # Get performance history
                history = self.monitoring_system.get_performance_history(hours=1)
                
                if len(history) < 10:
                    return
                
                # Calculate average usage
                avg_cpu = sum(entry.get("cpu_usage", 0) for entry in history) / len(history)
                avg_memory = sum(entry.get("memory_usage", 0) for entry in history) / len(history)
                
                # Optimize if usage is consistently high
                if avg_cpu > 80 or avg_memory > 80:
                    self.logger.info("Performance optimization triggered")
                    self._perform_optimization()
            
            # Schedule optimization check every 15 minutes
            import schedule
            schedule.every(15).minutes.do(optimize_performance)
            
            self.logger.info("Performance optimization feature started")
            
        except Exception as e:
            self.logger.error(f"Error starting performance optimization: {e}")

    def _perform_optimization(self):
        """Perform system optimization"""
        try:
            self.logger.info("Performing system optimization...")
            
            # Clear old logs
            self._clear_old_logs()
            
            # Optimize monitoring data
            self._optimize_monitoring_data()
            
            # Trigger garbage collection
            import gc
            gc.collect()
            
            self.logger.info("System optimization completed")
            
        except Exception as e:
            self.logger.error(f"Error performing optimization: {e}")

    def _clear_old_logs(self):
        """Clear old log files"""
        try:
            log_dirs = ["logs", "conversation_logs/logs"]
            
            for log_dir in log_dirs:
                log_path = self.project_root / log_dir
                if log_path.exists():
                    # Remove log files older than 7 days
                    cutoff_time = datetime.now().timestamp() - (7 * 24 * 3600)
                    
                    for log_file in log_path.glob("*.log"):
                        if log_file.stat().st_mtime < cutoff_time:
                            log_file.unlink()
                            self.logger.info(f"Removed old log file: {log_file.name}")
            
        except Exception as e:
            self.logger.error(f"Error clearing old logs: {e}")

    def _optimize_monitoring_data(self):
        """Optimize monitoring data storage"""
        try:
            if not self.monitoring_system:
                return
            
            # Keep only last 50 performance history entries
            history = self.monitoring_system.get_performance_history(hours=24)
            if len(history) > 50:
                # This will be handled by the monitoring system itself
                pass
            
        except Exception as e:
            self.logger.error(f"Error optimizing monitoring data: {e}")

    def perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            self.logger.info("Performing integration health check...")
            
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "backup_system": self._check_backup_health(),
                "monitoring_system": self._check_monitoring_health(),
                "integration_status": "healthy"
            }
            
            # Check for issues
            issues = []
            
            if not health_status["backup_system"]["status"]:
                issues.append("Backup system issue")
                health_status["integration_status"] = "degraded"
            
            if not health_status["monitoring_system"]["status"]:
                issues.append("Monitoring system issue")
                health_status["integration_status"] = "degraded"
            
            if issues:
                self.logger.warning(f"Health check issues detected: {', '.join(issues)}")
            else:
                self.logger.info("Health check passed - all systems healthy")
            
            # Save health status
            self._save_health_status(health_status)
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Error performing health check: {e}")
            return {"error": str(e)}

    def _check_backup_health(self):
        """Check backup system health"""
        try:
            if not self.backup_manager:
                return {"status": False, "error": "Backup manager not initialized"}
            
            # Get backup status
            backup_status = self.backup_manager.get_backup_status()
            
            if "error" in backup_status:
                return {"status": False, "error": backup_status["error"]}
            
            # Check if backup is recent (within 24 hours)
            last_backup = backup_status.get("last_backup")
            if last_backup and last_backup != "Never":
                from datetime import datetime, timedelta
                last_backup_time = datetime.fromisoformat(last_backup)
                if datetime.now() - last_backup_time < timedelta(hours=24):
                    return {"status": True, "last_backup": last_backup}
                else:
                    return {"status": False, "error": "Backup is too old"}
            else:
                return {"status": False, "error": "No backup found"}
                
        except Exception as e:
            return {"status": False, "error": str(e)}

    def _check_monitoring_health(self):
        """Check monitoring system health"""
        try:
            if not self.monitoring_system:
                return {"status": False, "error": "Monitoring system not initialized"}
            
            # Get monitoring status
            monitoring_status = self.monitoring_system.get_monitoring_status()
            
            if "error" in monitoring_status:
                return {"status": False, "error": monitoring_status["error"]}
            
            # Check if monitoring is active
            if not monitoring_status.get("monitoring_enabled", False):
                return {"status": False, "error": "Monitoring disabled"}
            
            # Check if last check is recent (within 5 minutes)
            last_check = monitoring_status.get("last_check")
            if last_check:
                from datetime import datetime, timedelta
                last_check_time = datetime.fromisoformat(last_check)
                if datetime.now() - last_check_time < timedelta(minutes=5):
                    return {"status": True, "last_check": last_check}
                else:
                    return {"status": False, "error": "Monitoring check is too old"}
            else:
                return {"status": False, "error": "No monitoring check found"}
                
        except Exception as e:
            return {"status": False, "error": str(e)}

    def _save_health_status(self, health_status):
        """Save health status to file"""
        try:
            health_file = self.project_root / "monitoring" / "health_status.json"
            health_file.parent.mkdir(exist_ok=True)
            
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(health_status, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving health status: {e}")

    def get_integration_status(self):
        """Get comprehensive integration status"""
        try:
            return {
                "integration_enabled": self.config["integration_enabled"],
                "auto_start": self.config["auto_start"],
                "backup_system": {
                    "initialized": self.backup_manager is not None,
                    "status": self.backup_manager.get_backup_status() if self.backup_manager else None
                },
                "monitoring_system": {
                    "initialized": self.monitoring_system is not None,
                    "status": self.monitoring_system.get_monitoring_status() if self.monitoring_system else None
                },
                "features": self.config["integration_features"],
                "health_check_interval": self.config["health_check_interval"]
            }
        except Exception as e:
            self.logger.error(f"Error getting integration status: {e}")
            return {"error": str(e)}

    def manual_backup(self, backup_type="full"):
        """Trigger manual backup"""
        try:
            if not self.backup_manager:
                raise Exception("Backup manager not initialized")
            
            self.logger.info(f"Triggering manual {backup_type} backup...")
            success = self.backup_manager.create_backup(backup_type)
            
            if success:
                self.logger.info(f"Manual {backup_type} backup completed successfully")
                return {"status": "success", "type": backup_type}
            else:
                self.logger.error(f"Manual {backup_type} backup failed")
                return {"status": "failed", "type": backup_type}
                
        except Exception as e:
            self.logger.error(f"Error triggering manual backup: {e}")
            return {"status": "error", "error": str(e)}

    def get_system_alerts(self, limit=10):
        """Get system alerts"""
        try:
            if not self.monitoring_system:
                return []
            
            return self.monitoring_system.get_alerts(limit=limit)
            
        except Exception as e:
            self.logger.error(f"Error getting system alerts: {e}")
            return []

    def clear_system_alerts(self):
        """Clear system alerts"""
        try:
            if not self.monitoring_system:
                return False
            
            self.monitoring_system.clear_alerts()
            self.logger.info("System alerts cleared")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing system alerts: {e}")
            return False

if __name__ == "__main__":
    integration_manager = EnhancedIntegrationManager()
    
    # Test integration
    print("Testing integration manager...")
    time.sleep(3)  # Wait for initialization
    
    # Show status
    status = integration_manager.get_integration_status()
    print("Integration Status:", json.dumps(status, indent=2))
    
    # Perform health check
    health = integration_manager.perform_health_check()
    print("Health Check:", json.dumps(health, indent=2))
    
    # Show alerts
    alerts = integration_manager.get_system_alerts()
    print("System Alerts:", json.dumps(alerts, indent=2)) 