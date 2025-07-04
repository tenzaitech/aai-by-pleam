#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Monitor Launcher - เริ่มต้นระบบ real-time monitoring
Launch script สำหรับระบบ real-time logging และ workflow monitoring
"""

import os
import sys
import time
import threading
import subprocess
import signal
import json
from datetime import datetime
from pathlib import Path

# เพิ่ม path สำหรับ import
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir / "core" / "logging"))

class RealTimeMonitorLauncher:
    """Launcher สำหรับ real-time monitor"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
        self.config = {
            "dashboard_port": 5000,
            "api_port": 8000,
            "log_level": "DEBUG",
            "auto_cleanup": True,
            "cleanup_interval": 3600,  # 1 ชั่วโมง
            "max_logs": 10000,
            "max_workflows": 1000,
            "max_alerts": 500
        }
        
        # โหลด config จากไฟล์
        self.load_config()
        
        print("🚀 Real-time Monitor Launcher initialized")
    
    def load_config(self):
        """โหลด configuration"""
        config_file = current_dir / "config" / "monitor_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
                print("✅ Configuration loaded from file")
            except Exception as e:
                print(f"⚠️ Error loading config: {e}")
        else:
            print("ℹ️ Using default configuration")
    
    def save_config(self):
        """บันทึก configuration"""
        config_file = current_dir / "config" / "monitor_config.json"
        config_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print("✅ Configuration saved")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def start_logging_system(self):
        """เริ่มต้นระบบ logging"""
        try:
            print("📝 Starting logging system...")
            
            # Import และเริ่มต้น logging components
            from logger_manager import get_logger_manager
            from workflow_monitor import get_workflow_monitor
            from performance_tracker import get_performance_tracker
            from alert_system import get_alert_system
            
            # เริ่มต้น components
            logger_manager = get_logger_manager()
            workflow_monitor = get_workflow_monitor()
            performance_tracker = get_performance_tracker()
            alert_system = get_alert_system()
            
            # บันทึก log เริ่มต้น
            logger_manager.log(
                module="launcher",
                level="info",
                message="Real-time monitor launcher started",
                metadata={"config": self.config}
            )
            
            print("✅ Logging system started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error starting logging system: {e}")
            return False
    
    def start_dashboard(self):
        """เริ่มต้น dashboard"""
        try:
            print(f"🌐 Starting dashboard on port {self.config['dashboard_port']}...")
            
            # เปลี่ยนไปยังโฟลเดอร์ dashboard
            dashboard_dir = current_dir / "dashboard"
            if not dashboard_dir.exists():
                print(f"❌ Dashboard directory not found: {dashboard_dir}")
                return False
            
            # เริ่มต้น Flask app
            dashboard_script = dashboard_dir / "app.py"
            if not dashboard_script.exists():
                print(f"❌ Dashboard script not found: {dashboard_script}")
                return False
            
            # เริ่มต้น process
            env = os.environ.copy()
            env["FLASK_ENV"] = "development"
            env["FLASK_DEBUG"] = "1"
            
            process = subprocess.Popen(
                [sys.executable, str(dashboard_script)],
                cwd=str(dashboard_dir),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["dashboard"] = process
            
            # รอให้ dashboard เริ่มต้น
            time.sleep(3)
            
            if process.poll() is None:
                print(f"✅ Dashboard started on http://localhost:{self.config['dashboard_port']}")
                return True
            else:
                print("❌ Dashboard failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting dashboard: {e}")
            return False
    
    def start_api_server(self):
        """เริ่มต้น API server"""
        try:
            print(f"🔌 Starting API server on port {self.config['api_port']}...")
            
            # เริ่มต้น FastAPI server
            api_script = current_dir / "api_server.py"
            if not api_script.exists():
                print(f"ℹ️ API server script not found, skipping...")
                return True
            
            env = os.environ.copy()
            env["API_PORT"] = str(self.config["api_port"])
            
            process = subprocess.Popen(
                [sys.executable, str(api_script)],
                cwd=str(current_dir),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes["api_server"] = process
            
            # รอให้ API server เริ่มต้น
            time.sleep(2)
            
            if process.poll() is None:
                print(f"✅ API server started on http://localhost:{self.config['api_port']}")
                return True
            else:
                print("❌ API server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting API server: {e}")
            return False
    
    def start_background_tasks(self):
        """เริ่มต้น background tasks"""
        try:
            print("🔄 Starting background tasks...")
            
            # เริ่มต้น cleanup task
            if self.config["auto_cleanup"]:
                cleanup_thread = threading.Thread(
                    target=self.cleanup_task,
                    daemon=True
                )
                cleanup_thread.start()
                print("✅ Cleanup task started")
            
            # เริ่มต้น monitoring task
            monitor_thread = threading.Thread(
                target=self.monitoring_task,
                daemon=True
            )
            monitor_thread.start()
            print("✅ Monitoring task started")
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting background tasks: {e}")
            return False
    
    def cleanup_task(self):
        """Background task สำหรับ cleanup"""
        while self.running:
            try:
                time.sleep(self.config["cleanup_interval"])
                
                print("🧹 Running scheduled cleanup...")
                
                # Cleanup logs
                from logger_manager import get_logger_manager
                logger_manager = get_logger_manager()
                logger_manager.cleanup_old_logs()
                
                # Cleanup alerts
                from alert_system import get_alert_system
                alert_system = get_alert_system()
                # (alert system จะ cleanup เอง)
                
                print("✅ Cleanup completed")
                
            except Exception as e:
                print(f"❌ Cleanup error: {e}")
    
    def monitoring_task(self):
        """Background task สำหรับ monitoring"""
        while self.running:
            try:
                time.sleep(30)  # ตรวจสอบทุก 30 วินาที
                
                # ตรวจสอบสถานะ processes
                for name, process in self.processes.items():
                    if process.poll() is not None:
                        print(f"⚠️ {name} process has stopped, restarting...")
                        self.restart_process(name)
                
                # ตรวจสอบระบบ resources
                self.check_system_resources()
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
    
    def restart_process(self, process_name):
        """restart process"""
        try:
            if process_name == "dashboard":
                self.stop_process(process_name)
                time.sleep(2)
                self.start_dashboard()
            elif process_name == "api_server":
                self.stop_process(process_name)
                time.sleep(2)
                self.start_api_server()
        except Exception as e:
            print(f"❌ Error restarting {process_name}: {e}")
    
    def check_system_resources(self):
        """ตรวจสอบระบบ resources"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            if cpu_percent > 80:
                print(f"⚠️ High CPU usage: {cpu_percent:.1f}%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                print(f"⚠️ High memory usage: {memory.percent:.1f}%")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                print(f"⚠️ High disk usage: {disk.percent:.1f}%")
                
        except Exception as e:
            print(f"❌ Error checking system resources: {e}")
    
    def start_all(self):
        """เริ่มต้นระบบทั้งหมด"""
        print("\n" + "="*60)
        print("🚀 STARTING REAL-TIME MONITOR SYSTEM")
        print("="*60)
        
        self.running = True
        
        # เริ่มต้น logging system
        if not self.start_logging_system():
            print("❌ Failed to start logging system")
            return False
        
        # เริ่มต้น dashboard
        if not self.start_dashboard():
            print("❌ Failed to start dashboard")
            return False
        
        # เริ่มต้น API server
        if not self.start_api_server():
            print("⚠️ API server not started, continuing...")
        
        # เริ่มต้น background tasks
        if not self.start_background_tasks():
            print("⚠️ Background tasks not started, continuing...")
        
        print("\n" + "="*60)
        print("✅ REAL-TIME MONITOR SYSTEM STARTED SUCCESSFULLY")
        print("="*60)
        print(f"🌐 Dashboard: http://localhost:{self.config['dashboard_port']}")
        print(f"📊 Real-time Monitor: http://localhost:{self.config['dashboard_port']}/real-time-monitor")
        if self.config.get('api_port'):
            print(f"🔌 API Server: http://localhost:{self.config['api_port']}")
        print("="*60)
        
        return True
    
    def stop_process(self, process_name):
        """หยุด process"""
        if process_name in self.processes:
            process = self.processes[process_name]
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {process_name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ {process_name} force killed")
            except Exception as e:
                print(f"❌ Error stopping {process_name}: {e}")
            finally:
                del self.processes[process_name]
    
    def stop_all(self):
        """หยุดระบบทั้งหมด"""
        print("\n🛑 Stopping Real-time Monitor System...")
        
        self.running = False
        
        # หยุด processes ทั้งหมด
        for process_name in list(self.processes.keys()):
            self.stop_process(process_name)
        
        # บันทึก log สิ้นสุด
        try:
            from logger_manager import get_logger_manager
            logger_manager = get_logger_manager()
            logger_manager.log(
                module="launcher",
                level="info",
                message="Real-time monitor launcher stopped"
            )
        except:
            pass
        
        print("✅ Real-time Monitor System stopped")
    
    def show_status(self):
        """แสดงสถานะระบบ"""
        print("\n📊 SYSTEM STATUS")
        print("="*40)
        
        # สถานะ processes
        print("Processes:")
        for name, process in self.processes.items():
            status = "Running" if process.poll() is None else "Stopped"
            print(f"  {name}: {status}")
        
        # สถานะ logging system
        try:
            from logger_manager import get_logger_manager
            from workflow_monitor import get_workflow_monitor
            from performance_tracker import get_performance_tracker
            from alert_system import get_alert_system
            
            logger_manager = get_logger_manager()
            workflow_monitor = get_workflow_monitor()
            performance_tracker = get_performance_tracker()
            alert_system = get_alert_system()
            
            print("\nLogging System:")
            print(f"  Logger Manager: Active")
            print(f"  Workflow Monitor: Active")
            print(f"  Performance Tracker: Active")
            print(f"  Alert System: Active")
            
            # สถิติ
            logs = logger_manager.get_recent_logs(limit=1)
            workflows = workflow_monitor.get_active_workflows()
            alerts = alert_system.get_active_alerts()
            
            print(f"\nStatistics:")
            print(f"  Recent Logs: {len(logs)}")
            print(f"  Active Workflows: {len(workflows)}")
            print(f"  Active Alerts: {len(alerts)}")
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
    
    def run_interactive(self):
        """รันในโหมด interactive"""
        print("\n🎮 Interactive Mode")
        print("Commands:")
        print("  status - Show system status")
        print("  restart - Restart all services")
        print("  cleanup - Run manual cleanup")
        print("  config - Show configuration")
        print("  quit - Exit")
        
        while self.running:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "status":
                    self.show_status()
                elif command == "restart":
                    print("🔄 Restarting all services...")
                    self.stop_all()
                    time.sleep(2)
                    self.start_all()
                elif command == "cleanup":
                    print("🧹 Running manual cleanup...")
                    try:
                        from logger_manager import get_logger_manager
                        logger_manager = get_logger_manager()
                        logger_manager.cleanup_old_logs()
                        print("✅ Cleanup completed")
                    except Exception as e:
                        print(f"❌ Cleanup error: {e}")
                elif command == "config":
                    print("⚙️ Configuration:")
                    for key, value in self.config.items():
                        print(f"  {key}: {value}")
                elif command == "quit":
                    break
                else:
                    print("❓ Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def signal_handler(signum, frame):
    """Handle system signals"""
    print(f"\n🛑 Received signal {signum}, shutting down...")
    if launcher:
        launcher.stop_all()
    sys.exit(0)


def main():
    """Main function"""
    global launcher
    
    # ตั้งค่า signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # สร้าง launcher
    launcher = RealTimeMonitorLauncher()
    
    try:
        # เริ่มต้นระบบ
        if launcher.start_all():
            # รันในโหมด interactive
            launcher.run_interactive()
        else:
            print("❌ Failed to start system")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if launcher:
            launcher.stop_all()


if __name__ == "__main__":
    launcher = None
    main() 