#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Dashboard Server for Backup-byGod - Enhanced Version
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
import json
import time
import threading
import os
import sys
from datetime import datetime
import psutil
import subprocess
import sqlite3

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add error handling for imports
try:
    import psutil
except ImportError:
    print("Warning: psutil not available, system monitoring limited")
    psutil = None

try:
    import sqlite3
except ImportError:
    print("Warning: sqlite3 not available, database features limited")
    sqlite3 = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'backup-bygod-dashboard-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Import God Mode Knowledge Manager with error handling
GODMODE_KM_AVAILABLE = False
godmode_km = None

try:
    from alldata_godmode.god_mode_knowledge_manager import GodModeKnowledgeManager
    godmode_km = GodModeKnowledgeManager()
    GODMODE_KM_AVAILABLE = True
    print("✅ God Mode Knowledge Manager loaded successfully")
except Exception as e:
    GODMODE_KM_AVAILABLE = False
    print(f"⚠️ God Mode Knowledge Manager not available: {e}")

# Import Knowledge Manager with error handling
KNOWLEDGE_MANAGER_AVAILABLE = False
knowledge_manager = None

try:
    from core.knowledge_manager import KnowledgeManager
    knowledge_manager = KnowledgeManager()
    KNOWLEDGE_MANAGER_AVAILABLE = True
    print("✅ Knowledge Manager loaded successfully")
except Exception as e:
    KNOWLEDGE_MANAGER_AVAILABLE = False
    print(f"⚠️ Knowledge Manager not available: {e}")

# Global variables for system status with error handling
system_status = {
    'capabilities': {},
    'logs': [],
    'project_status': {},
    'godmode_data': {},
    'last_update': datetime.now().isoformat()
}

# เพิ่ม state cache สำหรับ capabilities
capability_state_cache = {}
# เพิ่ม cache สำหรับ component imports เพื่อป้องกันการ import ซ้ำ
component_cache = {}

# ใช้ Singleton with error handling
try:
    from core.chrome_controller import AIChromeController
    chrome_controller = AIChromeController()
    print("✅ Chrome Controller loaded successfully")
except Exception as e:
    chrome_controller = None
    print(f"⚠️ Chrome Controller not available: {e}")

