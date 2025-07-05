# WAWAGOT.AI - Environment Launcher
# ===============================================================================
# WAWAGOT.AI - Launcher สำหรับระบบจัดการสภาพแวดล้อม
# ===============================================================================
# Created: 2024-12-19
# Purpose: Launcher หลักสำหรับระบบจัดการสภาพแวดล้อมทั้งหมด
# ===============================================================================

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import argparse

# Import modules
try:
    from system_environment_manager import SystemEnvironmentManager
    from environment_dashboard import EnvironmentDashboard
    from environment_quick_check import EnvironmentQuickCheck, quick_check, check_specific_area
except ImportError as e:
    print(f"❌ ไม่สามารถ import modules ได้: {e}")
    print("🔧 ตรวจสอบว่าไฟล์ทั้งหมดอยู่ในโฟลเดอร์เดียวกัน")
    sys.exit(1)

# ===============================================================================
# LAUNCHER CLASS
# ===============================================================================

class EnvironmentLauncher:
    """Launcher หลักสำหรับระบบจัดการสภาพแวดล้อม"""
    
    def __init__(self):
        self.env_manager = None
        self.dashboard = None
        self.quick_checker = None
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """โหลดการตั้งค่า"""
        default_config = {
            "dashboard_port": 8080,
            "dashboard_host": "0.0.0.0",
            "update_interval": 30,
            "log_level": "INFO",
            "auto_start_dashboard": False,
            "auto_start_monitoring": True
        }
        
        # โหลดจากไฟล์ config ถ้ามี
        config_file = "config/environment_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    default_config.update(file_config)
            except Exception as e:
                print(f"⚠️ ไม่สามารถโหลด config ได้: {e}")
        
        return default_config
    
    def _save_config(self):
        """บันทึกการตั้งค่า"""
        config_file = "config/environment_config.json"
        os.makedirs("config", exist_ok=True)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ ไม่สามารถบันทึก config ได้: {e}")
    
    async def initialize_system(self) -> Dict[str, Any]:
        """เริ่มต้นระบบทั้งหมด"""
        print("🚀 เริ่มต้นระบบจัดการสภาพแวดล้อม WAWAGOT.AI...")
        print("=" * 60)
        
        try:
            # สร้าง Environment Manager
            self.env_manager = SystemEnvironmentManager()
            
            # เริ่มต้นระบบ
            init_result = await self.env_manager.initialize_system()
            
            if init_result["success"]:
                print("✅ ระบบเริ่มต้นสำเร็จ!")
                
                # สร้าง Dashboard
                self.dashboard = EnvironmentDashboard()
                
                # สร้าง Quick Checker
                self.quick_checker = EnvironmentQuickCheck()
                
                return {
                    "success": True,
                    "message": "ระบบเริ่มต้นสำเร็จ",
                    "components": {
                        "environment_manager": "พร้อมใช้งาน",
                        "dashboard": "พร้อมใช้งาน",
                        "quick_checker": "พร้อมใช้งาน"
                    }
                }
            else:
                return init_result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการเริ่มต้นระบบ: {e}"
            }
    
    async def start_dashboard(self, host: str = None, port: int = None) -> Dict[str, Any]:
        """เริ่มต้น Dashboard"""
        try:
            if not self.dashboard:
                await self.initialize_system()
            
            host = host or self.config["dashboard_host"]
            port = port or self.config["dashboard_port"]
            
            print(f"🌐 เริ่มต้น Dashboard ที่ http://{host}:{port}")
            
            # เริ่มต้น Dashboard ใน background
            dashboard_task = asyncio.create_task(
                self.dashboard.start_dashboard(host, port)
            )
            
            return {
                "success": True,
                "message": f"Dashboard เริ่มต้นที่ http://{host}:{port}",
                "task": dashboard_task
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการเริ่มต้น Dashboard: {e}"
            }
    
    async def run_quick_check(self, area: str = None) -> Dict[str, Any]:
        """รัน Quick Check"""
        try:
            if area:
                print(f"🔍 ตรวจสอบเฉพาะส่วน: {area}")
                result = await check_specific_area(area)
            else:
                print("🔍 ตรวจสอบสภาพแวดล้อมทั้งหมด...")
                result = await quick_check()
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการตรวจสอบ: {e}"
            }
    
    async def optimize_environment(self) -> Dict[str, Any]:
        """ปรับปรุงสภาพแวดล้อม"""
        try:
            if not self.env_manager:
                await self.initialize_system()
            
            print("🔧 กำลังปรับปรุงสภาพแวดล้อม...")
            result = await self.env_manager.optimize_environment()
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการปรับปรุง: {e}"
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """ดึงสถานะระบบ"""
        try:
            if not self.env_manager:
                await self.initialize_system()
            
            status = await self.env_manager.get_system_status()
            return {
                "success": True,
                "status": status
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการดึงสถานะ: {e}"
            }
    
    def show_menu(self):
        """แสดงเมนูหลัก"""
        print("\n" + "=" * 60)
        print("🤖 WAWAGOT.AI Environment Management System")
        print("=" * 60)
        print("1. 🔍 ตรวจสอบสภาพแวดล้อมทั้งหมด")
        print("2. 🔧 ตรวจสอบเฉพาะส่วน")
        print("3. 🌐 เริ่มต้น Dashboard")
        print("4. ⚡ ปรับปรุงสภาพแวดล้อม")
        print("5. 📊 ดูสถานะระบบ")
        print("6. ⚙️ การตั้งค่า")
        print("7. 📋 ข้อมูลระบบ")
        print("0. 🚪 ออกจากระบบ")
        print("=" * 60)
    
    async def interactive_mode(self):
        """โหมด Interactive"""
        await self.initialize_system()
        
        while True:
            self.show_menu()
            
            try:
                choice = input("\nเลือกตัวเลือก (0-7): ").strip()
                
                if choice == "0":
                    print("👋 ขอบคุณที่ใช้งาน WAWAGOT.AI Environment System!")
                    break
                
                elif choice == "1":
                    print("\n🔍 ตรวจสอบสภาพแวดล้อมทั้งหมด...")
                    result = await self.run_quick_check()
                    if result["success"]:
                        print("✅ ตรวจสอบเสร็จสิ้น")
                    else:
                        print(f"❌ เกิดข้อผิดพลาด: {result['error']}")
                
                elif choice == "2":
                    print("\n🔧 ตรวจสอบเฉพาะส่วน:")
                    print("1. ระบบพื้นฐาน")
                    print("2. Python Environment")
                    print("3. Dependencies")
                    print("4. เครือข่าย")
                    print("5. บริการ")
                    print("6. พื้นที่จัดเก็บ")
                    print("7. ประสิทธิภาพ")
                    print("8. ความปลอดภัย")
                    
                    area_choice = input("เลือกส่วนที่ต้องการตรวจสอบ (1-8): ").strip()
                    
                    area_map = {
                        "1": "system",
                        "2": "python",
                        "3": "dependencies",
                        "4": "network",
                        "5": "services",
                        "6": "storage",
                        "7": "performance",
                        "8": "security"
                    }
                    
                    if area_choice in area_map:
                        result = await self.run_quick_check(area_map[area_choice])
                        if result["success"]:
                            print("✅ ตรวจสอบเสร็จสิ้น")
                        else:
                            print(f"❌ เกิดข้อผิดพลาด: {result['error']}")
                    else:
                        print("❌ ตัวเลือกไม่ถูกต้อง")
                
                elif choice == "3":
                    print("\n🌐 เริ่มต้น Dashboard...")
                    result = await self.start_dashboard()
                    if result["success"]:
                        print(f"✅ {result['message']}")
                        print("กด Ctrl+C เพื่อหยุด Dashboard")
                        try:
                            await result["task"]
                        except KeyboardInterrupt:
                            print("\n🛑 หยุด Dashboard")
                    else:
                        print(f"❌ เกิดข้อผิดพลาด: {result['error']}")
                
                elif choice == "4":
                    print("\n⚡ ปรับปรุงสภาพแวดล้อม...")
                    result = await self.optimize_environment()
                    if result["success"]:
                        print("✅ ปรับปรุงเสร็จสิ้น")
                        print(json.dumps(result["result"], ensure_ascii=False, indent=2))
                    else:
                        print(f"❌ เกิดข้อผิดพลาด: {result['error']}")
                
                elif choice == "5":
                    print("\n📊 สถานะระบบ...")
                    result = await self.get_system_status()
                    if result["success"]:
                        status = result["status"]
                        print(f"✅ CPU: {status['performance']['cpu_percent']:.1f}%")
                        print(f"✅ Memory: {status['performance']['memory_percent']:.1f}%")
                        print(f"✅ Process Count: {status['performance']['process_count']}")
                    else:
                        print(f"❌ เกิดข้อผิดพลาด: {result['error']}")
                
                elif choice == "6":
                    self._show_settings()
                
                elif choice == "7":
                    self._show_system_info()
                
                else:
                    print("❌ ตัวเลือกไม่ถูกต้อง")
                
                input("\nกด Enter เพื่อกลับไปเมนูหลัก...")
                
            except KeyboardInterrupt:
                print("\n👋 ขอบคุณที่ใช้งาน!")
                break
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาด: {e}")
    
    def _show_settings(self):
        """แสดงการตั้งค่า"""
        print("\n⚙️ การตั้งค่าปัจจุบัน:")
        print(json.dumps(self.config, ensure_ascii=False, indent=2))
        
        change = input("\nต้องการเปลี่ยนการตั้งค่า? (y/n): ").strip().lower()
        if change == 'y':
            print("\nการตั้งค่าที่สามารถเปลี่ยนได้:")
            print("1. Dashboard Port")
            print("2. Dashboard Host")
            print("3. Update Interval")
            print("4. Auto Start Dashboard")
            
            setting_choice = input("เลือกการตั้งค่า (1-4): ").strip()
            
            if setting_choice == "1":
                new_port = input("Dashboard Port (ปัจจุบัน: {}): ".format(self.config["dashboard_port"]))
                if new_port.isdigit():
                    self.config["dashboard_port"] = int(new_port)
            
            elif setting_choice == "2":
                new_host = input("Dashboard Host (ปัจจุบัน: {}): ".format(self.config["dashboard_host"]))
                if new_host:
                    self.config["dashboard_host"] = new_host
            
            elif setting_choice == "3":
                new_interval = input("Update Interval (ปัจจุบัน: {}): ".format(self.config["update_interval"]))
                if new_interval.isdigit():
                    self.config["update_interval"] = int(new_interval)
            
            elif setting_choice == "4":
                auto_start = input("Auto Start Dashboard (y/n): ").strip().lower()
                self.config["auto_start_dashboard"] = auto_start == 'y'
            
            self._save_config()
            print("✅ บันทึกการตั้งค่าแล้ว")
    
    def _show_system_info(self):
        """แสดงข้อมูลระบบ"""
        print("\n📋 ข้อมูลระบบ:")
        print(f"Python Version: {sys.version}")
        print(f"Platform: {sys.platform}")
        print(f"Current Directory: {os.getcwd()}")
        print(f"Config File: config/environment_config.json")
        print(f"Dashboard URL: http://{self.config['dashboard_host']}:{self.config['dashboard_port']}")

