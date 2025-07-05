# WAWAGOT.AI - Environment Quick Check
# ===============================================================================
# WAWAGOT.AI - เครื่องมือตรวจสอบสภาพแวดล้อมแบบรวดเร็ว
# ===============================================================================
# Created: 2024-12-19
# Purpose: ตรวจสอบสภาพแวดล้อมทั้งหมดแบบง่ายและรวดเร็ว
# ===============================================================================

import os
import sys
import psutil
import platform
import json
import asyncio
import subprocess
import shutil
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    TZ_BANGKOK = ZoneInfo("Asia/Bangkok")
except ImportError:
    import pytz
    TZ_BANGKOK = pytz.timezone("Asia/Bangkok")
from typing import Dict, List, Any, Tuple
import time

# ===============================================================================
# QUICK CHECK FUNCTIONS
# ===============================================================================

class EnvironmentQuickCheck:
    """เครื่องมือตรวจสอบสภาพแวดล้อมแบบรวดเร็ว"""
    
    def __init__(self):
        self.check_results = {}
        self.issues = []
        self.recommendations = []
    
    async def run_full_check(self) -> Dict[str, Any]:
        """ตรวจสอบสภาพแวดล้อมทั้งหมด"""
        print("🔍 เริ่มตรวจสอบสภาพแวดล้อม WAWAGOT.AI...")
        print("=" * 60)
        
        # ตรวจสอบระบบพื้นฐาน
        await self._check_system_basics()
        
        # ตรวจสอบ Python Environment
        await self._check_python_environment()
        
        # ตรวจสอบ Dependencies
        await self._check_dependencies()
        
        # ตรวจสอบ Network
        await self._check_network()
        
        # ตรวจสอบ Services
        await self._check_services()
        
        # ตรวจสอบ Storage
        await self._check_storage()
        
        # ตรวจสอบ Performance
        await self._check_performance()
        
        # ตรวจสอบ Security
        await self._check_security()
        
        # สรุปผลการตรวจสอบ
        return self._generate_summary()
    
    async def _check_system_basics(self):
        """ตรวจสอบระบบพื้นฐาน"""
        print("\n💻 ตรวจสอบระบบพื้นฐาน...")
        
        try:
            # ข้อมูลระบบปฏิบัติการ
            os_info = platform.uname()
            self.check_results["system"] = {
                "os_name": os_info.system,
                "os_version": os_info.release,
                "architecture": os_info.machine,
                "hostname": os_info.node,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            }
            
            # ข้อมูลฮาร์ดแวร์
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.check_results["hardware"] = {
                "cpu_count": cpu_count,
                "total_memory_gb": round(memory.total / 1024 / 1024 / 1024, 2),
                "available_memory_gb": round(memory.available / 1024 / 1024 / 1024, 2),
                "total_disk_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                "free_disk_gb": round(disk.free / 1024 / 1024 / 1024, 2)
            }
            
            print(f"   ✅ OS: {os_info.system} {os_info.release}")
            print(f"   ✅ Architecture: {os_info.machine}")
            print(f"   ✅ CPU Cores: {cpu_count}")
            print(f"   ✅ Memory: {self.check_results['hardware']['total_memory_gb']} GB")
            print(f"   ✅ Disk: {self.check_results['hardware']['total_disk_gb']} GB")
            
        except Exception as e:
            self.issues.append(f"เกิดข้อผิดพลาดในการตรวจสอบระบบพื้นฐาน: {e}")
            print(f"   ❌ เกิดข้อผิดพลาด: {e}")
    
    async def _check_python_environment(self):
        """ตรวจสอบ Python Environment"""
        print("\n🐍 ตรวจสอบ Python Environment...")
        
        try:
            # ตรวจสอบ Python version
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                self.issues.append("Python version ต้องเป็น 3.8 หรือสูงกว่า")
                print(f"   ❌ Python version: {python_version.major}.{python_version.minor}.{python_version.micro} (ต้องเป็น 3.8+)")
            else:
                print(f"   ✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
            
            # ตรวจสอบ Virtual Environment
            if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                print("   ✅ Virtual Environment: ใช้งานอยู่")
                self.check_results["virtual_env"] = True
            else:
                print("   ⚠️ Virtual Environment: ไม่พบ (แนะนำให้ใช้)")
                self.recommendations.append("ใช้ Virtual Environment เพื่อแยก dependencies")
                self.check_results["virtual_env"] = False
            
            # ตรวจสอบ Python path
            python_path = sys.executable
            print(f"   ✅ Python Path: {python_path}")
            self.check_results["python_path"] = python_path
            
        except Exception as e:
            self.issues.append(f"เกิดข้อผิดพลาดในการตรวจสอบ Python Environment: {e}")
            print(f"   ❌ เกิดข้อผิดพลาด: {e}")
    
    async def _check_dependencies(self):
        """ตรวจสอบ Dependencies"""
        print("\n📦 ตรวจสอบ Dependencies...")
        
        required_packages = [
            "flask", "fastapi", "requests", "aiohttp", "psutil",
            "selenium", "playwright", "openai", "google-generativeai",
            "supabase", "redis", "pandas", "numpy", "tensorflow", "torch"
        ]
        
        missing_packages = []
        installed_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                installed_packages.append(package)
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package} (ไม่พบ)")
        
        self.check_results["dependencies"] = {
            "installed": installed_packages,
            "missing": missing_packages,
            "total_required": len(required_packages),
            "total_installed": len(installed_packages)
        }
        
        if missing_packages:
            self.issues.append(f"ขาด Dependencies: {', '.join(missing_packages)}")
            self.recommendations.append(f"ติดตั้ง packages ที่ขาด: pip install {' '.join(missing_packages)}")
    
    async def _check_network(self):
        """ตรวจสอบเครือข่าย"""
        print("\n🌐 ตรวจสอบเครือข่าย...")
        
        try:
            # ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
            import urllib.request
            try:
                urllib.request.urlopen('http://www.google.com', timeout=5)
                print("   ✅ Internet Connection: เชื่อมต่อได้")
                self.check_results["internet"] = True
            except:
                print("   ❌ Internet Connection: ไม่สามารถเชื่อมต่อได้")
                self.check_results["internet"] = False
                self.issues.append("ไม่สามารถเชื่อมต่ออินเทอร์เน็ตได้")
            
            # ตรวจสอบ Network Interfaces
            network_info = {}
            for interface, stats in psutil.net_if_stats().items():
                if stats.isup:
                    addrs = psutil.net_if_addrs().get(interface, [])
                    ip_address = ""
                    for addr in addrs:
                        if addr.family == psutil.AF_INET:
                            ip_address = addr.address
                            break
                    
                    if ip_address:
                        network_info[interface] = ip_address
                        print(f"   ✅ {interface}: {ip_address}")
            
            self.check_results["network_interfaces"] = network_info
            
            # ตรวจสอบ DNS
            try:
                import socket
                socket.gethostbyname("google.com")
                print("   ✅ DNS Resolution: ทำงานปกติ")
                self.check_results["dns"] = True
            except:
                print("   ❌ DNS Resolution: มีปัญหา")
                self.check_results["dns"] = False
                self.issues.append("DNS resolution มีปัญหา")
                
        except Exception as e:
            self.issues.append(f"เกิดข้อผิดพลาดในการตรวจสอบเครือข่าย: {e}")
            print(f"   ❌ เกิดข้อผิดพลาด: {e}")
    
    async def _check_services(self):
        """ตรวจสอบบริการ"""
        print("\n🔧 ตรวจสอบบริการ...")
        
        services_to_check = [
            {"name": "WAWAGOT.AI API", "port": 5000},
            {"name": "Dashboard", "port": 8080},
            {"name": "Database", "port": 5432},
            {"name": "Redis", "port": 6379}
        ]
        
        services_status = {}
        
        for service in services_to_check:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', service["port"]))
                sock.close()
                
                if result == 0:
                    print(f"   ✅ {service['name']}: ทำงาน (Port {service['port']})")
                    services_status[service["name"]] = "running"
                else:
                    print(f"   ⚠️ {service['name']}: ไม่ทำงาน (Port {service['port']})")
                    services_status[service["name"]] = "stopped"
                    
            except Exception as e:
                print(f"   ❌ {service['name']}: เกิดข้อผิดพลาด - {e}")
                services_status[service["name"]] = "error"
        
        self.check_results["services"] = services_status
    
    async def _check_storage(self):
        """ตรวจสอบพื้นที่จัดเก็บ"""
        print("\n💾 ตรวจสอบพื้นที่จัดเก็บ...")
        
        try:
            # ตรวจสอบพื้นที่หลัก
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            print(f"   ✅ Total Disk: {round(disk.total / 1024 / 1024 / 1024, 2)} GB")
            print(f"   ✅ Used Disk: {round(disk.used / 1024 / 1024 / 1024, 2)} GB")
            print(f"   ✅ Free Disk: {round(disk.free / 1024 / 1024 / 1024, 2)} GB")
            print(f"   ✅ Usage: {disk_percent:.1f}%")
            
            if disk_percent > 90:
                self.issues.append(f"พื้นที่จัดเก็บเต็มเกือบหมด: {disk_percent:.1f}%")
                print(f"   ⚠️ พื้นที่จัดเก็บเต็มเกือบหมด!")
            elif disk_percent > 80:
                self.recommendations.append("พื้นที่จัดเก็บเริ่มเต็ม ควรทำความสะอาด")
                print(f"   ⚠️ พื้นที่จัดเก็บเริ่มเต็ม")
            
            self.check_results["storage"] = {
                "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "usage_percent": disk_percent
            }
            
            # ตรวจสอบไฟล์สำคัญ
            important_files = [
                "system_environment_manager.py",
                "environment_dashboard.py",
                "requirements.txt",
                "config/system_config.json"
            ]
            
            missing_files = []
            for file_path in important_files:
                if os.path.exists(file_path):
                    print(f"   ✅ {file_path}")
                else:
                    missing_files.append(file_path)
                    print(f"   ❌ {file_path} (ไม่พบ)")
            
            if missing_files:
                self.issues.append(f"ไฟล์สำคัญหายไป: {', '.join(missing_files)}")
                
        except Exception as e:
            self.issues.append(f"เกิดข้อผิดพลาดในการตรวจสอบพื้นที่จัดเก็บ: {e}")
            print(f"   ❌ เกิดข้อผิดพลาด: {e}")
    
    async def _check_performance(self):
        """ตรวจสอบประสิทธิภาพ"""
        print("\n⚡ ตรวจสอบประสิทธิภาพ...")
        
        try:
            # ตรวจสอบ CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"   ✅ CPU Usage: {cpu_percent:.1f}%")
            
            if cpu_percent > 90:
                self.issues.append(f"CPU ใช้งานสูง: {cpu_percent:.1f}%")
            elif cpu_percent > 70:
                self.recommendations.append("CPU ใช้งานค่อนข้างสูง ควรตรวจสอบ")
            
            # ตรวจสอบ Memory
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            print(f"   ✅ Memory Usage: {memory_percent:.1f}%")
            
            if memory_percent > 90:
                self.issues.append(f"Memory ใช้งานสูง: {memory_percent:.1f}%")
            elif memory_percent > 80:
                self.recommendations.append("Memory ใช้งานค่อนข้างสูง ควรตรวจสอบ")
            
            # ตรวจสอบ Process count
            process_count = len(psutil.pids())
            print(f"   ✅ Process Count: {process_count}")
            
            if process_count > 200:
                self.recommendations.append("มี Process จำนวนมาก ควรตรวจสอบ")
            
            self.check_results["performance"] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "process_count": process_count
            }
            
        except Exception as e:
            self.issues.append(f"เกิดข้อผิดพลาดในการตรวจสอบประสิทธิภาพ: {e}")
            print(f"   ❌ เกิดข้อผิดพลาด: {e}")
    
    async def _check_security(self):
        """ตรวจสอบความปลอดภัย"""
        print("\n🔒 ตรวจสอบความปลอดภัย...")
        
        try:
            # ตรวจสอบ Environment Variables ที่สำคัญ
            important_env_vars = [
                "OPENAI_API_KEY",
                "SUPABASE_URL",
                "SUPABASE_KEY",
                "RETELL_API_KEY"
            ]
            
            missing_env_vars = []
            for env_var in important_env_vars:
                if os.getenv(env_var):
                    print(f"   ✅ {env_var}: ตั้งค่าแล้ว")
                else:
                    missing_env_vars.append(env_var)
                    print(f"   ⚠️ {env_var}: ไม่ได้ตั้งค่า")
            
            if missing_env_vars:
                self.recommendations.append(f"ตั้งค่า Environment Variables: {', '.join(missing_env_vars)}")
            
            # ตรวจสอบไฟล์ .env
            if os.path.exists(".env"):
                print("   ✅ .env file: พบ")
            else:
                print("   ⚠️ .env file: ไม่พบ (แนะนำให้สร้าง)")
                self.recommendations.append("สร้างไฟล์ .env สำหรับ Environment Variables")
            
            # ตรวจสอบ Git ignore
            if os.path.exists(".gitignore"):
                with open(".gitignore", "r") as f:
                    gitignore_content = f.read()
                    if ".env" in gitignore_content:
                        print("   ✅ .env ใน .gitignore: ใช่")
                    else:
                        print("   ⚠️ .env ใน .gitignore: ไม่ (ควรเพิ่ม)")
                        self.recommendations.append("เพิ่ม .env ใน .gitignore")
            else:
                print("   ⚠️ .gitignore: ไม่พบ")
                self.recommendations.append("สร้างไฟล์ .gitignore")
            
            self.check_results["security"] = {
                "missing_env_vars": missing_env_vars,
                "has_env_file": os.path.exists(".env"),
                "has_gitignore": os.path.exists(".gitignore")
            }
            
        except Exception as e:
            self.issues.append(f"เกิดข้อผิดพลาดในการตรวจสอบความปลอดภัย: {e}")
            print(f"   ❌ เกิดข้อผิดพลาด: {e}")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """สร้างสรุปผลการตรวจสอบ"""
        print("\n" + "=" * 60)
        print("📊 สรุปผลการตรวจสอบ")
        print("=" * 60)
        
        # นับจำนวนปัญหา
        total_checks = 8  # จำนวนการตรวจสอบทั้งหมด
        issues_count = len(self.issues)
        recommendations_count = len(self.recommendations)
        
        # คำนวณคะแนน
        score = max(0, 100 - (issues_count * 15) - (recommendations_count * 5))
        
        print(f"🎯 คะแนนรวม: {score}/100")
        print(f"❌ ปัญหาที่พบ: {issues_count}")
        print(f"💡 คำแนะนำ: {recommendations_count}")
        
        # แสดงปัญหา
        if self.issues:
            print(f"\n❌ ปัญหาที่พบ:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        # แสดงคำแนะนำ
        if self.recommendations:
            print(f"\n💡 คำแนะนำ:")
            for i, recommendation in enumerate(self.recommendations, 1):
                print(f"   {i}. {recommendation}")
        
        # สรุปสถานะ
        if score >= 90:
            print(f"\n✅ สถานะ: ยอดเยี่ยม! ระบบพร้อมใช้งาน")
        elif score >= 70:
            print(f"\n⚠️ สถานะ: ดี แต่ควรปรับปรุง")
        elif score >= 50:
            print(f"\n⚠️ สถานะ: ปานกลาง ควรแก้ไขปัญหา")
        else:
            print(f"\n❌ สถานะ: แย่ ต้องแก้ไขปัญหาก่อนใช้งาน")
        
        return {
            "timestamp": datetime.now(TZ_BANGKOK).isoformat(),
            "score": score,
            "total_checks": total_checks,
            "issues_count": issues_count,
            "recommendations_count": recommendations_count,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "details": self.check_results,
            "status": "excellent" if score >= 90 else "good" if score >= 70 else "fair" if score >= 50 else "poor"
        }

# ===============================================================================
# QUICK CHECK FUNCTIONS
# ===============================================================================

async def quick_check() -> Dict[str, Any]:
    """ฟังก์ชันตรวจสอบแบบรวดเร็ว"""
    checker = EnvironmentQuickCheck()
    return await checker.run_full_check()

async def check_specific_area(area: str) -> Dict[str, Any]:
    """ตรวจสอบเฉพาะส่วน"""
    checker = EnvironmentQuickCheck()
    
    if area == "system":
        await checker._check_system_basics()
    elif area == "python":
        await checker._check_python_environment()
    elif area == "dependencies":
        await checker._check_dependencies()
    elif area == "network":
        await checker._check_network()
    elif area == "services":
        await checker._check_services()
    elif area == "storage":
        await checker._check_storage()
    elif area == "performance":
        await checker._check_performance()
    elif area == "security":
        await checker._check_security()
    else:
        return {"error": f"ไม่พบการตรวจสอบสำหรับ: {area}"}
    
    return checker.check_results

def save_check_results(results: Dict[str, Any], filename: str = None):
    """บันทึกผลการตรวจสอบ"""
    if not filename:
        timestamp = datetime.now(TZ_BANGKOK).strftime("%Y%m%d_%H%M%S")
        filename = f"environment_check_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 บันทึกผลการตรวจสอบไปยัง: {filename}")

# ===============================================================================
# MAIN EXECUTION
# ===============================================================================

async def main():
    """ฟังก์ชันหลัก"""
    print("🚀 WAWAGOT.AI Environment Quick Check")
    print("=" * 60)
    
    # ตรวจสอบทั้งหมด
    results = await quick_check()
    
    # บันทึกผล
    save_check_results(results)
    
    # แสดงผลลัพธ์ JSON
    print(f"\n📋 ผลลัพธ์ JSON:")
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main()) 