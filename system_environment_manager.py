# WAWAGOT.AI - System Environment Manager
# ===============================================================================
# WAWAGOT.AI - ระบบจัดการสภาพแวดล้อมทั้งหมด
# ===============================================================================
# Created: 2024-12-19
# Purpose: จัดการและตรวจสอบสภาพแวดล้อมระบบทั้งหมด
# ===============================================================================

import os
import sys
import psutil
import platform
import json
import asyncio
import logging
import subprocess
import shutil
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    TZ_BANGKOK = ZoneInfo("Asia/Bangkok")
except ImportError:
    import pytz
    TZ_BANGKOK = pytz.timezone("Asia/Bangkok")
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import time

# ===============================================================================
# ENVIRONMENT DATA STRUCTURES
# ===============================================================================

@dataclass
class SystemInfo:
    """ข้อมูลระบบพื้นฐาน"""
    os_name: str
    os_version: str
    architecture: str
    hostname: str
    python_version: str
    cpu_count: int
    total_memory: int
    total_disk: int

@dataclass
class ProcessInfo:
    """ข้อมูล Process"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: int
    status: str
    create_time: float

@dataclass
class NetworkInfo:
    """ข้อมูลเครือข่าย"""
    interface: str
    ip_address: str
    mac_address: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int

@dataclass
class EnvironmentVariable:
    """ข้อมูล Environment Variable"""
    name: str
    value: str
    source: str
    is_sensitive: bool

@dataclass
class ServiceStatus:
    """สถานะบริการ"""
    name: str
    status: str
    port: Optional[int]
    response_time: Optional[float]
    last_check: datetime

# ===============================================================================
# CORE ENVIRONMENT MANAGER
# ===============================================================================

class SystemEnvironmentManager:
    """ระบบจัดการสภาพแวดล้อมระบบทั้งหมด"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.system_info = None
        self.processes = {}
        self.network_info = {}
        self.env_vars = {}
        self.services = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "process_count": 100
        }
        
    def _setup_logger(self) -> logging.Logger:
        """ตั้งค่า Logger"""
        logger = logging.getLogger('SystemEnvironmentManager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize_system(self) -> Dict[str, Any]:
        """เริ่มต้นระบบและรวบรวมข้อมูลพื้นฐาน"""
        try:
            self.logger.info("เริ่มต้นระบบจัดการสภาพแวดล้อม")
            
            # รวบรวมข้อมูลระบบ
            self.system_info = await self._collect_system_info()
            
            # รวบรวมข้อมูล Process
            self.processes = await self._collect_process_info()
            
            # รวบรวมข้อมูลเครือข่าย
            self.network_info = await self._collect_network_info()
            
            # รวบรวม Environment Variables
            self.env_vars = await self._collect_environment_variables()
            
            # ตรวจสอบบริการ
            self.services = await self._check_services()
            
            # เริ่มการติดตาม
            await self.start_monitoring()
            
            return {
                "success": True,
                "message": "ระบบเริ่มต้นสำเร็จ",
                "system_info": asdict(self.system_info),
                "process_count": len(self.processes),
                "network_interfaces": len(self.network_info),
                "env_vars_count": len(self.env_vars),
                "services_count": len(self.services)
            }
            
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการเริ่มต้นระบบ: {e}")
            return {"success": False, "error": str(e)}
    
    async def _collect_system_info(self) -> SystemInfo:
        """รวบรวมข้อมูลระบบพื้นฐาน"""
        try:
            # ข้อมูลระบบปฏิบัติการ
            os_info = platform.uname()
            
            # ข้อมูล Python
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            
            # ข้อมูล CPU และ Memory
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return SystemInfo(
                os_name=os_info.system,
                os_version=os_info.release,
                architecture=os_info.machine,
                hostname=os_info.node,
                python_version=python_version,
                cpu_count=cpu_count,
                total_memory=memory.total,
                total_disk=disk.total
            )
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการรวบรวมข้อมูลระบบ: {e}")
            raise
    
    async def _collect_process_info(self) -> Dict[int, ProcessInfo]:
        """รวบรวมข้อมูล Process ทั้งหมด"""
        try:
            processes = {}
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status', 'create_time']):
                try:
                    proc_info = proc.info
                    processes[proc_info['pid']] = ProcessInfo(
                        pid=proc_info['pid'],
                        name=proc_info['name'],
                        cpu_percent=proc_info['cpu_percent'],
                        memory_percent=proc_info['memory_percent'],
                        memory_mb=proc_info['memory_info'].rss // 1024 // 1024,
                        status=proc_info['status'],
                        create_time=proc_info['create_time']
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return processes
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการรวบรวมข้อมูล Process: {e}")
            raise
    
    async def _collect_network_info(self) -> Dict[str, NetworkInfo]:
        """รวบรวมข้อมูลเครือข่าย"""
        try:
            network_info = {}
            
            for interface, stats in psutil.net_if_stats().items():
                try:
                    # ข้อมูล IP และ MAC
                    addrs = psutil.net_if_addrs().get(interface, [])
                    ip_address = ""
                    mac_address = ""
                    
                    for addr in addrs:
                        if addr.family == psutil.AF_INET:
                            ip_address = addr.address
                        elif addr.family == psutil.AF_LINK:
                            mac_address = addr.address
                    
                    # ข้อมูลสถิติเครือข่าย
                    net_io = psutil.net_io_counters(pernic=True).get(interface)
                    
                    if net_io:
                        network_info[interface] = NetworkInfo(
                            interface=interface,
                            ip_address=ip_address,
                            mac_address=mac_address,
                            bytes_sent=net_io.bytes_sent,
                            bytes_recv=net_io.bytes_recv,
                            packets_sent=net_io.packets_sent,
                            packets_recv=net_io.packets_recv
                        )
                except Exception:
                    continue
            
            return network_info
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการรวบรวมข้อมูลเครือข่าย: {e}")
            raise
    
    async def _collect_environment_variables(self) -> Dict[str, EnvironmentVariable]:
        """รวบรวม Environment Variables"""
        try:
            env_vars = {}
            sensitive_keys = ['password', 'secret', 'key', 'token', 'auth']
            
            for key, value in os.environ.items():
                is_sensitive = any(sensitive in key.lower() for sensitive in sensitive_keys)
                
                env_vars[key] = EnvironmentVariable(
                    name=key,
                    value=value if not is_sensitive else "***HIDDEN***",
                    source="system",
                    is_sensitive=is_sensitive
                )
            
            return env_vars
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการรวบรวม Environment Variables: {e}")
            raise
    
    async def _check_services(self) -> Dict[str, ServiceStatus]:
        """ตรวจสอบสถานะบริการ"""
        try:
            services = {}
            
            # ตรวจสอบบริการที่สำคัญ
            important_services = [
                {"name": "WAWAGOT.AI API", "port": 5000, "url": "http://localhost:5000/health"},
                {"name": "Dashboard", "port": 8080, "url": "http://localhost:8080/"},
                {"name": "Database", "port": 5432, "url": None},
                {"name": "Redis", "port": 6379, "url": None}
            ]
            
            for service in important_services:
                status = await self._check_service_status(service)
                services[service["name"]] = status
            
            return services
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการตรวจสอบบริการ: {e}")
            raise
    
    async def _check_service_status(self, service_config: Dict[str, Any]) -> ServiceStatus:
        """ตรวจสอบสถานะบริการเฉพาะ"""
        try:
            name = service_config["name"]
            port = service_config["port"]
            url = service_config.get("url")
            
            # ตรวจสอบ port
            port_status = await self._check_port(port)
            
            # ตรวจสอบ URL ถ้ามี
            response_time = None
            if url:
                response_time = await self._check_url(url)
            
            return ServiceStatus(
                name=name,
                status="running" if port_status else "stopped",
                port=port,
                response_time=response_time,
                last_check=datetime.now(TZ_BANGKOK)
            )
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการตรวจสอบบริการ {service_config['name']}: {e}")
            return ServiceStatus(
                name=service_config["name"],
                status="error",
                port=service_config["port"],
                response_time=None,
                last_check=datetime.now(TZ_BANGKOK)
            )
    
    async def _check_port(self, port: int) -> bool:
        """ตรวจสอบ port"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    async def _check_url(self, url: str) -> Optional[float]:
        """ตรวจสอบ URL และวัด response time"""
        try:
            import aiohttp
            import time
            
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        return time.time() - start_time
            return None
        except Exception:
            return None

# ===============================================================================
# MONITORING SYSTEM
# ===============================================================================

    async def start_monitoring(self):
        """เริ่มการติดตามระบบ"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            self.logger.info("เริ่มการติดตามระบบ")
    
    def stop_monitoring(self):
        """หยุดการติดตามระบบ"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        self.logger.info("หยุดการติดตามระบบ")
    
    def _monitoring_loop(self):
        """ลูปการติดตามระบบ"""
        while self.monitoring_active:
            try:
                asyncio.run(self._update_system_status())
                time.sleep(30)  # อัพเดททุก 30 วินาที
            except Exception as e:
                self.logger.error(f"เกิดข้อผิดพลาดในการติดตาม: {e}")
                time.sleep(60)  # รอ 1 นาทีถ้าเกิดข้อผิดพลาด
    
    async def _update_system_status(self):
        """อัพเดทสถานะระบบ"""
        try:
            # อัพเดทข้อมูล Process
            self.processes = await self._collect_process_info()
            
            # ตรวจสอบ alerts
            await self._check_alerts()
            
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการอัพเดทสถานะ: {e}")
    
    async def _check_alerts(self):
        """ตรวจสอบ alerts"""
        try:
            # ตรวจสอบ CPU usage
            cpu_percent = psutil.cpu_percent()
            if cpu_percent > self.alert_thresholds["cpu_usage"]:
                await self._send_alert("CPU Usage", f"CPU usage: {cpu_percent}%")
            
            # ตรวจสอบ Memory usage
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > self.alert_thresholds["memory_usage"]:
                await self._send_alert("Memory Usage", f"Memory usage: {memory_percent}%")
            
            # ตรวจสอบ Disk usage
            disk_percent = psutil.disk_usage('/').percent
            if disk_percent > self.alert_thresholds["disk_usage"]:
                await self._send_alert("Disk Usage", f"Disk usage: {disk_percent}%")
            
            # ตรวจสอบ Process count
            process_count = len(self.processes)
            if process_count > self.alert_thresholds["process_count"]:
                await self._send_alert("Process Count", f"Process count: {process_count}")
                
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการตรวจสอบ alerts: {e}")
    
    async def _send_alert(self, alert_type: str, message: str):
        """ส่ง alert"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now(TZ_BANGKOK).isoformat(),
            "severity": "warning"
        }
        self.logger.warning(f"ALERT: {alert_type} - {message}")
        # TODO: ส่ง alert ไปยังระบบแจ้งเตือน

# ===============================================================================
# ENVIRONMENT MANAGEMENT
# ===============================================================================

    async def get_system_status(self) -> Dict[str, Any]:
        """ดึงสถานะระบบทั้งหมด"""
        try:
            return {
                "success": True,
                "timestamp": datetime.now(TZ_BANGKOK).isoformat(),
                "system_info": asdict(self.system_info) if self.system_info else None,
                "performance": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent,
                    "process_count": len(self.processes)
                },
                "processes": {pid: asdict(proc) for pid, proc in self.processes.items()},
                "network": {name: asdict(net) for name, net in self.network_info.items()},
                "environment_variables": {name: asdict(env) for name, env in self.env_vars.items()},
                "services": {name: asdict(service) for name, service in self.services.items()},
                "monitoring_active": self.monitoring_active
            }
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการดึงสถานะระบบ: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_environment_variable(self, name: str, value: str, source: str = "user") -> Dict[str, Any]:
        """ตั้งค่า Environment Variable"""
        try:
            # ตั้งค่าในระบบ
            os.environ[name] = value
            
            # อัพเดทใน cache
            self.env_vars[name] = EnvironmentVariable(
                name=name,
                value=value,
                source=source,
                is_sensitive=any(sensitive in name.lower() for sensitive in ['password', 'secret', 'key', 'token', 'auth'])
            )
            
            self.logger.info(f"ตั้งค่า Environment Variable: {name}")
            return {"success": True, "message": f"ตั้งค่า {name} สำเร็จ"}
            
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการตั้งค่า Environment Variable: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_environment_variable(self, name: str) -> Dict[str, Any]:
        """ดึง Environment Variable"""
        try:
            if name in self.env_vars:
                env_var = self.env_vars[name]
                return {
                    "success": True,
                    "name": env_var.name,
                    "value": env_var.value,
                    "source": env_var.source,
                    "is_sensitive": env_var.is_sensitive
                }
            else:
                return {"success": False, "error": f"Environment Variable {name} ไม่พบ"}
                
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการดึง Environment Variable: {e}")
            return {"success": False, "error": str(e)}
    
    async def optimize_environment(self) -> Dict[str, Any]:
        """ปรับปรุงสภาพแวดล้อม"""
        try:
            optimizations = []
            
            # ตรวจสอบและปรับปรุง Memory
            memory_optimization = await self._optimize_memory()
            optimizations.append(memory_optimization)
            
            # ตรวจสอบและปรับปรุง Process
            process_optimization = await self._optimize_processes()
            optimizations.append(process_optimization)
            
            # ตรวจสอบและปรับปรุง Disk
            disk_optimization = await self._optimize_disk()
            optimizations.append(disk_optimization)
            
            return {
                "success": True,
                "message": "ปรับปรุงสภาพแวดล้อมสำเร็จ",
                "optimizations": optimizations
            }
            
        except Exception as e:
            self.logger.error(f"เกิดข้อผิดพลาดในการปรับปรุงสภาพแวดล้อม: {e}")
            return {"success": False, "error": str(e)}
    
    async def _optimize_memory(self) -> Dict[str, Any]:
        """ปรับปรุง Memory"""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > 80:
                # ล้าง cache ถ้าจำเป็น
                import gc
                gc.collect()
                
                return {
                    "type": "memory",
                    "action": "garbage_collection",
                    "before_percent": memory.percent,
                    "after_percent": psutil.virtual_memory().percent
                }
            
            return {
                "type": "memory",
                "action": "no_action_needed",
                "current_percent": memory.percent
            }
            
        except Exception as e:
            return {"type": "memory", "action": "error", "error": str(e)}
    
    async def _optimize_processes(self) -> Dict[str, Any]:
        """ปรับปรุง Process"""
        try:
            # หา process ที่ใช้ CPU สูง
            high_cpu_processes = []
            for pid, proc in self.processes.items():
                if proc.cpu_percent > 50:
                    high_cpu_processes.append({
                        "pid": pid,
                        "name": proc.name,
                        "cpu_percent": proc.cpu_percent
                    })
            
            return {
                "type": "processes",
                "action": "monitoring",
                "high_cpu_processes": high_cpu_processes,
                "total_processes": len(self.processes)
            }
            
        except Exception as e:
            return {"type": "processes", "action": "error", "error": str(e)}
    
    async def _optimize_disk(self) -> Dict[str, Any]:
        """ปรับปรุง Disk"""
        try:
            disk = psutil.disk_usage('/')
            
            if disk.percent > 90:
                return {
                    "type": "disk",
                    "action": "warning",
                    "usage_percent": disk.percent,
                    "free_space_gb": disk.free // 1024 // 1024 // 1024
                }
            
            return {
                "type": "disk",
                "action": "no_action_needed",
                "usage_percent": disk.percent
            }
            
        except Exception as e:
            return {"type": "disk", "action": "error", "error": str(e)}

# ===============================================================================
# MAIN EXECUTION
# ===============================================================================

async def main():
    """ฟังก์ชันหลัก"""
    # สร้าง Environment Manager
    env_manager = SystemEnvironmentManager()
    
    # เริ่มต้นระบบ
    init_result = await env_manager.initialize_system()
    print("ผลการเริ่มต้นระบบ:", json.dumps(init_result, indent=2, ensure_ascii=False))
    
    if init_result["success"]:
        # ดึงสถานะระบบ
        status = await env_manager.get_system_status()
        print("\nสถานะระบบ:", json.dumps(status, indent=2, ensure_ascii=False))
        
        # ปรับปรุงสภาพแวดล้อม
        optimization = await env_manager.optimize_environment()
        print("\nผลการปรับปรุง:", json.dumps(optimization, indent=2, ensure_ascii=False))
    
    # รอสักครู่เพื่อดูการติดตาม
    print("\nกำลังติดตามระบบ... (กด Ctrl+C เพื่อหยุด)")
    try:
        await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\nหยุดการทำงาน...")
        env_manager.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 