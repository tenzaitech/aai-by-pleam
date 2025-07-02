#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time Dashboard Server for Backup-byGod
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import time
import threading
import os
import sys
from datetime import datetime
import psutil
import subprocess

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'backup-bygod-dashboard-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Import Knowledge Manager
KNOWLEDGE_MANAGER_AVAILABLE = False
knowledge_manager = None

try:
    from core.knowledge_manager import knowledge_manager
    KNOWLEDGE_MANAGER_AVAILABLE = True
except Exception as e:
    KNOWLEDGE_MANAGER_AVAILABLE = False

# Global variables for system status
system_status = {
    'capabilities': {},
    'logs': [],
    'project_status': {},
    'last_update': datetime.now().isoformat()
}
# เพิ่ม state cache สำหรับ capabilities
capability_state_cache = {}
# เพิ่ม cache สำหรับ component imports เพื่อป้องกันการ import ซ้ำ
component_cache = {}

# ใช้ Singleton
from core.chrome_controller import AIChromeController
chrome_controller = AIChromeController()

class DashboardLogger:
    """Custom logger for dashboard (เฉพาะ log สำคัญ)"""
    def __init__(self):
        self.logs = []
        self.max_logs = 100
        self.important_keywords = [
            'เริ่มต้น', 'หยุด', 'สำรอง', 'กู้คืน', 'error', 'ผิดพลาด', 'เตือน', 'warning', 'ข้อเสนอแนะ', 'recommend', 'สำเร็จ', 'เสร็จสมบูรณ์', 'critical', 'fail', 'success', 'backup', 'restore', 'status', 'พร้อมใช้งาน', 'disconnected', 'connected'
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
    
    # Test Supabase Integration
    try:
        supabase_integration = safe_import_component('supabase_integration', 'core.supabase_integration', 'supabase_integration')
        if supabase_integration:
            supabase_status = supabase_integration.get_status()
            
            if supabase_status["library_available"] and supabase_status["credentials_configured"]:
                if supabase_integration.connect():
                    capabilities['supabase_integration']['status'] = 'ready'
                    log_if_changed('supabase_integration', 'ready', 'Supabase Database เชื่อมต่อสำเร็จ', 'Supabase Database error')
                else:
                    capabilities['supabase_integration']['status'] = 'warning'
                    log_if_changed('supabase_integration', 'warning', '', 'Supabase Database ไม่สามารถเชื่อมต่อได้')
            else:
                capabilities['supabase_integration']['status'] = 'warning'
                log_if_changed('supabase_integration', 'warning', '', 'Supabase Database ไม่ได้ตั้งค่า credentials')
        else:
            capabilities['supabase_integration']['status'] = 'error'
            log_if_changed('supabase_integration', 'error', '', 'Supabase Integration ไม่สามารถ import ได้')
    except Exception as e:
        capabilities['supabase_integration']['status'] = 'error'
        log_if_changed('supabase_integration', 'error', '', f'Supabase Database error: {str(e)}')
    
    # Test Environment Cards
    try:
        env_cards = safe_import_component('environment_cards', 'core.environment_cards', 'env_cards')
        if env_cards:
            env_cards.generate_all_cards()
            capabilities['environment_cards']['status'] = 'ready'
            log_if_changed('environment_cards', 'ready', 'Environment Cards พร้อมใช้งาน', 'Environment Cards error')
        else:
            capabilities['environment_cards']['status'] = 'error'
            log_if_changed('environment_cards', 'error', '', 'Environment Cards ไม่สามารถ import ได้')
    except Exception as e:
        capabilities['environment_cards']['status'] = 'error'
        log_if_changed('environment_cards', 'error', '', f'Environment Cards error: {str(e)}')
    
    # Test Knowledge Manager
    if KNOWLEDGE_MANAGER_AVAILABLE:
        capabilities['knowledge_manager']['status'] = 'ready'
        log_if_changed('knowledge_manager', 'ready', 'Knowledge Manager พร้อมใช้งาน', 'Knowledge Manager error')
    else:
        capabilities['knowledge_manager']['status'] = 'warning'
        log_if_changed('knowledge_manager', 'warning', '', 'Knowledge Manager ไม่พร้อมใช้งาน')
    
    return capabilities

def get_project_status():
    """Get current project status"""
    # Get system resources
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Calculate overall readiness
    capabilities = get_system_capabilities()
    ready_count = sum(1 for cap in capabilities.values() if cap['status'] == 'ready')
    total_count = len(capabilities)
    readiness_percent = (ready_count / total_count) * 100
    
    status = {
        'readiness_percent': round(readiness_percent, 1),
        'ready_components': ready_count,
        'total_components': total_count,
        'system_resources': {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': (disk.used / disk.total) * 100
        },
        'last_update': datetime.now().isoformat(),
        'status_message': get_status_message(readiness_percent),
        'recommendations': get_recommendations(capabilities)
    }
    
    return status

def get_status_message(percent):
    """Get friendly status message"""
    if percent >= 90:
        return "🎉 ระบบพร้อมใช้งานเต็มรูปแบบ!"
    elif percent >= 70:
        return "✅ ระบบพร้อมใช้งานส่วนใหญ่"
    elif percent >= 50:
        return "⚠️ ระบบพร้อมใช้งานบางส่วน"
    else:
        return "❌ ระบบมีปัญหา ต้องแก้ไข"

def get_recommendations(capabilities):
    """Get recommendations based on capabilities"""
    recommendations = []
    
    for cap_name, cap_data in capabilities.items():
        if cap_data['status'] == 'error':
            recommendations.append(f"🔧 แก้ไข {cap_data['name']}")
        elif cap_data['status'] == 'warning':
            recommendations.append(f"⚡ ปรับปรุง {cap_data['name']}")
    
    if not recommendations:
        recommendations.append("🎯 ระบบทำงานได้ดีแล้ว!")
    
    return recommendations

@app.route('/')
def dashboard():
    """Main dashboard page"""
    global system_status
    
    # ใช้ cache capabilities แทนการเรียกใหม่ทุกครั้ง
    if 'capabilities' not in system_status or not system_status['capabilities']:
        system_status['capabilities'] = get_system_capabilities()
    
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    global system_status
    
    # ใช้ cache capabilities แทนการเรียกใหม่ทุกครั้ง
    if 'capabilities' not in system_status or not system_status['capabilities']:
        system_status['capabilities'] = get_system_capabilities()
    
    return jsonify(system_status)

# Knowledge Manager API Routes
@app.route('/api/knowledge/statistics')
def api_knowledge_statistics():
    """Get knowledge base statistics"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'}), 503
    
    try:
        stats = knowledge_manager.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/search')
def api_knowledge_search():
    """Search knowledge base"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'}), 503
    
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', None)
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        results = knowledge_manager.search_knowledge(query, category, limit)
        return jsonify({'results': results, 'query': query})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/categories')
def api_knowledge_categories():
    """Get all categories"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'}), 503
    
    try:
        categories = knowledge_manager.get_categories()
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/category/<category>')
def api_knowledge_by_category(category):
    """Get knowledge by category"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'}), 503
    
    try:
        knowledge = knowledge_manager.get_knowledge_by_category(category)
        return jsonify({'knowledge': knowledge, 'category': category})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/add', methods=['POST'])
def api_knowledge_add():
    """Add knowledge from URL or text"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'}), 503
    
    try:
        data = request.get_json()
        
        if data.get('type') == 'url':
            result = knowledge_manager.add_knowledge_from_url(
                url=data['url'],
                category=data['category'],
                title=data.get('title'),
                description=data.get('description')
            )
        elif data.get('type') == 'text':
            result = knowledge_manager.add_knowledge_from_text(
                title=data['title'],
                content=data['content'],
                category=data['category'],
                description=data.get('description')
            )
        else:
            return jsonify({'error': 'Invalid type. Use "url" or "text"'}), 400
        
        if result['success']:
            dashboard_logger.add_log('success', f'Knowledge added: {data.get("title", data.get("url", "Unknown"))}')
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/update/<knowledge_id>', methods=['PUT'])
def api_knowledge_update(knowledge_id):
    """Update knowledge item"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'}), 503
    
    try:
        data = request.get_json()
        result = knowledge_manager.update_knowledge(knowledge_id, data)
        
        if result['success']:
            dashboard_logger.add_log('success', f'Knowledge updated: {knowledge_id}')
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/delete/<knowledge_id>', methods=['DELETE'])
def api_knowledge_delete(knowledge_id):
    """Delete knowledge item"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'}), 503
    
    try:
        result = knowledge_manager.delete_knowledge(knowledge_id)
        
        if result['success']:
            dashboard_logger.add_log('success', f'Knowledge deleted: {knowledge_id}')
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/<knowledge_id>')
def api_knowledge_get(knowledge_id):
    """Get knowledge item by ID"""
    if not KNOWLEDGE_MANAGER_AVAILABLE:
        return jsonify({'error': 'Knowledge Manager not available'}), 503
    
    try:
        knowledge = knowledge_manager.get_knowledge_by_id(knowledge_id)
        if knowledge:
            return jsonify(knowledge)
        else:
            return jsonify({'error': 'Knowledge not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    dashboard_logger.add_log('info', f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to Backup-byGod Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    dashboard_logger.add_log('info', f'Client disconnected: {request.sid}')

def background_updates():
    """Background updates for real-time data"""
    while True:
        try:
            # อัปเดตทุก 60 วินาทีแทนที่จะเป็น 30 วินาที
            time.sleep(60)
            
            # Auto cleanup chrome.exe ทุก 1 นาที
            try:
                subprocess.call(['taskkill', '/F', '/IM', 'chrome.exe'], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("[AUTO CLEANUP] Killed chrome.exe processes")
            except Exception as e:
                print(f"[AUTO CLEANUP] Failed to kill chrome.exe: {e}")
            
            # อัปเดต system status (ไม่เรียก get_system_capabilities() บ่อย)
            global system_status
            system_status['last_update'] = datetime.now().isoformat()
            
            # อัปเดต project status
            system_status['project_status'] = get_project_status()
            
            # ส่งข้อมูลไปยัง clients
            socketio.emit('status_update', system_status)
            
        except Exception as e:
            print(f"Background update error: {e}")
            time.sleep(120)  # รอ 2 นาทีถ้าเกิดข้อผิดพลาด

if __name__ == '__main__':
    # Start background update thread
    update_thread = threading.Thread(target=background_updates, daemon=True)
    update_thread.start()
    
    # Add initial log
    dashboard_logger.add_log('info', '🚀 Dashboard Server เริ่มต้น')
    dashboard_logger.add_log('info', '📊 ระบบพร้อมรับการเชื่อมต่อ')
    dashboard_logger.add_log('info', '🎮 GPU Processing ถูกปิดใช้งาน (เก็บไว้สำหรับอนาคต)')
    
    # Run the server
    print("🌐 Dashboard Server เริ่มต้นที่ http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 