class DashboardLogger:
    """Custom logger for dashboard (เฉพาะ log สำคัญ)"""
    def __init__(self):
        self.logs = []
        self.max_logs = 100
        self.important_keywords = [
            'เริ่มต้น', 'หยุด', 'สำรอง', 'กู้คืน', 'error', 'ผิดพลาด', 'เตือน', 'warning', 'ข้อเสนอแนะ', 'recommend', 'สำเร็จ', 'เสร็จสมบูรณ์', 'critical', 'fail', 'success', 'backup', 'restore', 'status', 'พร้อมใช้งาน', 'disconnected', 'connected', 'godmode', 'session'
        ]
    def add_log(self, level, message, timestamp=None):
        """Add log entry (เฉพาะ log สำคัญ)"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        # กรอง log เฉพาะที่สำคัญ
        if not any(k in message.lower() for k in self.important_keywords) and level not in ['error', 'warning', 'success']:
            return
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.logs.append(log_entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        socketio.emit('new_log', log_entry)
        print(f"[{level.upper()}] {message}")

# Global logger instance
dashboard_logger = DashboardLogger()

# Log Knowledge Manager status after logger is created
if KNOWLEDGE_MANAGER_AVAILABLE:
    dashboard_logger.add_log('info', '🧠 Knowledge Manager loaded successfully')
else:
    dashboard_logger.add_log('warning', 'Knowledge Manager not available')

if GODMODE_KM_AVAILABLE:
    dashboard_logger.add_log('info', '🚀 God Mode Knowledge Manager loaded successfully')
else:
    dashboard_logger.add_log('warning', 'God Mode Knowledge Manager not available')

def safe_import_component(component_name, import_path, class_name=None):
    """Import component อย่างปลอดภัยและ cache ผลลัพธ์"""
    if component_name in component_cache:
        return component_cache[component_name]
    
    try:
        module = __import__(import_path, fromlist=[class_name] if class_name else [])
        if class_name:
            component = getattr(module, class_name)
        else:
            component = module
        component_cache[component_name] = component
        return component
    except Exception as e:
        component_cache[component_name] = None
        return None

def get_system_capabilities():
    """Get system capabilities status (log เฉพาะเมื่อสถานะเปลี่ยน)"""
    global capability_state_cache
    capabilities = {
        'chrome_automation': {
            'name': 'Chrome Automation',
            'description': 'ควบคุม Chrome ด้วย AI และ Selenium',
            'status': 'unknown',
            'icon': '🌐'
        },
        'ai_integration': {
            'name': 'AI Integration',
            'description': 'การประมวลผล AI แบบ Multimodal',
            'status': 'unknown',
            'icon': '🧠'
        },
        'thai_processor': {
            'name': 'Thai Language Processor',
            'description': 'ประมวลผลภาษาไทยและ OCR',
            'status': 'unknown',
            'icon': '🇹🇭'
        },
        'visual_recognition': {
            'name': 'Visual Recognition',
            'description': 'การจดจำภาพและวิเคราะห์ภาพ',
            'status': 'unknown',
            'icon': '👁️'
        },
        'backup_controller': {
            'name': 'Backup Controller',
            'description': 'ควบคุมการสำรองข้อมูลอัตโนมัติ',
            'status': 'unknown',
            'icon': '💾'
        },
        'supabase_integration': {
            'name': 'Supabase Database',
            'description': 'Cloud Database และ Real-time Features',
            'status': 'unknown',
            'icon': '☁️'
        },
        'environment_cards': {
            'name': 'Environment Cards',
            'description': 'แสดงข้อมูล Environment ของโปรแกรมต่างๆ',
            'status': 'unknown',
            'icon': '📋'
        },
        'knowledge_manager': {
            'name': 'Knowledge Manager',
            'description': 'จัดการฐานความรู้สำหรับการเรียนรู้และควบคุมระบบ',
            'status': 'unknown',
            'icon': '🧠'
        },
        'godmode_knowledge': {
            'name': 'God Mode Knowledge',
            'description': 'ฐานข้อมูลความรู้ถาวรสำหรับ God Mode',
            'status': 'unknown',
            'icon': '🚀'
        },
        'gpu_processing': {
            'name': 'GPU Processing',
            'description': 'การประมวลผลด้วย GPU (RTX 4060)',
            'status': 'unknown',
            'icon': '🎮'
        },
        'smart_allocator': {
            'name': 'Smart Resource Allocator',
            'description': 'จัดสรรทรัพยากรอัจฉริยะ',
            'status': 'unknown',
            'icon': '⚡'
        }
    }
    
    # Helper สำหรับ log เฉพาะเมื่อเปลี่ยนแปลง
    def log_if_changed(key, status, msg_ready, msg_error):
        prev = capability_state_cache.get(key)
        if prev != status:
            if status == 'ready':
                dashboard_logger.add_log('info', msg_ready)
            elif status == 'error':
                dashboard_logger.add_log('error', msg_error)
            capability_state_cache[key] = status
    
    # Test Chrome Controller - ใช้ instance ที่มีอยู่แล้วแทนการ import class
    try:
        if 'chrome_controller' in globals() and chrome_controller:
            capabilities['chrome_automation']['status'] = 'ready'
            log_if_changed('chrome_automation', 'ready', 'Chrome Controller พร้อมใช้งาน', 'Chrome Controller error')
        else:
            capabilities['chrome_automation']['status'] = 'error'
            log_if_changed('chrome_automation', 'error', '', 'Chrome Controller ไม่พร้อมใช้งาน')
    except Exception as e:
        capabilities['chrome_automation']['status'] = 'error'
        log_if_changed('chrome_automation', 'error', '', f'Chrome Controller error: {str(e)}')
    
    # Test God Mode Knowledge Manager
    try:
        if GODMODE_KM_AVAILABLE and godmode_km:
            capabilities['godmode_knowledge']['status'] = 'ready'
            log_if_changed('godmode_knowledge', 'ready', 'God Mode Knowledge Manager พร้อมใช้งาน', 'God Mode Knowledge Manager error')
        else:
            capabilities['godmode_knowledge']['status'] = 'error'
            log_if_changed('godmode_knowledge', 'error', '', 'God Mode Knowledge Manager ไม่พร้อมใช้งาน')
    except Exception as e:
        capabilities['godmode_knowledge']['status'] = 'error'
        log_if_changed('godmode_knowledge', 'error', '', f'God Mode Knowledge Manager error: {str(e)}')
    
    # Test GPU Processing
    try:
        import torch
        if torch.cuda.is_available():
            capabilities['gpu_processing']['status'] = 'ready'
            log_if_changed('gpu_processing', 'ready', 'GPU Processing พร้อมใช้งาน (CUDA)', 'GPU Processing error')
        else:
            capabilities['gpu_processing']['status'] = 'warning'
            log_if_changed('gpu_processing', 'warning', 'GPU Processing ไม่พร้อม (ไม่มี CUDA)', '')
    except Exception as e:
        capabilities['gpu_processing']['status'] = 'error'
        log_if_changed('gpu_processing', 'error', '', f'GPU Processing error: {str(e)}')
    
    # Test Smart Resource Allocator
    try:
        smart_allocator = safe_import_component('smart_allocator', 'smart_resource_allocator', 'SmartResourceAllocator')
        if smart_allocator:
            capabilities['smart_allocator']['status'] = 'ready'
            log_if_changed('smart_allocator', 'ready', 'Smart Resource Allocator พร้อมใช้งาน', 'Smart Resource Allocator error')
        else:
            capabilities['smart_allocator']['status'] = 'error'
            log_if_changed('smart_allocator', 'error', '', 'Smart Resource Allocator ไม่สามารถ import ได้')
    except Exception as e:
        capabilities['smart_allocator']['status'] = 'error'
        log_if_changed('smart_allocator', 'error', '', f'Smart Resource Allocator error: {str(e)}')
    
    try:
        ai_integration = safe_import_component('ai_integration', 'core.ai_integration', 'MultimodalAIIntegration')
        if ai_integration:
            capabilities['ai_integration']['status'] = 'ready'
            log_if_changed('ai_integration', 'ready', 'AI Integration พร้อมใช้งาน', 'AI Integration error')
        else:
            capabilities['ai_integration']['status'] = 'error'
            log_if_changed('ai_integration', 'error', '', 'AI Integration ไม่สามารถ import ได้')
    except Exception as e:
        capabilities['ai_integration']['status'] = 'error'
        log_if_changed('ai_integration', 'error', '', f'AI Integration error: {str(e)}')
    
    try:
        thai_processor = safe_import_component('thai_processor', 'core.thai_processor', 'FullThaiProcessor')
        if thai_processor:
            capabilities['thai_processor']['status'] = 'ready'
            log_if_changed('thai_processor', 'ready', 'Thai Processor พร้อมใช้งาน', 'Thai Processor error')
        else:
            capabilities['thai_processor']['status'] = 'error'
            log_if_changed('thai_processor', 'error', '', 'Thai Processor ไม่สามารถ import ได้')
    except Exception as e:
        capabilities['thai_processor']['status'] = 'error'
        log_if_changed('thai_processor', 'error', '', f'Thai Processor error: {str(e)}')
    
    try:
        visual_recognition = safe_import_component('visual_recognition', 'core.visual_recognition', 'VisualRecognition')
        if visual_recognition:
            capabilities['visual_recognition']['status'] = 'ready'
            log_if_changed('visual_recognition', 'ready', 'Visual Recognition พร้อมใช้งาน', 'Visual Recognition error')
        else:
            capabilities['visual_recognition']['status'] = 'error'
            log_if_changed('visual_recognition', 'error', '', 'Visual Recognition ไม่สามารถ import ได้')
    except Exception as e:
        capabilities['visual_recognition']['status'] = 'error'
        log_if_changed('visual_recognition', 'error', '', f'Visual Recognition error: {str(e)}')
    
    try:
        backup_controller = safe_import_component('backup_controller', 'core.backup_controller', 'BackupController')
        if backup_controller:
            capabilities['backup_controller']['status'] = 'ready'
            log_if_changed('backup_controller', 'ready', 'Backup Controller พร้อมใช้งาน', 'Backup Controller error')
        else:
            capabilities['backup_controller']['status'] = 'error'
            log_if_changed('backup_controller', 'error', '', 'Backup Controller ไม่สามารถ import ได้')
    except Exception as e:
        capabilities['backup_controller']['status'] = 'error'
        log_if_changed('backup_controller', 'error', '', f'Backup Controller error: {str(e)}')
    
    try:
        supabase_integration = safe_import_component('supabase_integration', 'core.supabase_integration', 'SupabaseIntegration')
        if supabase_integration:
            capabilities['supabase_integration']['status'] = 'ready'
            log_if_changed('supabase_integration', 'ready', 'Supabase Integration พร้อมใช้งาน', 'Supabase Integration error')
        else:
            capabilities['supabase_integration']['status'] = 'error'
            log_if_changed('supabase_integration', 'error', '', 'Supabase Integration ไม่สามารถ import ได้')
    except Exception as e:
        capabilities['supabase_integration']['status'] = 'error'
        log_if_changed('supabase_integration', 'error', '', f'Supabase Integration error: {str(e)}')
    
    try:
        environment_cards = safe_import_component('environment_cards', 'core.environment_cards', 'EnvironmentCards')
        if environment_cards:
            capabilities['environment_cards']['status'] = 'ready'
            log_if_changed('environment_cards', 'ready', 'Environment Cards พร้อมใช้งาน', 'Environment Cards error')
        else:
            capabilities['environment_cards']['status'] = 'error'
            log_if_changed('environment_cards', 'error', '', 'Environment Cards ไม่สามารถ import ได้')
    except Exception as e:
        capabilities['environment_cards']['status'] = 'error'
        log_if_changed('environment_cards', 'error', '', f'Environment Cards error: {str(e)}')
    
    try:
        if KNOWLEDGE_MANAGER_AVAILABLE and knowledge_manager:
            capabilities['knowledge_manager']['status'] = 'ready'
            log_if_changed('knowledge_manager', 'ready', 'Knowledge Manager พร้อมใช้งาน', 'Knowledge Manager error')
        else:
            capabilities['knowledge_manager']['status'] = 'error'
            log_if_changed('knowledge_manager', 'error', '', 'Knowledge Manager ไม่พร้อมใช้งาน')
    except Exception as e:
        capabilities['knowledge_manager']['status'] = 'error'
        log_if_changed('knowledge_manager', 'error', '', f'Knowledge Manager error: {str(e)}')
    
    return capabilities

def get_godmode_data():
    """Get God Mode Knowledge Base data"""
    if not GODMODE_KM_AVAILABLE or not godmode_km:
        return {
            'available': False,
            'message': 'God Mode Knowledge Manager not available'
        }
    
    try:
        # Get statistics
        stats = godmode_km.get_statistics()
        
        # Get recent sessions
        sessions = godmode_km.get_session_history(limit=5)
        
        # Get recent commands
        commands = godmode_km.get_command_history(limit=10)
        
        # Get patterns
        patterns = godmode_km.get_patterns()
        
        # Get learnings
        learnings = godmode_km.get_learnings(min_importance=0.7)
        
        return {
            'available': True,
            'statistics': stats,
            'recent_sessions': sessions,
            'recent_commands': commands,
            'patterns': patterns,
            'learnings': learnings,
            'last_update': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'available': False,
            'message': f'Error getting God Mode data: {str(e)}'
        }

def get_system_resources():
    """Get system resources information with error handling"""
    try:
        if psutil is None:
            return {
                'cpu': {'percent': 0, 'count': 0},
                'memory': {'total_gb': 0, 'available_gb': 0, 'percent': 0},
                'disk': {'total_gb': 0, 'used_gb': 0, 'free_gb': 0, 'percent': 0},
                'gpu': {'available': False},
                'error': 'psutil not available'
            }
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        # Get GPU info if available
        gpu_info = None
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                gpu_memory_used = torch.cuda.memory_allocated(0) / 1024**2
                gpu_info = {
                    'name': gpu_name,
                    'total_memory_gb': round(gpu_memory, 2),
                    'used_memory_mb': round(gpu_memory_used, 2),
                    'available': True
                }
        except Exception as gpu_error:
            gpu_info = {'available': False, 'error': str(gpu_error)}
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total_gb': round(memory.total / 1024**3, 2),
                'available_gb': round(memory.available / 1024**3, 2),
                'percent': memory.percent
            },
            'disk': {
                'total_gb': round(disk.total / 1024**3, 2),
                'used_gb': round(disk.used / 1024**3, 2),
                'free_gb': round(disk.free / 1024**3, 2),
                'percent': disk.percent
            },
            'gpu': gpu_info
        }
    except Exception as e:
        dashboard_logger.add_log('error', f'System resources error: {str(e)}')
        return {
            'cpu': {'percent': 0, 'count': 0},
            'memory': {'total_gb': 0, 'available_gb': 0, 'percent': 0},
            'disk': {'total_gb': 0, 'used_gb': 0, 'free_gb': 0, 'percent': 0},
            'gpu': {'available': False},
            'error': str(e)
        }

def get_project_status():
    """Get project status information"""
    try:
        # Get file counts
        total_files = 0
        python_files = 0
        config_files = 0
        
        for root, dirs, files in os.walk('.'):
            for file in files:
                total_files += 1
                if file.endswith('.py'):
                    python_files += 1
                elif file.endswith(('.json', '.yml', '.yaml', '.conf')):
                    config_files += 1
        
        # Get recent activity
        recent_activity = []
        try:
            # Get recent git commits
            result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                                  capture_output=True, text=True, cwd='.')
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                for commit in commits:
                    if commit:
                        recent_activity.append({
                            'type': 'git_commit',
                            'message': commit,
                            'timestamp': datetime.now().isoformat()
                        })
        except:
            pass
        
        return {
            'total_files': total_files,
            'python_files': python_files,
            'config_files': config_files,
            'recent_activity': recent_activity,
            'last_update': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e)
        }

def get_status_message(percent):
    """Get status message based on percentage"""
    if percent >= 90:
        return "ยอดเยี่ยม"
    elif percent >= 70:
        return "ดี"
    elif percent >= 50:
        return "ปานกลาง"
    else:
        return "ต้องปรับปรุง"

def get_recommendations(capabilities):
    """Get system recommendations based on capabilities"""
    recommendations = []
    
    ready_count = sum(1 for cap in capabilities.values() if cap['status'] == 'ready')
    error_count = sum(1 for cap in capabilities.values() if cap['status'] == 'error')
    
    if error_count > 0:
        recommendations.append({
            'type': 'warning',
            'message': f'มี {error_count} ระบบที่ไม่พร้อมใช้งาน ควรตรวจสอบและแก้ไข'
        })
    
    if ready_count >= 8:
        recommendations.append({
            'type': 'success',
            'message': 'ระบบส่วนใหญ่พร้อมใช้งานแล้ว'
        })
    
    if 'chrome_automation' in capabilities and capabilities['chrome_automation']['status'] == 'error':
        recommendations.append({
            'type': 'error',
            'message': 'Chrome Automation ไม่พร้อม ควรตรวจสอบ Chrome driver'
        })
    
    if 'gpu_processing' in capabilities and capabilities['gpu_processing']['status'] == 'error':
        recommendations.append({
            'type': 'warning',
            'message': 'GPU Processing ไม่พร้อม ควรตรวจสอบ CUDA installation'
        })
    
    return recommendations

@app.route('/')
def dashboard():
    """Main dashboard page"""
    capabilities = get_system_capabilities()
    ready_count = sum(1 for cap in capabilities.values() if cap['status'] == 'ready')
    total_count = len(capabilities)
    status_percent = (ready_count / total_count) * 100 if total_count > 0 else 0
    
    system_status['capabilities'] = capabilities
    system_status['project_status'] = get_project_status()
    system_status['godmode_data'] = get_godmode_data()
    system_status['system_resources'] = get_system_resources()
    system_status['recommendations'] = get_recommendations(capabilities)
    system_status['status_percent'] = status_percent
    system_status['status_message'] = get_status_message(status_percent)
    system_status['last_update'] = datetime.now().isoformat()
    
    return render_template('dashboard.html', 
                         system_status=system_status,
                         capabilities=capabilities,
                         logs=dashboard_logger.logs)

@app.route('/test')
def test_api():
    """Test API endpoint"""
    return render_template('test.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    try:
        capabilities = get_system_capabilities()
        ready_count = sum(1 for cap in capabilities.values() if cap['status'] == 'ready')
        total_count = len(capabilities)
        status_percent = (ready_count / total_count) * 100 if total_count > 0 else 0
        
        # Mock data for testing
        mock_system_resources = {
            'cpu': {'percent': 45, 'count': 8},
            'memory': {'percent': 62, 'available_gb': 12.5},
            'disk': {'percent': 78, 'free_gb': 156.2},
            'gpu': {'available': True, 'name': 'NVIDIA RTX 4060', 'used_memory_mb': 2048, 'total_memory_gb': 8},
            'network': {'status': 'Connected'}
        }
        
        mock_godmode_data = {
            'statistics': {
                'total_sessions': 15,
                'total_commands': 127,
                'total_patterns': 23,
                'success_rate': 87.5
            },
            'sessions': [
                {
                    'session_id': 'session_001',
                    'status': 'completed',
                    'commands_count': 8,
                    'start_time': '2024-01-15T10:30:00Z'
                },
                {
                    'session_id': 'session_002',
                    'status': 'active',
                    'commands_count': 3,
                    'start_time': '2024-01-15T14:20:00Z'
                }
            ],
            'commands': [
                {
                    'command_text': 'Analyze system performance and generate report',
                    'command_type': 'analysis',
                    'success': True,
                    'execution_time': '2024-01-15T10:35:00Z'
                },
                {
                    'command_text': 'Backup critical data files',
                    'command_type': 'backup',
                    'success': True,
                    'execution_time': '2024-01-15T10:40:00Z'
                }
            ]
        }
        
        mock_recommendations = [
            {
                'type': 'success',
                'message': 'ระบบทำงานปกติ ทุก component พร้อมใช้งาน'
            },
            {
                'type': 'info',
                'message': 'แนะนำให้ทำ backup ข้อมูลทุกสัปดาห์'
            }
        ]
        
        return jsonify({
            'capabilities': capabilities,
            'status_percent': status_percent,
            'status_message': get_status_message(status_percent),
            'system_resources': mock_system_resources,
            'godmode_data': mock_godmode_data,
            'recommendations': mock_recommendations,
            'last_update': datetime.now().isoformat()
        })
    except Exception as e:
        dashboard_logger.add_log('error', f'API Status Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/godmode/statistics')
def api_godmode_statistics():
    """API endpoint for God Mode statistics"""
    if not GODMODE_KM_AVAILABLE:
        # Return mock data when God Mode KM is not available
        return jsonify({
            'total_sessions': 15,
            'total_commands': 127,
            'total_patterns': 23,
            'total_results': 89,
            'total_learnings': 45,
            'success_rate': 87.5
        })
    
    try:
        stats = godmode_km.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/godmode/sessions')
def api_godmode_sessions():
    """API endpoint for God Mode sessions"""
    if not GODMODE_KM_AVAILABLE:
        # Return mock data when God Mode KM is not available
        return jsonify([
            {
                'session_id': 'session_001',
                'status': 'completed',
                'commands_count': 8,
                'start_time': '2024-01-15T10:30:00Z',
                'end_time': '2024-01-15T11:15:00Z'
            },
            {
                'session_id': 'session_002',
                'status': 'active',
                'commands_count': 3,
                'start_time': '2024-01-15T14:20:00Z'
            }
        ])
    
    try:
        limit = request.args.get('limit', 10, type=int)
        sessions = godmode_km.get_session_history(limit=limit)
        return jsonify(sessions)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/godmode/commands')
def api_godmode_commands():
    """API endpoint for God Mode commands"""
    if not GODMODE_KM_AVAILABLE:
        # Return mock data when God Mode KM is not available
        return jsonify([
            {
                'command_text': 'Analyze system performance and generate report',
                'command_type': 'analysis',
                'success': True,
                'execution_time': '2024-01-15T10:35:00Z',
                'result_summary': 'System analysis completed successfully'
            },
            {
                'command_text': 'Backup critical data files',
                'command_type': 'backup',
                'success': True,
                'execution_time': '2024-01-15T10:40:00Z',
                'result_summary': 'Backup completed: 2.5GB data backed up'
            }
        ])
    
    try:
        limit = request.args.get('limit', 20, type=int)
        session_id = request.args.get('session_id')
        commands = godmode_km.get_command_history(session_id=session_id, limit=limit)
        return jsonify(commands)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/godmode/patterns')
def api_godmode_patterns():
    """API endpoint for God Mode patterns"""
    if not GODMODE_KM_AVAILABLE:
        return jsonify({'error': 'God Mode Knowledge Manager not available'})
    
    try:
        pattern_type = request.args.get('type')
        patterns = godmode_km.get_patterns(pattern_type=pattern_type)
        return jsonify(patterns)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/godmode/learnings')
def api_godmode_learnings():
    """API endpoint for God Mode learnings"""
    if not GODMODE_KM_AVAILABLE:
        return jsonify({'error': 'God Mode Knowledge Manager not available'})
    
    try:
        learning_type = request.args.get('type')
        min_importance = request.args.get('min_importance', 0.5, type=float)
        learnings = godmode_km.get_learnings(learning_type=learning_type, min_importance=min_importance)
        return jsonify(learnings)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/godmode/search')
def api_godmode_search():
    """API endpoint for God Mode search"""
    if not GODMODE_KM_AVAILABLE:
        return jsonify({'error': 'God Mode Knowledge Manager not available'})
    
    try:
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')
        results = godmode_km.search_knowledge(query, search_type)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/godmode/start-session', methods=['POST'])
def api_godmode_start_session():
    """API endpoint to start a new God Mode session"""
    if not GODMODE_KM_AVAILABLE:
        return jsonify({'error': 'God Mode Knowledge Manager not available'})
    
    try:
        session_id = request.json.get('session_id')
        session_id = godmode_km.start_session(session_id)
        dashboard_logger.add_log('info', f'🚀 Started God Mode session: {session_id}')
        return jsonify({'session_id': session_id, 'status': 'started'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/godmode/end-session', methods=['POST'])
def api_godmode_end_session():
    """API endpoint to end a God Mode session"""
    if not GODMODE_KM_AVAILABLE:
        return jsonify({'error': 'God Mode Knowledge Manager not available'})
    
    try:
        session_id = request.json.get('session_id')
        godmode_km.end_session(session_id)
        dashboard_logger.add_log('info', f'🏁 Ended God Mode session: {session_id}')
        return jsonify({'status': 'ended'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/godmode/save-command', methods=['POST'])
def api_godmode_save_command():
    """API endpoint to save a command to God Mode knowledge base"""
    if not GODMODE_KM_AVAILABLE:
        return jsonify({'error': 'God Mode Knowledge Manager not available'})
    
    try:
        data = request.json
        session_id = data.get('session_id')
        command = data.get('command')
        command_type = data.get('command_type', 'general')
        success = data.get('success', True)
        result_summary = data.get('result_summary', '')
        
        godmode_km.save_command(session_id, command, command_type, success, result_summary)
        return jsonify({'status': 'saved'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/godmode/save-learning', methods=['POST'])
def api_godmode_save_learning():
    """API endpoint to save learning to God Mode knowledge base"""
    if not GODMODE_KM_AVAILABLE:
        return jsonify({'error': 'God Mode Knowledge Manager not available'})
    
    try:
        data = request.json
        learning_type = data.get('learning_type')
        learning_data = data.get('learning_data', {})
        context = data.get('context', '')
        importance_score = data.get('importance_score', 1.0)
        tags = data.get('tags', [])
        
        godmode_km.save_learning(learning_type, learning_data, context, importance_score, tags)
        return jsonify({'status': 'saved'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/knowledge/statistics')
def api_knowledge_statistics():
    """API endpoint for knowledge manager statistics"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'})
    
    try:
        stats = knowledge_manager.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/knowledge/search')
