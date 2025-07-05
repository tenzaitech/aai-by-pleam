#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI - Windows Service
รันระบบตลอดเวลาแบบ Windows Service
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import time
import logging
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.system_monitor import SystemMonitor
from core.backup_manager import BackupManager
from conversation_logs.auto_logger.auto_logger import AutoLogger
from conversation_logs.monitoring_alert_system import MonitoringAlertSystem

class WawagotService(win32serviceutil.ServiceFramework):
    _svc_name_ = "WawagotAIService"
    _svc_display_name_ = "WAWAGOT.AI System Service"
    _svc_description_ = "AI-Powered Chrome Automation System Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = False
        
        # Setup logging
        logging.basicConfig(
            filename=os.path.join(project_root, 'logs', 'wawagot_service.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize components
        self.system_monitor = None
        self.backup_manager = None
        self.auto_logger = None
        self.alert_system = None

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False
        logging.info("WAWAGOT.AI Service stopping...")

    def SvcDoRun(self):
        """Run the service"""
        try:
            logging.info("WAWAGOT.AI Service starting...")
            self.running = True
            self.main()
        except Exception as e:
            logging.error(f"Service error: {e}")
            self.running = False

    def initialize_components(self):
        """Initialize all system components"""
        try:
            logging.info("Initializing system components...")
            
            # Initialize system monitor
            self.system_monitor = SystemMonitor()
            logging.info("System monitor initialized")
            
            # Initialize backup manager
            self.backup_manager = BackupManager()
            logging.info("Backup manager initialized")
            
            # Initialize auto logger
            self.auto_logger = AutoLogger()
            logging.info("Auto logger initialized")
            
            # Initialize alert system
            self.alert_system = MonitoringAlertSystem()
            logging.info("Alert system initialized")
            
            logging.info("All components initialized successfully")
            
        except Exception as e:
            logging.error(f"Component initialization error: {e}")
            raise

    def health_check(self):
        """Perform system health check"""
        try:
            # Check system resources
            cpu_usage = self.system_monitor.get_cpu_usage()
            memory_usage = self.system_monitor.get_memory_usage()
            
            # Log health status
            logging.info(f"Health check - CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%")
            
            # Alert if resources are high
            if cpu_usage > 80 or memory_usage > 80:
                self.alert_system.send_alert(
                    "High resource usage detected",
                    f"CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%"
                )
                
        except Exception as e:
            logging.error(f"Health check error: {e}")

    def backup_check(self):
        """Check and perform backups if needed"""
        try:
            if self.backup_manager.should_backup():
                logging.info("Starting scheduled backup...")
                self.backup_manager.create_backup()
                logging.info("Backup completed successfully")
                
        except Exception as e:
            logging.error(f"Backup error: {e}")

    def main(self):
        """Main service loop"""
        try:
            # Initialize components
            self.initialize_components()
            
            # Start monitoring threads
            health_thread = threading.Thread(target=self.health_monitor_loop, daemon=True)
            backup_thread = threading.Thread(target=self.backup_monitor_loop, daemon=True)
            
            health_thread.start()
            backup_thread.start()
            
            logging.info("WAWAGOT.AI Service running successfully")
            
            # Main service loop
            while self.running:
                # Check if service should stop
                if win32event.WaitForSingleObject(self.stop_event, 1000) == win32event.WAIT_OBJECT_0:
                    break
                    
                # Perform periodic tasks
                self.periodic_tasks()
                
        except Exception as e:
            logging.error(f"Main service error: {e}")
        finally:
            self.cleanup()

    def health_monitor_loop(self):
        """Health monitoring loop"""
        while self.running:
            try:
                self.health_check()
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logging.error(f"Health monitor error: {e}")
                time.sleep(60)

    def backup_monitor_loop(self):
        """Backup monitoring loop"""
        while self.running:
            try:
                self.backup_check()
                time.sleep(3600)  # Check every hour
            except Exception as e:
                logging.error(f"Backup monitor error: {e}")
                time.sleep(300)

    def periodic_tasks(self):
        """Perform periodic maintenance tasks"""
        try:
            # Log system status
            self.auto_logger.log_system_status()
            
            # Clean up old logs
            self.auto_logger.cleanup_old_logs()
            
        except Exception as e:
            logging.error(f"Periodic tasks error: {e}")

    def cleanup(self):
        """Cleanup resources"""
        try:
            logging.info("Cleaning up service resources...")
            
            # Stop all components
            if self.system_monitor:
                self.system_monitor.stop()
            
            if self.backup_manager:
                self.backup_manager.stop()
                
            if self.auto_logger:
                self.auto_logger.stop()
                
            if self.alert_system:
                self.alert_system.stop()
                
            logging.info("Service cleanup completed")
            
        except Exception as e:
            logging.error(f"Cleanup error: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(WawagotService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(WawagotService) 