# ===============================================================================
# COMMAND LINE INTERFACE
# ===============================================================================

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="WAWAGOT.AI Environment Launcher")
    
    parser.add_argument("--mode", choices=["interactive", "dashboard", "check", "optimize", "status"], 
                       default="interactive", help="โหมดการทำงาน")
    
    parser.add_argument("--area", choices=["system", "python", "dependencies", "network", "services", "storage", "performance", "security"],
                       help="ส่วนที่ต้องการตรวจสอบ (ใช้กับ --mode check)")
    
    parser.add_argument("--host", default="0.0.0.0", help="Dashboard host")
    parser.add_argument("--port", type=int, default=8080, help="Dashboard port")
    
    parser.add_argument("--config", help="ไฟล์ config")
    parser.add_argument("--output", help="ไฟล์ output สำหรับผลลัพธ์")
    
    return parser.parse_args()

# ===============================================================================
# MAIN EXECUTION
# ===============================================================================

async def main():
    """ฟังก์ชันหลัก"""
    args = parse_arguments()
    
    # สร้าง Launcher
    launcher = EnvironmentLauncher()
    
    try:
        if args.mode == "interactive":
            # โหมด Interactive
            await launcher.interactive_mode()
        
        elif args.mode == "dashboard":
            # โหมด Dashboard
            await launcher.initialize_system()
            result = await launcher.start_dashboard(args.host, args.port)
            if result["success"]:
                print(f"✅ {result['message']}")
                await result["task"]
            else:
                print(f"❌ {result['error']}")
        
        elif args.mode == "check":
            # โหมดตรวจสอบ
            if args.area:
                result = await launcher.run_quick_check(args.area)
            else:
                result = await launcher.run_quick_check()
            
            if result["success"]:
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(result["result"], f, ensure_ascii=False, indent=2)
                    print(f"✅ บันทึกผลลัพธ์ไปยัง: {args.output}")
                else:
                    print(json.dumps(result["result"], ensure_ascii=False, indent=2))
            else:
                print(f"❌ {result['error']}")
        
        elif args.mode == "optimize":
            # โหมดปรับปรุง
            await launcher.initialize_system()
            result = await launcher.optimize_environment()
            if result["success"]:
                print("✅ ปรับปรุงเสร็จสิ้น")
                print(json.dumps(result["result"], ensure_ascii=False, indent=2))
            else:
                print(f"❌ {result['error']}")
        
        elif args.mode == "status":
            # โหมดสถานะ
            await launcher.initialize_system()
            result = await launcher.get_system_status()
            if result["success"]:
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(result["status"], f, ensure_ascii=False, indent=2)
                    print(f"✅ บันทึกสถานะไปยัง: {args.output}")
                else:
                    print(json.dumps(result["status"], ensure_ascii=False, indent=2))
            else:
                print(f"❌ {result['error']}")
    
    except KeyboardInterrupt:
        print("\n👋 หยุดการทำงาน...")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 