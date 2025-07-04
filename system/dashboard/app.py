#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GOD MODE Dashboard - Main Application
A comprehensive dashboard for monitoring and controlling the GOD MODE system
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import psutil
import GPUtil

# Add current directory to path for logging imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core', 'logging'))

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import logging components
try:
    from system.core.logging.logger_manager import get_logger_manager
    from system.core.logging.workflow_monitor import get_workflow_monitor
    from system.core.logging.performance_tracker import get_performance_tracker
    from system.core.logging.alert_system import get_alert_system
    LOGGING_AVAILABLE = True
    print("✅ Logging system loaded successfully")
except Exception as e:
    LOGGING_AVAILABLE = False
    print(f"⚠️ Logging system not available: {e}")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'godmode_dashboard_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
capability_state_cache = {}
component_cache = {}

# Import components with error handling
try:
    from system.core.controllers.chrome_controller import AIChromeController
    chrome_controller = AIChromeController()
    print("✅ Chrome Controller loaded successfully")
except Exception as e:
    chrome_controller = None
    print(f"⚠️ Chrome Controller not available: {e}")

try:
    from system.core.controllers.knowledge_manager import KnowledgeManager
    knowledge_manager = KnowledgeManager()
    KNOWLEDGE_MANAGER_AVAILABLE = True
    print("✅ Knowledge Manager loaded successfully")
except Exception as e:
    knowledge_manager = None
    KNOWLEDGE_MANAGER_AVAILABLE = False
    print(f"⚠️ Knowledge Manager not available: {e}")

try:
    from system.godmode.god_mode_knowledge_manager import GodModeKnowledgeManager
    godmode_km = GodModeKnowledgeManager()
    GODMODE_KM_AVAILABLE = True
    print("✅ God Mode Knowledge Manager loaded successfully")
except Exception as e:
    godmode_km = None
    GODMODE_KM_AVAILABLE = False
    print(f"⚠️ God Mode Knowledge Manager not available: {e}")

