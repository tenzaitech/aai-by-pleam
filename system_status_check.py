#!/usr/bin/env python3
"""
System Status Check - WAWA
ตรวจสอบสถานะการทำงานจริงทั้งหมดของโปรแกรม
"""

import psutil
import os
import time
import subprocess
import threading
from datetime import datetime

def check_system_status():
    """ตรวจสอบสถานะระบบ"""
    print("🔍 Cursor System Status Report - WAWA")
    print("=" * 60)
    
    # 1. CPU & Memory
    print("💻 System Resources:")
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    print(f"   CPU Usage: {cpu_percent}%")
    print(f"   Memory Usage: {memory.percent}%")
    print(f"   Available Memory: {memory.available / 1024**3:.2f} GB")
    print(f"   Total Memory: {memory.total / 1024**3:.2f} GB")
    
    # 2. Python Processes
    print("\n🐍 Python Processes:")
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            if 'python' in proc.info['name'].lower():
                python_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if python_processes:
        for proc in python_processes:
            memory_mb = proc['memory_info'].rss / 1024**2
            print(f"   PID {proc['pid']}: {proc['name']} - {memory_mb:.1f} MB - CPU: {proc['cpu_percent']}%")
    else:
        print("   No Python processes running")
    
    # 3. Chrome Processes
    print("\n🌐 Chrome Processes:")
    chrome_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            if 'chrome' in proc.info['name'].lower():
                chrome_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if chrome_processes:
        total_chrome_memory = 0
        for proc in chrome_processes:
            memory_mb = proc['memory_info'].rss / 1024**2
            total_chrome_memory += memory_mb
            print(f"   PID {proc['pid']}: {proc['name']} - {memory_mb:.1f} MB - CPU: {proc['cpu_percent']}%")
        print(f"   Total Chrome Memory: {total_chrome_memory:.1f} MB")
    else:
        print("   No Chrome processes running")
    
    # 4. Network Ports
    print("\n🌍 Network Ports:")
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        # Check port 5000 (dashboard)
        port_5000_found = False
        for line in lines:
            if ':5000' in line and 'LISTENING' in line:
                print(f"   Port 5000: LISTENING (Dashboard)")
                port_5000_found = True
                break
        
        if not port_5000_found:
            print("   Port 5000: NOT LISTENING (Dashboard not running)")
            
    except Exception as e:
        print(f"   Error checking ports: {e}")
    
    # 5. GPU Status
    print("\n🎮 GPU Status:")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            gpu_memory_used = torch.cuda.memory_allocated(0) / 1024**2
            print(f"   GPU: {gpu_name}")
            print(f"   Total Memory: {gpu_memory:.2f} GB")
            print(f"   Used Memory: {gpu_memory_used:.2f} MB")
            print(f"   CUDA Available: ✅")
        else:
            print("   CUDA Available: ❌")
    except ImportError:
        print("   PyTorch not installed")
    except Exception as e:
        print(f"   GPU Error: {e}")
    
    # 6. Disk Usage
    print("\n💾 Disk Usage:")
    disk = psutil.disk_usage('.')
    print(f"   Total: {disk.total / 1024**3:.2f} GB")
    print(f"   Used: {disk.used / 1024**3:.2f} GB")
    print(f"   Free: {disk.free / 1024**3:.2f} GB")
    print(f"   Usage: {disk.percent}%")
    
    # 7. Project Files Status
    print("\n📁 Project Files Status:")
    important_files = [
        'dashboard/app.py',
        'core/chrome_controller.py',
        'smart_resource_allocator.py',
        'gpu_cursor_boost.py',
        'parallel_chrome_test.py'
    ]
    
    for file_path in important_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"   ✅ {file_path} - {size} bytes - Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"   ❌ {file_path} - NOT FOUND")
    
    # 8. System Performance Summary
    print("\n📊 Performance Summary:")
    if cpu_percent < 30:
        print("   CPU Status: ✅ Excellent")
    elif cpu_percent < 60:
        print("   CPU Status: ⚠️ Good")
    else:
        print("   CPU Status: ❌ High Load")
    
    if memory.percent < 70:
        print("   Memory Status: ✅ Good")
    elif memory.percent < 90:
        print("   Memory Status: ⚠️ Moderate")
    else:
        print("   Memory Status: ❌ High Usage")
    
    if len(chrome_processes) == 0:
        print("   Chrome Status: ✅ Clean (No Chrome running)")
    elif len(chrome_processes) <= 2:
        print("   Chrome Status: ✅ Normal")
    else:
        print("   Chrome Status: ⚠️ Multiple instances")
    
    if len(python_processes) == 0:
        print("   Python Status: ✅ Clean (No Python running)")
    elif len(python_processes) <= 2:
        print("   Python Status: ✅ Normal")
    else:
        print("   Python Status: ⚠️ Multiple processes")
    
    print(f"\n🕐 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    check_system_status() 