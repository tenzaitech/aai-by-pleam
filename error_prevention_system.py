#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error Prevention System for WAWAGOT.AI
ระบบป้องกันและแก้ไข error ที่อาจเกิดขึ้นในอนาคต
"""

import os
import sys
import logging
import json
import traceback
import subprocess
import importlib
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/error_prevention.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ErrorPreventionSystem:
    """ระบบป้องกันและแก้ไข error"""
    
    def __init__(self):
        self.errors_found = []
        self.errors_fixed = []
        self.warnings = []
        self.recommendations = []
        
    def check_directory_structure(self):
        """ตรวจสอบโครงสร้างไดเรกทอรี"""
        logger.info("Checking directory structure...")
        
        required_dirs = [
            'logs',
            'backups',
            'reports',
            'data',
            'config',
            'core',
            'tools',
            'tests',
            'conversation_logs'
        ]
        
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                try:
                    os.makedirs(dir_name, exist_ok=True)
                    self.errors_fixed.append(f"Created missing directory: {dir_name}")
                    logger.info(f"Created missing directory: {dir_name}")
                except Exception as e:
                    self.errors_found.append(f"Cannot create directory {dir_name}: {e}")
                    logger.error(f"Cannot create directory {dir_name}: {e}")
    
    def check_python_imports(self):
        """ตรวจสอบ Python imports ที่อาจมีปัญหา"""
        logger.info("Checking Python imports...")
        
        critical_modules = [
            'core.chrome_controller',
            'core.ai_integration',
            'core.thai_processor',
            'core.visual_recognition',
            'core.backup_controller',
            'core.supabase_integration',
            'core.environment_cards',
            'core.knowledge_manager',
            'conversation_logs.auto_logger.auto_logger',
            'conversation_logs.security_manager',
            'conversation_logs.monitoring_alert_system'
        ]
        
        for module_name in critical_modules:
            try:
                importlib.import_module(module_name)
                logger.debug(f"Module {module_name} imported successfully")
            except ImportError as e:
                self.errors_found.append(f"Import error in {module_name}: {e}")
                logger.warning(f"Import error in {module_name}: {e}")
            except Exception as e:
                self.errors_found.append(f"Unexpected error importing {module_name}: {e}")
                logger.error(f"Unexpected error importing {module_name}: {e}")
    
    def check_config_files(self):
        """ตรวจสอบไฟล์ config ที่จำเป็น"""
        logger.info("Checking configuration files...")
        
        config_files = [
            'config/system_config.json',
            'config/ai.json',
            'config/supabase_config.json',
            'config/backup_config.json',
            'config/chrome.json'
        ]
        
        for config_file in config_files:
            if not os.path.exists(config_file):
                self.warnings.append(f"Missing config file: {config_file}")
                logger.warning(f"Missing config file: {config_file}")
            else:
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                    logger.debug(f"Config file {config_file} is valid JSON")
                except json.JSONDecodeError as e:
                    self.errors_found.append(f"Invalid JSON in {config_file}: {e}")
                    logger.error(f"Invalid JSON in {config_file}: {e}")
                except Exception as e:
                    self.errors_found.append(f"Error reading {config_file}: {e}")
                    logger.error(f"Error reading {config_file}: {e}")
    
    def check_logging_setup(self):
        """ตรวจสอบการตั้งค่า logging"""
        logger.info("Checking logging setup...")
        
        # ตรวจสอบว่า logs directory มีอยู่
        if not os.path.exists('logs'):
            try:
                os.makedirs('logs', exist_ok=True)
                self.errors_fixed.append("Created logs directory")
                logger.info("Created logs directory")
            except Exception as e:
                self.errors_found.append(f"Cannot create logs directory: {e}")
                logger.error(f"Cannot create logs directory: {e}")
        
        # ตรวจสอบ log files ที่อาจมีขนาดใหญ่เกินไป
        log_files = ['logs/mcp_server.log', 'logs/system_components_test.log', 
                    'logs/env_cards_viewer.log', 'logs/chrome_cleanup.log']
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    file_size = os.path.getsize(log_file)
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        self.warnings.append(f"Large log file detected: {log_file} ({file_size // 1024 // 1024}MB)")
                        logger.warning(f"Large log file detected: {log_file} ({file_size // 1024 // 1024}MB)")
                except Exception as e:
                    logger.error(f"Error checking log file {log_file}: {e}")
    
    def check_environment_variables(self):
        """ตรวจสอบ environment variables ที่จำเป็น"""
        logger.info("Checking environment variables...")
        
        critical_env_vars = [
            'SUPABASE_URL',
            'SUPABASE_KEY',
            'GOOGLE_API_KEY',
            'GEMINI_API_KEY'
        ]
        
        missing_vars = []
        for var in critical_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.warnings.append(f"Missing environment variables: {', '.join(missing_vars)}")
            logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
    
    def check_file_permissions(self):
        """ตรวจสอบสิทธิ์การเข้าถึงไฟล์"""
        logger.info("Checking file permissions...")
        
        critical_files = [
            'wawagot_mcp_server.py',
            'system_status_check.py',
            'test_system_components.py'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                try:
                    # ตรวจสอบว่าสามารถอ่านได้
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read(1)
                    logger.debug(f"File {file_path} is readable")
                except PermissionError:
                    self.errors_found.append(f"Permission denied reading {file_path}")
                    logger.error(f"Permission denied reading {file_path}")
                except Exception as e:
                    self.errors_found.append(f"Error reading {file_path}: {e}")
                    logger.error(f"Error reading {file_path}: {e}")
    
    def check_dependencies(self):
        """ตรวจสอบ dependencies ที่จำเป็น"""
        logger.info("Checking dependencies...")
        
        required_packages = [
            'requests',
            'psutil',
            'selenium',
            'playwright',
            'supabase',
            'google-auth',
            'google-api-python-client',
            'transformers',
            'torch',
            'tensorflow'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                # Handle special cases for Google packages
                if package == 'google-auth':
                    importlib.import_module('google.auth')
                elif package == 'google-api-python-client':
                    importlib.import_module('googleapiclient')
                else:
                    importlib.import_module(package.replace('-', '_'))
                logger.debug(f"Package {package} is available")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"Missing package: {package}")
        
        if missing_packages:
            self.warnings.append(f"Missing packages: {', '.join(missing_packages)}")
            logger.warning(f"Missing packages: {', '.join(missing_packages)}")
    
    def check_system_resources(self):
        """ตรวจสอบทรัพยากรระบบ"""
        logger.info("Checking system resources...")
        
        try:
            import psutil
            
            # ตรวจสอบ memory
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.warnings.append(f"High memory usage: {memory.percent}%")
                logger.warning(f"High memory usage: {memory.percent}%")
            
            # ตรวจสอบ disk space
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                self.warnings.append(f"Low disk space: {disk.percent}% used")
                logger.warning(f"Low disk space: {disk.percent}% used")
            
            # ตรวจสอบ CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                self.warnings.append(f"High CPU usage: {cpu_percent}%")
                logger.warning(f"High CPU usage: {cpu_percent}%")
                
        except ImportError:
            self.warnings.append("psutil not available for system resource monitoring")
            logger.warning("psutil not available for system resource monitoring")
        except Exception as e:
            self.errors_found.append(f"Error checking system resources: {e}")
            logger.error(f"Error checking system resources: {e}")
    
    def generate_recommendations(self):
        """สร้างคำแนะนำสำหรับการปรับปรุง"""
        logger.info("Generating recommendations...")
        
        if self.errors_found:
            self.recommendations.append("Review and fix all found errors before production deployment")
        
        if self.warnings:
            self.recommendations.append("Address warnings to improve system stability")
        
        if not os.path.exists('logs'):
            self.recommendations.append("Create logs directory for proper error tracking")
        
        if not os.path.exists('backups'):
            self.recommendations.append("Create backups directory for data protection")
        
        self.recommendations.extend([
            "Implement automated testing for all critical components",
            "Set up monitoring and alerting for system health",
            "Regularly review and rotate log files",
            "Backup configuration files regularly",
            "Monitor system resource usage",
            "Keep dependencies updated"
        ])
    
    def run_full_check(self):
        """รันการตรวจสอบทั้งหมด"""
        logger.info("Starting comprehensive error prevention check...")
        
        print("🔍 Error Prevention System - Comprehensive Check")
        print("=" * 60)
        
        # ตรวจสอบทั้งหมด
        self.check_directory_structure()
        self.check_python_imports()
        self.check_config_files()
        self.check_logging_setup()
        self.check_environment_variables()
        self.check_file_permissions()
        self.check_dependencies()
        self.check_system_resources()
        self.generate_recommendations()
        
        # แสดงผลลัพธ์
        self.print_report()
        
        return len(self.errors_found) == 0
    
    def print_report(self):
        """พิมพ์รายงานผลการตรวจสอบ"""
        print("\n📊 Error Prevention Report")
        print("=" * 60)
        
        # Errors Found
        if self.errors_found:
            print(f"\n❌ Errors Found ({len(self.errors_found)}):")
            for error in self.errors_found:
                print(f"   - {error}")
        else:
            print("\n✅ No critical errors found")
        
        # Errors Fixed
        if self.errors_fixed:
            print(f"\n🔧 Errors Fixed ({len(self.errors_fixed)}):")
            for fix in self.errors_fixed:
                print(f"   - {fix}")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️ Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        # Recommendations
        if self.recommendations:
            print(f"\n💡 Recommendations ({len(self.recommendations)}):")
            for rec in self.recommendations:
                print(f"   - {rec}")
        
        # Summary
        print(f"\n📈 Summary:")
        print(f"   - Errors Found: {len(self.errors_found)}")
        print(f"   - Errors Fixed: {len(self.errors_fixed)}")
        print(f"   - Warnings: {len(self.warnings)}")
        print(f"   - Recommendations: {len(self.recommendations)}")
        
        if len(self.errors_found) == 0:
            print("\n🎉 System is ready for production!")
        else:
            print(f"\n⚠️ Please address {len(self.errors_found)} errors before production deployment")
    
    def save_report(self):
        """บันทึกรายงานเป็นไฟล์ JSON"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "errors_found": self.errors_found,
            "errors_fixed": self.errors_fixed,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "summary": {
                "total_errors": len(self.errors_found),
                "total_fixed": len(self.errors_fixed),
                "total_warnings": len(self.warnings),
                "total_recommendations": len(self.recommendations)
            }
        }
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        filename = f"reports/error_prevention_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Error prevention report saved: {filename}")
            print(f"\n💾 Report saved: {filename}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            print(f"\n❌ Error saving report: {e}")

def main():
    """ฟังก์ชันหลัก"""
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Error Prevention System starting...")
    
    try:
        eps = ErrorPreventionSystem()
        success = eps.run_full_check()
        eps.save_report()
        
        logger.info("Error Prevention System completed successfully")
        return 0 if success else 1
        
    except Exception as e:
        error_msg = f"Critical error in Error Prevention System: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ Critical Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 