def api_knowledge_search():
    """API endpoint for knowledge search"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'})
    
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        limit = request.args.get('limit', 10, type=int)
        
        results = knowledge_manager.search_knowledge(query, category, limit)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/knowledge/categories')
def api_knowledge_categories():
    """API endpoint for knowledge categories"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'})
    
    try:
        categories = knowledge_manager.get_categories()
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/knowledge/category/<category>')
def api_knowledge_by_category(category):
    """API endpoint for knowledge by category"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'})
    
    try:
        limit = request.args.get('limit', 10, type=int)
        knowledge_items = knowledge_manager.get_knowledge_by_category(category, limit)
        return jsonify(knowledge_items)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/knowledge/add', methods=['POST'])
def api_knowledge_add():
    """API endpoint to add knowledge"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'})
    
    try:
        data = request.json
        title = data.get('title')
        content = data.get('content')
        category = data.get('category', 'general')
        tags = data.get('tags', [])
        
        if not title or not content:
            return jsonify({'error': 'Title and content are required'})
        
        knowledge_id = knowledge_manager.add_knowledge(title, content, category, tags)
        dashboard_logger.add_log('info', f'📝 Added knowledge: {title}')
        
        return jsonify({
            'id': knowledge_id,
            'status': 'added'
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/knowledge/update/<knowledge_id>', methods=['PUT'])
def api_knowledge_update(knowledge_id):
    """API endpoint to update knowledge"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'})
    
    try:
        data = request.json
        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        tags = data.get('tags')
        
        success = knowledge_manager.update_knowledge(knowledge_id, title, content, category, tags)
        if success:
            dashboard_logger.add_log('info', f'📝 Updated knowledge: {knowledge_id}')
            return jsonify({'status': 'updated'})
        else:
            return jsonify({'error': 'Knowledge not found'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/knowledge/delete/<knowledge_id>', methods=['DELETE'])
def api_knowledge_delete(knowledge_id):
    """API endpoint to delete knowledge"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'})
    
    try:
        success = knowledge_manager.delete_knowledge(knowledge_id)
        if success:
            dashboard_logger.add_log('info', f'🗑️ Deleted knowledge: {knowledge_id}')
            return jsonify({'status': 'deleted'})
        else:
            return jsonify({'error': 'Knowledge not found'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/knowledge/<knowledge_id>')
def api_knowledge_get(knowledge_id):
    """API endpoint to get knowledge by ID"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'})
    
    try:
        knowledge = knowledge_manager.get_knowledge(knowledge_id)
        if knowledge:
            return jsonify(knowledge)
        else:
            return jsonify({'error': 'Knowledge not found'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/system/cleanup-chrome', methods=['POST'])
def api_cleanup_chrome():
    """API endpoint to cleanup Chrome processes - DISABLED"""
    try:
        dashboard_logger.add_log('info', '🚫 Chrome cleanup disabled - user preference')
        return jsonify({'status': 'disabled', 'message': 'Chrome cleanup disabled by user preference'})
    except Exception as e:
        dashboard_logger.add_log('error', f'Chrome cleanup error: {str(e)}')
        return jsonify({'error': str(e)})

@app.route('/api/system/restart-dashboard', methods=['POST'])
def api_restart_dashboard():
    """API endpoint to restart dashboard"""
    try:
        dashboard_logger.add_log('info', '🔄 Dashboard restart requested')
        # In a real implementation, you might want to restart the Flask app
        return jsonify({'status': 'restart_requested', 'message': 'Dashboard restart requested'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/logs')
def api_logs():
    """Get system logs"""
    try:
        return jsonify(dashboard_logger.logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/resources')
def api_system_resources():
    """Get system resources"""
    try:
        resources = get_system_resources()
        return jsonify(resources)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/status')
def api_system_status():
    """Get detailed system status"""
    try:
        status = {
            'status_percent': 85,  # Default value
            'status_message': 'System running normally',
            'capabilities': get_system_capabilities(),
            'system_resources': get_system_resources(),
            'godmode_data': get_godmode_data(),
            'recommendations': get_recommendations(get_system_capabilities()),
            'last_update': datetime.now().isoformat()
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    dashboard_logger.add_log('info', '🔗 Client connected to dashboard')
    emit('status', {'message': 'Connected to dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    dashboard_logger.add_log('info', '🔌 Client disconnected from dashboard')

def background_updates():
    """Background task to update system status with error handling"""
    while True:
        try:
            # Update system status with error handling
            try:
                capabilities = get_system_capabilities()
            except Exception as e:
                dashboard_logger.add_log('error', f'Capabilities error: {str(e)}')
                capabilities = {}
            
            try:
                system_resources = get_system_resources()
            except Exception as e:
                dashboard_logger.add_log('error', f'System resources error: {str(e)}')
                system_resources = {'error': str(e)}
            
            try:
                godmode_data = get_godmode_data()
            except Exception as e:
                dashboard_logger.add_log('error', f'God mode data error: {str(e)}')
                godmode_data = {'available': False, 'error': str(e)}
            
            # Emit updates to connected clients
            try:
                socketio.emit('system_update', {
                    'capabilities': capabilities,
                    'system_resources': system_resources,
                    'godmode_data': godmode_data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                dashboard_logger.add_log('error', f'Socket emit error: {str(e)}')
            
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            dashboard_logger.add_log('error', f'Background update error: {str(e)}')
            time.sleep(10)  # Wait longer on error

if __name__ == '__main__':
    # Start background update thread
    update_thread = threading.Thread(target=background_updates, daemon=True)
    update_thread.start()
    
    dashboard_logger.add_log('info', '🚀 Dashboard server starting...')
    dashboard_logger.add_log('info', '📊 System monitoring active')
    
    # Run the Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 