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

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'backup-bygod-dashboard-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for system status
system_status = {
    'capabilities': {},
    'logs': [],
    'project_status': {},
    'last_update': datetime.now().isoformat()
}

class DashboardLogger:
    """Custom logger for dashboard"""
    
    def __init__(self):
        self.logs = []
        self.max_logs = 100
    
    def add_log(self, level, message, timestamp=None):
        """Add log entry"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        
        self.logs.append(log_entry)
        
        # Keep only recent logs
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        
        # Emit to all connected clients
        socketio.emit('new_log', log_entry)
        
        print(f"[{level.upper()}] {message}")

# Global logger instance
dashboard_logger = DashboardLogger()

def get_system_capabilities():
    """Get system capabilities status"""
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
        }
        # GPU Processing removed for future development
        # 'gpu_processing': {
        #     'name': 'GPU Processing',
        #     'description': 'การประมวลผลด้วย GPU (Future Feature)',
        #     'status': 'disabled',
        #     'icon': '🎮'
        # }
    }
    
    # Test each capability
    try:
        from core.chrome_controller import AIChromeController
        capabilities['chrome_automation']['status'] = 'ready'
        dashboard_logger.add_log('info', 'Chrome Controller พร้อมใช้งาน')
    except Exception as e:
        capabilities['chrome_automation']['status'] = 'error'
        dashboard_logger.add_log('error', f'Chrome Controller error: {str(e)}')
    
    try:
        from core.ai_integration import MultimodalAIIntegration
        capabilities['ai_integration']['status'] = 'ready'
        dashboard_logger.add_log('info', 'AI Integration พร้อมใช้งาน')
    except Exception as e:
        capabilities['ai_integration']['status'] = 'error'
        dashboard_logger.add_log('error', f'AI Integration error: {str(e)}')
    
    try:
        from core.thai_processor import FullThaiProcessor
        capabilities['thai_processor']['status'] = 'ready'
        dashboard_logger.add_log('info', 'Thai Processor พร้อมใช้งาน')
    except Exception as e:
        capabilities['thai_processor']['status'] = 'error'
        dashboard_logger.add_log('error', f'Thai Processor error: {str(e)}')
    
    try:
        from core.visual_recognition import VisualRecognition
        capabilities['visual_recognition']['status'] = 'ready'
        dashboard_logger.add_log('info', 'Visual Recognition พร้อมใช้งาน')
    except Exception as e:
        capabilities['visual_recognition']['status'] = 'error'
        dashboard_logger.add_log('error', f'Visual Recognition error: {str(e)}')
    
    try:
        from core.backup_controller import BackupController
        capabilities['backup_controller']['status'] = 'ready'
        dashboard_logger.add_log('info', 'Backup Controller พร้อมใช้งาน')
    except Exception as e:
        capabilities['backup_controller']['status'] = 'error'
        dashboard_logger.add_log('error', f'Backup Controller error: {str(e)}')
    
    # GPU Processing disabled for future development
    # try:
    #     import tensorflow as tf
    #     gpu_devices = tf.config.list_physical_devices('GPU')
    #     if gpu_devices:
    #         capabilities['gpu_processing']['status'] = 'ready'
    #         dashboard_logger.add_log('success', f'GPU พร้อมใช้งาน: {len(gpu_devices)} devices')
    #     else:
    #         capabilities['gpu_processing']['status'] = 'warning'
    #         dashboard_logger.add_log('warning', 'GPU ไม่พร้อมใช้งาน - ใช้ CPU แทน')
    # except Exception as e:
    #     capabilities['gpu_processing']['status'] = 'error'
    #     dashboard_logger.add_log('error', f'GPU error: {str(e)}')
    
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
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    system_status['capabilities'] = get_system_capabilities()
    system_status['project_status'] = get_project_status()
    system_status['logs'] = dashboard_logger.logs[-20:]  # Last 20 logs
    system_status['last_update'] = datetime.now().isoformat()
    
    return jsonify(system_status)

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
    """Background thread for periodic updates"""
    while True:
        try:
            # Update system status every 5 seconds
            system_status['capabilities'] = get_system_capabilities()
            system_status['project_status'] = get_project_status()
            system_status['last_update'] = datetime.now().isoformat()
            
            # Emit update to all clients
            socketio.emit('status_update', system_status)
            
            time.sleep(5)
        except Exception as e:
            dashboard_logger.add_log('error', f'Background update error: {str(e)}')
            time.sleep(10)

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