#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment Cards Viewer
แสดงข้อมูล Environment ของโปรแกรมต่างๆ แบบ standalone
"""

import sys
import os
import logging
import json
import traceback
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/env_cards_viewer.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

try:
from core.environment_cards import env_cards
except ImportError as e:
    logger.error(f"Failed to import environment_cards: {e}")
    sys.exit(1)

def display_environment_cards():
    """แสดง Environment Cards ทั้งหมด"""
    logger.info("Starting environment cards display")
    print("🔍 Environment Cards Viewer")
    print("=" * 50)
    
    try:
    # สร้าง cards
    cards = env_cards.generate_all_cards()
    summary = env_cards.get_card_summary()
    
    # แสดง System Info
    print("\n🖥️  System Information:")
    print(f"  OS: {cards['system']['os']} {cards['system']['os_version']}")
    print(f"  Python: {cards['system']['python_version'].split()[0]}")
    print(f"  Architecture: {cards['system']['architecture']}")
    print(f"  CPU Cores: {cards['system']['cpu_count']}")
    print(f"  Memory: {cards['system']['memory_total'] // (1024**3):.1f} GB")
    print(f"  Disk: {cards['system']['disk_total'] // (1024**3):.1f} GB")
    
    # แสดง Python Environment
    print("\n🐍 Python Environment:")
    if 'error' not in cards['python']:
        print(f"  Python Path: {cards['python']['python_path']}")
        print(f"  Pip Version: {cards['python']['pip_version']}")
        print(f"  Virtual Env: {cards['python']['virtual_env']}")
        print(f"  Installed Packages: {cards['python']['installed_packages']}")
        print("  Key Packages:")
        for pkg in cards['python']['key_packages'][:5]:  # แสดง 5 แรก
            print(f"    - {pkg}")
    else:
            error_msg = f"Python environment error: {cards['python']['error']}"
            logger.error(error_msg)
        print(f"  ❌ Error: {cards['python']['error']}")
    
    # แสดง Chrome Environment
    print("\n🌐 Chrome Environment:")
    if cards['chrome']['installed']:
        print(f"  ✅ Installed: {cards['chrome']['version']}")
        print(f"  Path: {cards['chrome']['path']}")
    else:
            logger.warning("Chrome not found in system")
        print("  ❌ Chrome not found")
    
    # แสดง Database Environment
    print("\n🗄️  Database Environment:")
    for db_name, db_info in cards['databases'].items():
        status = "✅" if db_info.get('available', False) else "❌"
        version = f" ({db_info.get('version', 'unknown')})" if db_info.get('version') else ""
        print(f"  {status} {db_name.title()}{version}")
            if not db_info.get('available', False):
                logger.warning(f"Database {db_name} not available")
    
    # แสดง AI Libraries
    print("\n🧠 AI Libraries:")
    for lib_name, lib_info in cards['ai_libraries'].items():
        status = "✅" if lib_info.get('available', False) else "❌"
        version = f" ({lib_info.get('version', 'unknown')})" if lib_info.get('version') else ""
        gpu_info = " [GPU]" if lib_info.get('gpu_available', False) else ""
        print(f"  {status} {lib_name.title()}{version}{gpu_info}")
            if not lib_info.get('available', False):
                logger.warning(f"AI library {lib_name} not available")
    
    # แสดง Network Environment
    print("\n🌍 Network Environment:")
    if cards['network']['internet_available']:
        print(f"  ✅ Internet: Available")
        print(f"  External IP: {cards['network']['external_ip']}")
    else:
            logger.warning("Internet connection not available")
        print("  ❌ Internet: Not available")
    
    # แสดง Backup Environment
    print("\n💾 Backup Environment:")
    for dir_name, dir_info in cards['backup'].items():
        if dir_info.get('exists', False):
            size_mb = dir_info.get('size_bytes', 0) / (1024**2)
            print(f"  ✅ {dir_name}: {dir_info.get('file_count', 0)} files, {size_mb:.1f} MB")
        else:
                logger.warning(f"Backup directory {dir_name} not found")
            print(f"  ❌ {dir_name}: Not found")
    
    # แสดง Summary
    print("\n📊 Environment Summary:")
    print(f"  Total Components: {summary['total_components']}")
    print(f"  Ready Components: {summary['ready_components']}")
    print(f"  Readiness: {summary['readiness_percent']:.1f}%")
    
    if summary['issues']:
        print("\n⚠️  Issues Found:")
        for issue in summary['issues']:
            print(f"  - {issue}")
                logger.warning(f"Environment issue: {issue}")
    
    if summary['recommendations']:
        print("\n💡 Recommendations:")
        for rec in summary['recommendations']:
            print(f"  - {rec}")
                logger.info(f"Environment recommendation: {rec}")
    
    print(f"\n🕒 Last Update: {cards['last_update']}")
        logger.info("Environment cards display completed successfully")
        
    except Exception as e:
        error_msg = f"Error displaying environment cards: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ Error: {e}")

def save_environment_report():
    """บันทึก Environment Report เป็นไฟล์ JSON"""
    logger.info("Starting environment report save")
    
    try:
    cards = env_cards.generate_all_cards()
    summary = env_cards.get_card_summary()
    
    report = {
        "timestamp": cards['last_update'],
        "summary": summary,
        "details": cards
    }
    
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        filename = f"reports/environment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Environment report saved: {filename}")
        logger.info(f"Environment report saved successfully: {filename}")
        
    except Exception as e:
        error_msg = f"Error saving environment report: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ Error saving report: {e}")

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Environment Cards Viewer starting...")
    
    try:
        display_environment_cards()
        save_environment_report()
        logger.info("Environment Cards Viewer completed successfully")
    except Exception as e:
        error_msg = f"Critical error in Environment Cards Viewer: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ Critical Error: {e}")
        sys.exit(1) 