class DashboardLogger:
    """Custom logger for dashboard"""
    def __init__(self):
        self.logs = []
        self.max_logs = 100
        self.important_keywords = [
            'start', 'stop', 'backup', 'restore', 'error', 'warning', 'success',
            'critical', 'fail', 'ready', 'disconnected', 'connected', 'godmode'
        ]
    
    def add_log(self, level, message, timestamp=None):
        """Add log entry"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        # Filter important logs only
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
        
        try:
            socketio.emit('new_log', log_entry)
        except:
            pass
        print(f"[{level.upper()}] {message}")

# Global logger instance
dashboard_logger = DashboardLogger()

# Log component status
if KNOWLEDGE_MANAGER_AVAILABLE:
    dashboard_logger.add_log('info', 'Knowledge Manager loaded successfully')
else:
    dashboard_logger.add_log('warning', 'Knowledge Manager not available')

if GODMODE_KM_AVAILABLE:
    dashboard_logger.add_log('info', 'God Mode Knowledge Manager loaded successfully')
else:
    dashboard_logger.add_log('warning', 'God Mode Knowledge Manager not available')

def safe_import_component(component_name, import_path, class_name=None):
    """Import component safely and cache result"""
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
    """Get system capabilities status"""
    global capability_state_cache
    capabilities = {
        'chrome_automation': {
            'name': 'Chrome Automation',
            'description': 'Control Chrome with AI and Selenium',
            'status': 'unknown',
            'icon': '🌐'
        },
        'ai_integration': {
            'name': 'AI Integration',
            'description': 'Multimodal AI Processing',
            'status': 'unknown',
            'icon': '🧠'
        },
        'thai_processor': {
            'name': 'Thai Language Processor',
            'description': 'Thai language processing and OCR',
            'status': 'unknown',
            'icon': '🇹🇭'
        },
        'visual_recognition': {
            'name': 'Visual Recognition',
            'description': 'Image recognition and analysis',
            'status': 'unknown',
            'icon': '👁️'
        },
        'backup_controller': {
            'name': 'Backup Controller',
            'description': 'Automated backup control',
            'status': 'unknown',
            'icon': '💾'
        },
        'supabase_integration': {
            'name': 'Supabase Database',
            'description': 'Cloud Database and Real-time Features',
            'status': 'unknown',
            'icon': '☁️'
        },
        'environment_cards': {
            'name': 'Environment Cards',
            'description': 'Display environment information',
            'status': 'unknown',
            'icon': '📋'
        },
        'knowledge_manager': {
            'name': 'Knowledge Manager',
            'description': 'Knowledge base management',
            'status': 'unknown',
            'icon': '🧠'
        },
        'godmode_knowledge': {
            'name': 'God Mode Knowledge',
            'description': 'Permanent knowledge base for God Mode',
            'status': 'unknown',
            'icon': '⚡'
        },
        'gpu_processing': {
            'name': 'GPU Processing',
            'description': 'GPU processing (RTX 4060)',
            'status': 'unknown',
            'icon': '🎮'
        },
        'smart_allocator': {
            'name': 'Smart Resource Allocator',
            'description': 'Intelligent resource allocation',
            'status': 'unknown',
            'icon': '⚡'
        }
    }
    
    def log_if_changed(key, status, msg_ready, msg_error):
        """Log only if status changed"""
        if key not in capability_state_cache or capability_state_cache[key] != status:
            capability_state_cache[key] = status
            if status == 'ready':
                dashboard_logger.add_log('success', msg_ready)
            elif status == 'error':
                dashboard_logger.add_log('error', msg_error)
        return status
    
    # Chrome Automation
    try:
        if chrome_controller and hasattr(chrome_controller, 'is_ready'):
            if chrome_controller.is_ready():
                capabilities['chrome_automation']['status'] = log_if_changed(
                    'chrome_automation', 'ready', 
                    'Chrome Controller ready', 
                    'Chrome Controller error'
                )
            else:
                capabilities['chrome_automation']['status'] = log_if_changed(
                    'chrome_automation', 'warning', 
                    'Chrome Controller ready', 
                    'Chrome Controller preparing'
                )
        else:
            capabilities['chrome_automation']['status'] = log_if_changed(
                'chrome_automation', 'error', 
                'Chrome Controller ready', 
                'Chrome Controller not available'
            )
    except:
        capabilities['chrome_automation']['status'] = log_if_changed(
            'chrome_automation', 'error', 
            'Chrome Controller ready', 
            'Chrome Controller not available'
        )

    # AI Integration
    try:
        ai_integration = safe_import_component('ai_integration', 'system.core.controllers.ai_integration', 'MultimodalAIIntegration')
        if ai_integration:
            capabilities['ai_integration']['status'] = log_if_changed(
                'ai_integration', 'ready', 
                'AI Integration ready', 
                'AI Integration error'
            )
        else:
            capabilities['ai_integration']['status'] = log_if_changed(
                'ai_integration', 'error', 
                'AI Integration ready', 
                'AI Integration not available'
            )
    except:
        capabilities['ai_integration']['status'] = log_if_changed(
            'ai_integration', 'error', 
            'AI Integration ready', 
            'AI Integration not available'
        )
    
    # Thai Processor
    try:
        thai_processor = safe_import_component('thai_processor', 'system.core.controllers.thai_processor', 'FullThaiProcessor')
        if thai_processor:
            capabilities['thai_processor']['status'] = log_if_changed(
                'thai_processor', 'ready', 
                'Thai Processor ready', 
                'Thai Processor error'
            )
        else:
            capabilities['thai_processor']['status'] = log_if_changed(
                'thai_processor', 'error', 
                'Thai Processor ready', 
                'Thai Processor not available'
            )
    except:
        capabilities['thai_processor']['status'] = log_if_changed(
            'thai_processor', 'error', 
            'Thai Processor ready', 
            'Thai Processor not available'
        )
    
    # Visual Recognition
    try:
        visual_recognition = safe_import_component('visual_recognition', 'system.core.controllers.visual_recognition', 'VisualRecognition')
        if visual_recognition:
            capabilities['visual_recognition']['status'] = log_if_changed(
                'visual_recognition', 'ready', 
                'Visual Recognition ready', 
                'Visual Recognition error'
            )
        else:
            capabilities['visual_recognition']['status'] = log_if_changed(
                'visual_recognition', 'error', 
                'Visual Recognition ready', 
                'Visual Recognition not available'
            )
    except:
        capabilities['visual_recognition']['status'] = log_if_changed(
            'visual_recognition', 'error', 
            'Visual Recognition ready', 
            'Visual Recognition not available'
        )

    # Backup Controller
    try:
        backup_controller = safe_import_component('backup_controller', 'system.core.controllers.backup_controller', 'BackupController')
        if backup_controller:
            capabilities['backup_controller']['status'] = log_if_changed(
                'backup_controller', 'ready', 
                'Backup Controller ready', 
                'Backup Controller error'
            )
        else:
            capabilities['backup_controller']['status'] = log_if_changed(
                'backup_controller', 'error', 
                'Backup Controller ready', 
                'Backup Controller not available'
            )
    except:
        capabilities['backup_controller']['status'] = log_if_changed(
            'backup_controller', 'error', 
            'Backup Controller ready', 
            'Backup Controller not available'
        )
    
    # Supabase Integration
    try:
        supabase_integration = safe_import_component('supabase_integration', 'system.core.controllers.supabase_integration', 'SupabaseIntegration')
        if supabase_integration:
            capabilities['supabase_integration']['status'] = log_if_changed(
                'supabase_integration', 'ready', 
                'Supabase Integration ready', 
                'Supabase Integration error'
            )
        else:
            capabilities['supabase_integration']['status'] = log_if_changed(
                'supabase_integration', 'error', 
                'Supabase Integration ready', 
                'Supabase Integration not available'
            )
    except:
        capabilities['supabase_integration']['status'] = log_if_changed(
            'supabase_integration', 'error', 
            'Supabase Integration ready', 
            'Supabase Integration not available'
        )
    
    # Environment Cards
    try:
        environment_cards = safe_import_component('environment_cards', 'system.core.controllers.environment_cards', 'EnvironmentCards')
        if environment_cards:
            capabilities['environment_cards']['status'] = log_if_changed(
                'environment_cards', 'ready', 
                'Environment Cards ready', 
                'Environment Cards error'
            )
        else:
            capabilities['environment_cards']['status'] = log_if_changed(
                'environment_cards', 'error', 
                'Environment Cards ready', 
                'Environment Cards not available'
            )
    except:
        capabilities['environment_cards']['status'] = log_if_changed(
            'environment_cards', 'error', 
            'Environment Cards ready', 
            'Environment Cards not available'
        )
    
    # Knowledge Manager
    if KNOWLEDGE_MANAGER_AVAILABLE:
        capabilities['knowledge_manager']['status'] = log_if_changed(
            'knowledge_manager', 'ready', 
            'Knowledge Manager ready', 
            'Knowledge Manager error'
        )
    else:
        capabilities['knowledge_manager']['status'] = log_if_changed(
            'knowledge_manager', 'error', 
            'Knowledge Manager ready', 
            'Knowledge Manager not available'
        )

    # God Mode Knowledge
    if GODMODE_KM_AVAILABLE:
        capabilities['godmode_knowledge']['status'] = log_if_changed(
            'godmode_knowledge', 'ready', 
            'God Mode Knowledge ready', 
            'God Mode Knowledge error'
        )
    else:
        capabilities['godmode_knowledge']['status'] = log_if_changed(
            'godmode_knowledge', 'error', 
            'God Mode Knowledge ready', 
            'God Mode Knowledge not available'
        )
    
    # GPU Processing
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            capabilities['gpu_processing']['status'] = log_if_changed(
                'gpu_processing', 'ready', 
                'GPU Processing ready', 
                'GPU Processing error'
            )
        else:
            capabilities['gpu_processing']['status'] = log_if_changed(
                'gpu_processing', 'error', 
                'GPU Processing ready', 
                'GPU Processing not available'
            )
    except:
        capabilities['gpu_processing']['status'] = log_if_changed(
            'gpu_processing', 'error', 
            'GPU Processing ready', 
            'GPU Processing not available'
        )
    
    # Smart Allocator
    try:
        smart_allocator = safe_import_component('smart_allocator', 'smart_resource_allocator', 'SmartResourceAllocator')
        if smart_allocator:
            capabilities['smart_allocator']['status'] = log_if_changed(
                'smart_allocator', 'ready', 
                'Smart Allocator ready', 
                'Smart Allocator error'
            )
        else:
            capabilities['smart_allocator']['status'] = log_if_changed(
                'smart_allocator', 'error', 
                'Smart Allocator ready', 
                'Smart Allocator not available'
            )
    except:
        capabilities['smart_allocator']['status'] = log_if_changed(
            'smart_allocator', 'error', 
            'Smart Allocator ready', 
            'Smart Allocator not available'
        )
    
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
        patterns = godmode_km.get_patterns(limit=5)
        
        return {
            'available': True,
            'statistics': stats,
            'sessions': sessions,
            'commands': commands,
            'patterns': patterns
        }
    except Exception as e:
        return {
            'available': False,
            'message': f'Error getting God Mode data: {str(e)}'
        }

def get_system_resources():
    """Get system resource usage"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        
        # Disk
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_free_gb = disk.free / (1024**3)
        
        # GPU
        gpu_info = None
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Use first GPU
                gpu_info = {
                    'available': True,
                    'name': gpu.name,
                    'used_memory_mb': gpu.memoryUsed,
                    'total_memory_gb': gpu.memoryTotal / 1024
                }
        except:
            gpu_info = {'available': False}
        
        # Network
        network_status = 'Connected' if psutil.net_if_addrs() else 'Disconnected'
        
        return {
            'cpu': {'percent': cpu_percent, 'count': cpu_count},
            'memory': {'percent': memory_percent, 'available_gb': memory_available_gb},
            'disk': {'percent': disk_percent, 'free_gb': disk_free_gb},
            'gpu': gpu_info,
            'network': {'status': network_status}
        }
    except Exception as e:
        return {
            'error': f'Error getting system resources: {str(e)}'
        }

