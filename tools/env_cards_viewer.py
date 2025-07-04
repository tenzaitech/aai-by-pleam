#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment Cards Viewer
แสดงข้อมูล Environment ของโปรแกรมต่างๆ แบบ standalone
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.environment_cards import env_cards
import json

def display_environment_cards():
    """แสดง Environment Cards ทั้งหมด"""
    print("🔍 Environment Cards Viewer")
    print("=" * 50)
    
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
        print(f"  ❌ Error: {cards['python']['error']}")
    
    # แสดง Chrome Environment
    print("\n🌐 Chrome Environment:")
    if cards['chrome']['installed']:
        print(f"  ✅ Installed: {cards['chrome']['version']}")
        print(f"  Path: {cards['chrome']['path']}")
    else:
        print("  ❌ Chrome not found")
    
    # แสดง Database Environment
    print("\n🗄️  Database Environment:")
    for db_name, db_info in cards['databases'].items():
        status = "✅" if db_info.get('available', False) else "❌"
        version = f" ({db_info.get('version', 'unknown')})" if db_info.get('version') else ""
        print(f"  {status} {db_name.title()}{version}")
    
    # แสดง AI Libraries
    print("\n🧠 AI Libraries:")
    for lib_name, lib_info in cards['ai_libraries'].items():
        status = "✅" if lib_info.get('available', False) else "❌"
        version = f" ({lib_info.get('version', 'unknown')})" if lib_info.get('version') else ""
        gpu_info = " [GPU]" if lib_info.get('gpu_available', False) else ""
        print(f"  {status} {lib_name.title()}{version}{gpu_info}")
    
    # แสดง Network Environment
    print("\n🌍 Network Environment:")
    if cards['network']['internet_available']:
        print(f"  ✅ Internet: Available")
        print(f"  External IP: {cards['network']['external_ip']}")
    else:
        print("  ❌ Internet: Not available")
    
    # แสดง Backup Environment
    print("\n💾 Backup Environment:")
    for dir_name, dir_info in cards['backup'].items():
        if dir_info.get('exists', False):
            size_mb = dir_info.get('size_bytes', 0) / (1024**2)
            print(f"  ✅ {dir_name}: {dir_info.get('file_count', 0)} files, {size_mb:.1f} MB")
        else:
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
    
    if summary['recommendations']:
        print("\n💡 Recommendations:")
        for rec in summary['recommendations']:
            print(f"  - {rec}")
    
    print(f"\n🕒 Last Update: {cards['last_update']}")

def save_environment_report():
    """บันทึก Environment Report เป็นไฟล์ JSON"""
    cards = env_cards.generate_all_cards()
    summary = env_cards.get_card_summary()
    
    report = {
        "timestamp": cards['last_update'],
        "summary": summary,
        "details": cards
    }
    
    filename = f"environment_report_{cards['last_update'][:10]}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Environment report saved: {filename}")

if __name__ == "__main__":
    try:
        display_environment_cards()
        save_environment_report()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 