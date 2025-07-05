#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI - Enhanced Service Manager
ระบบ Service Manager ที่รวมระบบ Backup, Monitoring และ Integration เข้าด้วยกัน
"""

import os
import json
import time
import threading
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
from datetime import datetime
from pathlib import Path
import logging
from core.logger import get_logger

# Import our enhanced systems
from enhanced_backup_manager import EnhancedBackupManager
from enhanced_monitoring_system import EnhancedMonitoringSystem
from enhanced_integration_manager import EnhancedIntegrationManager

class WawagotService(win32serviceutil.ServiceFramework):
    _svc_name_ = "WawagotService"
    _svc_display_name_ = "WAWAGOT.AI Enhanced Service"
    _svc_description_ = "Enhanced Backup, Monitoring and Integration Service for WAWAGOT.AI"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        
        # Initialize logger
        self.logger = get_logger("wawagot_service")
        
        # Initialize systems
        self.backup_manager = None
        self.monitoring_system = None
        self.integration_manager = None
        
        # Service status
        self.service_running = False
        self.service_start_time = None

    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.service_running = False

    def SvcDoRun(self):
        """Run the service"""
        try:
            self.logger.info("Starting WAWAGOT.AI Enhanced Service...")
            self.service_start_time = datetime.now()
            self.service_running = True
            
            # Initialize systems
            self.initialize_systems()
            
            # Start service loop
            self.run_service()
            
        except Exception as e:
            self.logger.error(f"Service failed to start: {e}")
            self.service_running = False

    def initialize_systems(self):
        """Initialize all systems"""
        try:
            self.logger.info("Initializing all systems...")
            
            # Initialize backup manager
            self.backup_manager = EnhancedBackupManager()
            self.logger.info("Backup manager initialized")
            
            # Initialize monitoring system
            self.monitoring_system = EnhancedMonitoringSystem()
            self.logger.info("Monitoring system initialized")
            
            # Initialize integration manager
            self.integration_manager = EnhancedIntegrationManager()
            self.logger.info("Integration manager initialized")
            
            self.logger.info("All systems initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing systems: {e}")
            raise

    def run_service(self):
        """Main service loop"""
        try:
            self.logger.info("Service is running...")
            
            # Perform initial health check
            self.perform_health_check()
            
            # Main service loop
            while self.service_running:
                try:
                    # Check for stop event
                    if win32event.WaitForSingleObject(self.stop_event, 5000) == win32event.WAIT_OBJECT_0:
                        break
                    
                    # Perform periodic health check
                    self.perform_health_check()
                    
                    # Sleep for a bit
                    time.sleep(30)
                    
                except Exception as e:
                    self.logger.error(f"Error in service loop: {e}")
                    time.sleep(60)  # Wait longer on error
            
            self.logger.info("Service loop ended")
            
        except Exception as e:
            self.logger.error(f"Service loop failed: {e}")

    def perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "service_running": self.service_running,
                "service_uptime": self.get_service_uptime(),
                "systems": {}
            }
            
            # Check backup system
            if self.backup_manager:
                backup_status = self.backup_manager.get_backup_status()
                health_status["systems"]["backup"] = {
                    "status": "healthy" if "error" not in backup_status else "error",
                    "last_backup": backup_status.get("last_backup", "Never"),
                    "backup_count": backup_status.get("backup_count", 0)
                }
            
            # Check monitoring system
            if self.monitoring_system:
                monitoring_status = self.monitoring_system.get_monitoring_status()
                health_status["systems"]["monitoring"] = {
                    "status": "healthy" if "error" not in monitoring_status else "error",
                    "last_check": monitoring_status.get("last_check"),
                    "alerts_count": monitoring_status.get("alerts_count", 0)
                }
            
            # Check integration system
            if self.integration_manager:
                integration_status = self.integration_manager.get_integration_status()
                health_status["systems"]["integration"] = {
                    "status": "healthy" if "error" not in integration_status else "error",
                    "enabled": integration_status.get("integration_enabled", False)
                }
            
            # Save health status
            self.save_health_status(health_status)
            
            # Log health status
            self.log_health_status(health_status)
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Error performing health check: {e}")
            return {"error": str(e)}

    def get_service_uptime(self):
        """Get service uptime"""
        if self.service_start_time:
            uptime = datetime.now() - self.service_start_time
            return str(uptime).split('.')[0]  # Remove microseconds
        return "Unknown"

    def save_health_status(self, health_status):
        """Save health status to file"""
        try:
            health_file = Path(__file__).parent / "monitoring" / "service_health.json"
            health_file.parent.mkdir(exist_ok=True)
            
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(health_status, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving health status: {e}")

    def log_health_status(self, health_status):
        """Log health status"""
        try:
            # Check for issues
            issues = []
            
            for system_name, system_status in health_status.get("systems", {}).items():
                if system_status.get("status") == "error":
                    issues.append(f"{system_name} system error")
            
            if issues:
                self.logger.warning(f"Health check issues: {', '.join(issues)}")
            else:
                self.logger.info("Health check passed - all systems healthy")
                
        except Exception as e:
            self.logger.error(f"Error logging health status: {e}")

class EnhancedServiceManager:
    def __init__(self):
        self.logger = get_logger("service_manager")
        self.service_name = "WawagotService"
        self.service_display_name = "WAWAGOT.AI Enhanced Service"

    def install_service(self):
        """Install the service"""
        try:
            self.logger.info("Installing service...")
            win32serviceutil.InstallService(
                None,
                self.service_name,
                self.service_display_name,
                startType=win32service.SERVICE_AUTO_START
            )
            self.logger.info("Service installed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error installing service: {e}")
            return False

    def uninstall_service(self):
        """Uninstall the service"""
        try:
            self.logger.info("Uninstalling service...")
            win32serviceutil.RemoveService(self.service_name)
            self.logger.info("Service uninstalled successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error uninstalling service: {e}")
            return False

    def start_service(self):
        """Start the service"""
        try:
            self.logger.info("Starting service...")
            win32serviceutil.StartService(self.service_name)
            self.logger.info("Service started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error starting service: {e}")
            return False

    def stop_service(self):
        """Stop the service"""
        try:
            self.logger.info("Stopping service...")
            win32serviceutil.StopService(self.service_name)
            self.logger.info("Service stopped successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping service: {e}")
            return False

    def restart_service(self):
        """Restart the service"""
        try:
            self.logger.info("Restarting service...")
            win32serviceutil.RestartService(self.service_name)
            self.logger.info("Service restarted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error restarting service: {e}")
            return False

    def get_service_status(self):
        """Get service status"""
        try:
            status = win32serviceutil.QueryServiceStatus(self.service_name)
            status_map = {
                win32service.SERVICE_RUNNING: "Running",
                win32service.SERVICE_STOPPED: "Stopped",
                win32service.SERVICE_START_PENDING: "Starting",
                win32service.SERVICE_STOP_PENDING: "Stopping"
            }
            return status_map.get(status[1], "Unknown")
        except Exception as e:
            self.logger.error(f"Error getting service status: {e}")
            return "Error"

    def get_service_info(self):
        """Get comprehensive service information"""
        try:
            return {
                "service_name": self.service_name,
                "display_name": self.service_display_name,
                "status": self.get_service_status(),
                "installed": self.is_service_installed(),
                "auto_start": self.is_auto_start()
            }
        except Exception as e:
            self.logger.error(f"Error getting service info: {e}")
            return {"error": str(e)}

    def is_service_installed(self):
        """Check if service is installed"""
        try:
            win32serviceutil.QueryServiceStatus(self.service_name)
            return True
        except Exception:
            return False

    def is_auto_start(self):
        """Check if service is set to auto start"""
        try:
            # This would require additional registry checking
            # For now, return True if service is installed
            return self.is_service_installed()
        except Exception:
            return False

def main():
    """Main function for command line usage"""
    import sys
    
    if len(sys.argv) == 1:
        # Run as service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(WawagotService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Command line usage
        service_manager = EnhancedServiceManager()
        
        if sys.argv[1] == "install":
            service_manager.install_service()
        elif sys.argv[1] == "uninstall":
            service_manager.uninstall_service()
        elif sys.argv[1] == "start":
            service_manager.start_service()
        elif sys.argv[1] == "stop":
            service_manager.stop_service()
        elif sys.argv[1] == "restart":
            service_manager.restart_service()
        elif sys.argv[1] == "status":
            info = service_manager.get_service_info()
            print(json.dumps(info, indent=2))
        else:
            print("Usage: python enhanced_service_manager.py [install|uninstall|start|stop|restart|status]")

if __name__ == "__main__":
    main() 