def get_project_status():
    """Get project status and statistics"""
    try:
        # Count files in different directories
        core_files = len([f for f in os.listdir('core') if f.endswith('.py')]) if os.path.exists('core') else 0
        config_files = len([f for f in os.listdir('config') if f.endswith('.json')]) if os.path.exists('config') else 0
        tool_files = len([f for f in os.listdir('tools') if f.endswith('.py')]) if os.path.exists('tools') else 0
        
        # Get total lines of code (approximate)
        total_lines = 0
        for root, dirs, files in os.walk('.'):
            if 'venv' not in root and '__pycache__' not in root:
                for file in files:
                    if file.endswith('.py'):
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                total_lines += len(f.readlines())
                        except:
                            pass
        
        return {
            'core_files': core_files,
            'config_files': config_files,
            'tool_files': tool_files,
            'total_lines': total_lines,
            'last_updated': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'error': f'Error getting project status: {str(e)}'
        }

def get_status_message(percent):
    """Get status message based on percentage"""
    if percent >= 90:
        return "Excellent - All systems operational"
    elif percent >= 75:
        return "Good - Most systems working"
    elif percent >= 50:
        return "Fair - Some systems need attention"
    elif percent >= 25:
        return "Poor - Many systems down"
    else:
        return "Critical - System failure"

def get_recommendations(capabilities):
    """Get recommendations based on system status"""
    recommendations = []
    
    ready_count = sum(1 for cap in capabilities.values() if cap['status'] == 'ready')
    total_count = len(capabilities)
    
    if ready_count == total_count:
        recommendations.append({
            'type': 'success',
            'message': 'All systems operational and ready'
        })
    elif ready_count >= total_count * 0.8:
        recommendations.append({
            'type': 'info',
            'message': 'Most systems working well'
        })
    else:
        recommendations.append({
            'type': 'warning',
            'message': 'Several systems need attention'
        })
    
    # Check specific components
    if capabilities.get('chrome_automation', {}).get('status') == 'error':
        recommendations.append({
            'type': 'error',
            'message': 'Chrome automation needs setup'
        })
    
    if capabilities.get('ai_integration', {}).get('status') == 'error':
        recommendations.append({
            'type': 'error',
            'message': 'AI integration requires configuration'
        })
    
    if capabilities.get('gpu_processing', {}).get('status') == 'error':
        recommendations.append({
            'type': 'warning',
            'message': 'GPU processing not available'
        })
    
    return recommendations

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        capabilities = get_system_capabilities()
        ready_count = sum(1 for cap in capabilities.values() if cap['status'] == 'ready')
        total_count = len(capabilities)
        status_percent = (ready_count / total_count) * 100 if total_count > 0 else 0
        
        return render_template('dashboard.html',
                             capabilities=capabilities,
                             status_percent=status_percent,
                             status_message=get_status_message(status_percent))
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/test')
def test_api():
    """Test API endpoint"""
    return jsonify({'status': 'Dashboard API is working'})

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
                'message': 'System operating normally, all components ready'
            },
            {
                'type': 'info',
                'message': 'Recommend weekly data backup'
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
        return jsonify({
            'error': f'Error getting status: {str(e)}'
        }), 500

@app.route('/api/godmode/statistics')
def api_godmode_statistics():
    """API endpoint for God Mode statistics"""
    try:
        if GODMODE_KM_AVAILABLE and godmode_km:
            stats = godmode_km.get_statistics()
            return jsonify(stats)
        else:
            return jsonify({
                'error': 'God Mode Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error getting God Mode statistics: {str(e)}'
        }), 500

@app.route('/api/godmode/sessions')
def api_godmode_sessions():
    """API endpoint for God Mode sessions"""
    try:
        if GODMODE_KM_AVAILABLE and godmode_km:
            sessions = godmode_km.get_session_history(limit=10)
            return jsonify(sessions)
        else:
            return jsonify({
                'error': 'God Mode Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error getting God Mode sessions: {str(e)}'
        }), 500

@app.route('/api/godmode/commands')
def api_godmode_commands():
    """API endpoint for God Mode commands"""
    try:
        if GODMODE_KM_AVAILABLE and godmode_km:
            commands = godmode_km.get_command_history(limit=20)
            return jsonify(commands)
        else:
            return jsonify({
                'error': 'God Mode Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error getting God Mode commands: {str(e)}'
        }), 500

@app.route('/api/godmode/patterns')
def api_godmode_patterns():
    """API endpoint for God Mode patterns"""
    try:
        if GODMODE_KM_AVAILABLE and godmode_km:
            patterns = godmode_km.get_patterns(limit=10)
            return jsonify(patterns)
        else:
            return jsonify({
                'error': 'God Mode Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error getting God Mode patterns: {str(e)}'
        }), 500

@app.route('/api/godmode/learnings')
def api_godmode_learnings():
    """API endpoint for God Mode learnings"""
    try:
        if GODMODE_KM_AVAILABLE and godmode_km:
            learnings = godmode_km.get_learnings(limit=10)
            return jsonify(learnings)
        else:
            return jsonify({
                'error': 'God Mode Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error getting God Mode learnings: {str(e)}'
        }), 500

@app.route('/api/godmode/search')
def api_godmode_search():
    """API endpoint for God Mode search"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        if GODMODE_KM_AVAILABLE and godmode_km:
            results = godmode_km.search(query)
            return jsonify(results)
        else:
            return jsonify({
                'error': 'God Mode Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error searching God Mode: {str(e)}'
        }), 500

@app.route('/api/godmode/start-session', methods=['POST'])
def api_godmode_start_session():
    """API endpoint to start God Mode session"""
    try:
        if GODMODE_KM_AVAILABLE and godmode_km:
            session_id = godmode_km.start_session()
            return jsonify({'session_id': session_id, 'status': 'started'})
        else:
            return jsonify({
                'error': 'God Mode Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error starting God Mode session: {str(e)}'
        }), 500

@app.route('/api/godmode/end-session', methods=['POST'])
def api_godmode_end_session():
    """API endpoint to end God Mode session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        if GODMODE_KM_AVAILABLE and godmode_km:
            godmode_km.end_session(session_id)
            return jsonify({'status': 'ended'})
        else:
            return jsonify({
                'error': 'God Mode Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error ending God Mode session: {str(e)}'
        }), 500

@app.route('/api/godmode/save-command', methods=['POST'])
def api_godmode_save_command():
    """API endpoint to save God Mode command"""
    try:
        data = request.get_json()
        command_text = data.get('command_text')
        command_type = data.get('command_type', 'general')
        success = data.get('success', True)
        
        if not command_text:
            return jsonify({'error': 'Command text required'}), 400
        
        if GODMODE_KM_AVAILABLE and godmode_km:
            command_id = godmode_km.save_command(command_text, command_type, success)
            return jsonify({'command_id': command_id, 'status': 'saved'})
        else:
            return jsonify({
                'error': 'God Mode Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error saving God Mode command: {str(e)}'
        }), 500

@app.route('/api/godmode/save-learning', methods=['POST'])
def api_godmode_save_learning():
    """API endpoint to save God Mode learning"""
    try:
        data = request.get_json()
        learning_text = data.get('learning_text')
        category = data.get('category', 'general')
        
        if not learning_text:
            return jsonify({'error': 'Learning text required'}), 400
        
        if GODMODE_KM_AVAILABLE and godmode_km:
            learning_id = godmode_km.save_learning(learning_text, category)
            return jsonify({'learning_id': learning_id, 'status': 'saved'})
        else:
            return jsonify({
                'error': 'God Mode Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error saving God Mode learning: {str(e)}'
        }), 500

@app.route('/api/knowledge/statistics')
def api_knowledge_statistics():
    """API endpoint for Knowledge Manager statistics"""
    try:
        if KNOWLEDGE_MANAGER_AVAILABLE and knowledge_manager:
            stats = knowledge_manager.get_statistics()
            return jsonify(stats)
        else:
            return jsonify({
                'error': 'Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error getting Knowledge Manager statistics: {str(e)}'
        }), 500

@app.route('/api/knowledge/search')
def api_knowledge_search():
    """API endpoint for Knowledge Manager search"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        if KNOWLEDGE_MANAGER_AVAILABLE and knowledge_manager:
            results = knowledge_manager.search(query)
            return jsonify(results)
        else:
            return jsonify({
                'error': 'Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error searching Knowledge Manager: {str(e)}'
        }), 500

@app.route('/api/knowledge/categories')
def api_knowledge_categories():
    """API endpoint for Knowledge Manager categories"""
    try:
        if KNOWLEDGE_MANAGER_AVAILABLE and knowledge_manager:
            categories = knowledge_manager.get_categories()
            return jsonify(categories)
        else:
            return jsonify({
                'error': 'Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error getting Knowledge Manager categories: {str(e)}'
        }), 500

@app.route('/api/knowledge/category/<category>')
def api_knowledge_by_category(category):
    """API endpoint for Knowledge Manager by category"""
    try:
        if KNOWLEDGE_MANAGER_AVAILABLE and knowledge_manager:
            items = knowledge_manager.get_by_category(category)
            return jsonify(items)
        else:
            return jsonify({
                'error': 'Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error getting Knowledge Manager category: {str(e)}'
        }), 500

@app.route('/api/knowledge/add', methods=['POST'])
def api_knowledge_add():
    """API endpoint to add Knowledge Manager item"""
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        category = data.get('category', 'general')
        
        if not title or not content:
            return jsonify({'error': 'Title and content required'}), 400
        
        if KNOWLEDGE_MANAGER_AVAILABLE and knowledge_manager:
            item_id = knowledge_manager.add_item(title, content, category)
            return jsonify({'item_id': item_id, 'status': 'added'})
        else:
            return jsonify({
                'error': 'Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error adding Knowledge Manager item: {str(e)}'
        }), 500

@app.route('/api/knowledge/update/<knowledge_id>', methods=['PUT'])
def api_knowledge_update(knowledge_id):
    """API endpoint to update Knowledge Manager item"""
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        
        if not title and not content and not category:
            return jsonify({'error': 'At least one field required'}), 400
        
        if KNOWLEDGE_MANAGER_AVAILABLE and knowledge_manager:
            knowledge_manager.update_item(knowledge_id, title, content, category)
            return jsonify({'status': 'updated'})
        else:
            return jsonify({
                'error': 'Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error updating Knowledge Manager item: {str(e)}'
        }), 500

@app.route('/api/knowledge/delete/<knowledge_id>', methods=['DELETE'])
def api_knowledge_delete(knowledge_id):
    """API endpoint to delete Knowledge Manager item"""
    try:
        if KNOWLEDGE_MANAGER_AVAILABLE and knowledge_manager:
            knowledge_manager.delete_item(knowledge_id)
            return jsonify({'status': 'deleted'})
        else:
            return jsonify({
                'error': 'Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error deleting Knowledge Manager item: {str(e)}'
        }), 500

@app.route('/api/knowledge/<knowledge_id>')
def api_knowledge_get(knowledge_id):
    """API endpoint to get Knowledge Manager item"""
    try:
        if KNOWLEDGE_MANAGER_AVAILABLE and knowledge_manager:
            item = knowledge_manager.get_item(knowledge_id)
            if item:
                return jsonify(item)
            else:
                return jsonify({'error': 'Item not found'}), 404
        else:
            return jsonify({
                'error': 'Knowledge Manager not available'
            }), 404
    except Exception as e:
        return jsonify({
            'error': f'Error getting Knowledge Manager item: {str(e)}'
        }), 500

@app.route('/api/system/cleanup-chrome', methods=['POST'])
def api_cleanup_chrome():
    """API endpoint to cleanup Chrome processes"""
    try:
        if chrome_controller:
            chrome_controller.cleanup()
            return jsonify({'status': 'Chrome cleanup completed'})
        else:
            return jsonify({'error': 'Chrome Controller not available'}), 404
    except Exception as e:
        return jsonify({'error': f'Error cleaning up Chrome: {str(e)}'}), 500

@app.route('/api/system/restart-dashboard', methods=['POST'])
def api_restart_dashboard():
    """API endpoint to restart dashboard"""
    try:
        # This would typically restart the application
        return jsonify({'status': 'Dashboard restart initiated'})
    except Exception as e:
        return jsonify({'error': f'Error restarting dashboard: {str(e)}'}), 500

@app.route('/api/logs')
def api_logs():
    """API endpoint for dashboard logs"""
    try:
        return jsonify(dashboard_logger.logs)
    except Exception as e:
        return jsonify({'error': f'Error getting logs: {str(e)}'}), 500

# Real-time Monitor Routes
@app.route('/real-time-monitor')
def real_time_monitor():
    """Real-time monitoring dashboard"""
    return render_template('real-time-monitor.html')

@app.route('/api/logging/health')
def logging_health():
    """Check logging system health"""
    if not LOGGING_AVAILABLE:
        return jsonify({
            "status": "unavailable",
            "message": "Logging system not available"
        }), 503
    
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "logger_manager": "active",
                "workflow_monitor": "active", 
                "performance_tracker": "active",
                "alert_system": "active"
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/logging/logs/recent')
def get_recent_logs():
    """Get recent logs from logging system"""
    if not LOGGING_AVAILABLE:
        return jsonify({"logs": [], "total": 0, "timestamp": datetime.now().isoformat()})
    
    try:
        limit = request.args.get('limit', 100, type=int)
        module = request.args.get('module')
        level = request.args.get('level')
        
        logger_manager = get_logger_manager()
        logs = logger_manager.get_recent_logs(limit=limit, module=module, level=level)
        
        return jsonify({
            "logs": logs,
            "total": len(logs),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "logs": [],
            "total": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/logging/workflows/active')
def get_active_workflows():
    """Get active workflows"""
    if not LOGGING_AVAILABLE:
        return jsonify({"workflows": [], "total": 0, "timestamp": datetime.now().isoformat()})
    
    try:
        workflow_monitor = get_workflow_monitor()
        workflows = workflow_monitor.get_active_workflows()
        
        return jsonify({
            "workflows": workflows,
            "total": len(workflows),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "workflows": [],
            "total": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/logging/performance/summary')
def get_performance_summary():
    """Get performance summary"""
    if not LOGGING_AVAILABLE:
        return jsonify({"summary": {}, "timestamp": datetime.now().isoformat()})
    
    try:
        performance_tracker = get_performance_tracker()
        summary = performance_tracker.get_performance_summary()
        
        return jsonify({
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "summary": {},
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/logging/alerts/active')
def get_active_alerts():
    """Get active alerts"""
    if not LOGGING_AVAILABLE:
        return jsonify({"alerts": [], "total": 0, "timestamp": datetime.now().isoformat()})
    
    try:
        alert_system = get_alert_system()
        alerts = alert_system.get_active_alerts()
        
        return jsonify({
            "alerts": alerts,
            "total": len(alerts),
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "alerts": [],
            "total": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/logging/reset/status')
def get_reset_status():
    """Get log reset status"""
    if not LOGGING_AVAILABLE:
        return jsonify({"reset_status": {}, "timestamp": datetime.now().isoformat()})
    
    try:
        logger_manager = get_logger_manager()
        status = logger_manager.get_reset_status()
        
        return jsonify({
            "reset_status": status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "reset_status": {},
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/logging/reset/cleanup', methods=['POST'])
def cleanup_logs():
    """Clean up old logs"""
    if not LOGGING_AVAILABLE:
        return jsonify({"status": "unavailable", "message": "Logging system not available"}), 503
    
    try:
        logger_manager = get_logger_manager()
        logger_manager.cleanup_old_logs()
        
        return jsonify({
            "status": "cleanup_completed",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/system/resources')
def api_system_resources():
    """API endpoint for system resources"""
    try:
        resources = get_system_resources()
        return jsonify(resources)
    except Exception as e:
        return jsonify({'error': f'Error getting system resources: {str(e)}'}), 500

@app.route('/api/system/status')
def api_system_status():
    """API endpoint for system status"""
    try:
        capabilities = get_system_capabilities()
        ready_count = sum(1 for cap in capabilities.values() if cap['status'] == 'ready')
        total_count = len(capabilities)
        status_percent = (ready_count / total_count) * 100 if total_count > 0 else 0
        
        return jsonify({
            'capabilities': capabilities,
            'status_percent': status_percent,
            'status_message': get_status_message(status_percent),
            'recommendations': get_recommendations(capabilities),
            'last_update': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Error getting system status: {str(e)}'}), 500

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('status', {'message': 'Connected to GOD MODE Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

def background_updates():
    """Background task for real-time updates"""
    while True:
        try:
            # Get current status
            capabilities = get_system_capabilities()
            ready_count = sum(1 for cap in capabilities.values() if cap['status'] == 'ready')
            total_count = len(capabilities)
            status_percent = (ready_count / total_count) * 100 if total_count > 0 else 0
            
            # Emit status update
            socketio.emit('status_update', {
                'capabilities': capabilities,
                'status_percent': status_percent,
                'status_message': get_status_message(status_percent),
                'timestamp': datetime.now().isoformat()
            })
            
            # Wait before next update
            time.sleep(5)
        except Exception as e:
            print(f"Error in background updates: {e}")
            time.sleep(10)

# Direct Control API endpoints
@app.route('/api/direct-control/activate', methods=['POST'])
def activate_direct_control():
    """API endpoint to activate Direct Control"""
    try:
        from system.core.controllers.direct_control import direct_control
        direct_control.activate_system()
        return jsonify({'status': 'Direct Control activated'})
    except Exception as e:
        return jsonify({'error': f'Error activating Direct Control: {str(e)}'}), 500

@app.route('/api/direct-control/deactivate', methods=['POST'])
def deactivate_direct_control():
    """API endpoint to deactivate Direct Control"""
    try:
        from system.core.controllers.direct_control import direct_control
        direct_control.deactivate_system()
        return jsonify({'status': 'Direct Control deactivated'})
    except Exception as e:
        return jsonify({'error': f'Error deactivating Direct Control: {str(e)}'}), 500

@app.route('/api/direct-control/status', methods=['GET'])
def get_direct_control_status():
    """API endpoint to get Direct Control status"""
    try:
        from system.core.controllers.direct_control import direct_control
        return jsonify({
            'active': direct_control.is_active,
            'mouse_position': direct_control.get_mouse_position(),
            'screen_size': direct_control.get_screen_size(),
            'action_count': direct_control.get_action_count(),
            'last_action': direct_control.get_last_action()
        })
    except Exception as e:
        return jsonify({'error': f'Error getting Direct Control status: {str(e)}'}), 500

@app.route('/api/direct-control/history', methods=['GET'])
def get_direct_control_history():
    """API endpoint to get Direct Control history"""
    try:
        from system.core.controllers.direct_control import direct_control
        history = direct_control.get_history()
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': f'Error getting Direct Control history: {str(e)}'}), 500

@app.route('/api/direct-control/command', methods=['POST'])
def execute_direct_command():
    """API endpoint to execute Direct Control command"""
    try:
        from system.core.controllers.smart_command_processor import smart_processor
        data = request.get_json()
        command = data.get('command')
        result = smart_processor.process_command(command)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': f'Error executing command: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting GOD MODE Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    
    # Start background updates thread
    update_thread = threading.Thread(target=background_updates, daemon=True)
    update_thread.start()
    
    # Start the application
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 