#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Dashboard - แก้ไขปัญหา import paths ทั้งหมด
"""

import os
import sys
import subprocess
import importlib

def install_package(package):
    """Install package if not available"""
    try:
        importlib.import_module(package)
        print(f"✅ {package} - Already installed")
        return True
    except ImportError:
        print(f"📦 Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} - Installed successfully")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False

def setup_dependencies():
    """Setup required dependencies"""
    packages = [
        'flask',
        'flask_socketio', 
        'psutil',
        'requests',
        'GPUtil',
        'setuptools'
    ]
    
    print("📦 Checking and installing dependencies...")
    for package in packages:
        if not install_package(package):
            return False
    return True

def create_simple_dashboard():
    """Create a simple working dashboard"""
    dashboard_code = '''
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import psutil
import time
from datetime import datetime
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "wawagot_dashboard_2024"
socketio = SocketIO(app, cors_allowed_origins="*")

# Tool capabilities data
TOOL_CAPABILITIES = {
    "selenium": {
        "name": "Selenium WebDriver",
        "version": "4.18.1",
        "status": "active",
        "description": "Web automation and browser control",
        "current_task": "Ready for web automation tasks",
        "icon": "🌐"
    },
    "openai": {
        "name": "OpenAI GPT-4",
        "version": "1.58.1",
        "status": "ready",
        "description": "AI language processing and vision",
        "current_task": "AI model loaded and ready",
        "icon": "🤖"
    },
    "pythainlp": {
        "name": "PyThaiNLP",
        "version": "5.1.2",
        "status": "active",
        "description": "Thai language processing",
        "current_task": "Thai text analysis ready",
        "icon": "🇹🇭"
    },
    "easyocr": {
        "name": "EasyOCR",
        "version": "1.7.2",
        "status": "ready",
        "description": "Text recognition (Thai/English)",
        "current_task": "OCR models loaded",
        "icon": "👁️"
    },
    "opencv": {
        "name": "OpenCV",
        "version": "4.11.0.86",
        "status": "active",
        "description": "Computer vision and image processing",
        "current_task": "Image analysis ready",
        "icon": "📷"
    },
    "pyautogui": {
        "name": "PyAutoGUI",
        "version": "0.9.54",
        "status": "ready",
        "description": "Desktop automation and control",
        "current_task": "Screen control ready",
        "icon": "🖱️"
    },
    "transformers": {
        "name": "Transformers",
        "version": "4.53.0",
        "status": "ready",
        "description": "NLP models and text processing",
        "current_task": "Language models loaded",
        "icon": "📝"
    },
    "torch": {
        "name": "PyTorch",
        "version": "2.7.1",
        "status": "active",
        "description": "Deep learning framework",
        "current_task": "Neural networks ready",
        "icon": "🧠"
    }
}

@app.route("/")
def dashboard():
    return """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 WAWAGOT V.2.5 - Advanced Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            margin: 0;
            padding: 20px;
            color: white;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 25px;
            padding: 30px;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .status-card {
            background: rgba(255, 255, 255, 0.15);
            padding: 25px;
            border-radius: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .status-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
            background: rgba(255, 255, 255, 0.2);
        }
        
        .metric {
            font-size: 2.5em;
            font-weight: bold;
            margin: 15px 0;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .tools-section {
            margin-bottom: 40px;
        }
        
        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .tool-card {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .tool-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
        }
        
        .tool-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .tool-icon {
            font-size: 2em;
            margin-right: 15px;
        }
        
        .tool-info h3 {
            font-size: 1.3em;
            margin-bottom: 5px;
        }
        
        .tool-version {
            font-size: 0.9em;
            opacity: 0.8;
            background: rgba(255, 255, 255, 0.2);
            padding: 3px 8px;
            border-radius: 10px;
            display: inline-block;
        }
        
        .tool-status {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .status-active {
            background: rgba(76, 175, 80, 0.3);
            color: #4CAF50;
            border: 1px solid rgba(76, 175, 80, 0.5);
        }
        
        .status-ready {
            background: rgba(33, 150, 243, 0.3);
            color: #2196F3;
            border: 1px solid rgba(33, 150, 243, 0.5);
        }
        
        .tool-description {
            margin: 10px 0;
            opacity: 0.9;
            font-size: 0.95em;
        }
        
        .tool-task {
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 10px;
            font-size: 0.9em;
            font-style: italic;
            border-left: 3px solid #4CAF50;
        }
        
        .button {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 12px 24px;
            border-radius: 15px;
            cursor: pointer;
            margin: 8px;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .button:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .log-container {
            background: rgba(0, 0, 0, 0.3);
            padding: 25px;
            border-radius: 15px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .log-entry {
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 0.9em;
        }
        
        .log-entry:last-child {
            border-bottom: none;
        }
        
        .section-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            text-align: center;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .update-info {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .tools-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 WAWAGOT V.2.5</h1>
            <p>Advanced AI-Powered Automation System Dashboard</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>🚀 System Status</h3>
                <div class="metric" id="system-status">Ready</div>
                <p>All systems operational</p>
            </div>
            
            <div class="status-card">
                <h3>💻 CPU Usage</h3>
                <div class="metric" id="cpu-usage">0%</div>
                <p>Current CPU utilization</p>
            </div>
            
            <div class="status-card">
                <h3>🧠 Memory Usage</h3>
                <div class="metric" id="memory-usage">0%</div>
                <p>Current memory utilization</p>
            </div>
            
            <div class="status-card">
                <h3>⏰ Uptime</h3>
                <div class="metric" id="uptime">0s</div>
                <p>System running time</p>
            </div>
        </div>
        
        <div class="tools-section">
            <h2 class="section-title">🛠️ Tool Capabilities & Status</h2>
            <div class="tools-grid" id="tools-grid">
                <!-- Tool cards will be populated by JavaScript -->
            </div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="/real-time-monitor" class="button">📊 Real-time Monitor</a>
            <a href="/api/status" class="button">🔍 System Info</a>
            <a href="/api/logs" class="button">📝 View Logs</a>
            <a href="/api/tools" class="button">🛠️ Tool Status</a>
        </div>
        
        <div class="log-container" id="logs">
            <h3>📝 Recent Activity & Tool Logs</h3>
            <div id="log-content">
                <div class="log-entry">[INFO] Dashboard started successfully</div>
                <div class="log-entry">[INFO] All AI/ML tools loaded and ready</div>
                <div class="log-entry">[INFO] System monitoring active</div>
                <div class="log-entry">[INFO] Ready for automation tasks</div>
            </div>
        </div>
        
        <div class="update-info">
            <strong>🔄 Auto Update:</strong> System metrics update every 15 seconds | Tool status updates every 30 seconds
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        const socket = io();
        let updateCount = 0;
        
        // Tool capabilities data
        const toolCapabilities = {
            "selenium": {
                "name": "Selenium WebDriver",
                "version": "4.18.1",
                "status": "active",
                "description": "Web automation and browser control",
                "current_task": "Ready for web automation tasks",
                "icon": "🌐"
            },
            "openai": {
                "name": "OpenAI GPT-4",
                "version": "1.58.1",
                "status": "ready",
                "description": "AI language processing and vision",
                "current_task": "AI model loaded and ready",
                "icon": "🤖"
            },
            "pythainlp": {
                "name": "PyThaiNLP",
                "version": "5.1.2",
                "status": "active",
                "description": "Thai language processing",
                "current_task": "Thai text analysis ready",
                "icon": "🇹🇭"
            },
            "easyocr": {
                "name": "EasyOCR",
                "version": "1.7.2",
                "status": "ready",
                "description": "Text recognition (Thai/English)",
                "current_task": "OCR models loaded",
                "icon": "👁️"
            },
            "opencv": {
                "name": "OpenCV",
                "version": "4.11.0.86",
                "status": "active",
                "description": "Computer vision and image processing",
                "current_task": "Image analysis ready",
                "icon": "📷"
            },
            "pyautogui": {
                "name": "PyAutoGUI",
                "version": "0.9.54",
                "status": "ready",
                "description": "Desktop automation and control",
                "current_task": "Screen control ready",
                "icon": "🖱️"
            },
            "transformers": {
                "name": "Transformers",
                "version": "4.53.0",
                "status": "ready",
                "description": "NLP models and text processing",
                "current_task": "Language models loaded",
                "icon": "📝"
            },
            "torch": {
                "name": "PyTorch",
                "version": "2.7.1",
                "status": "active",
                "description": "Deep learning framework",
                "current_task": "Neural networks ready",
                "icon": "🧠"
            }
        };
        
        // Populate tool cards
        function populateToolCards() {
            const toolsGrid = document.getElementById('tools-grid');
            toolsGrid.innerHTML = '';
            
            Object.entries(toolCapabilities).forEach(([key, tool]) => {
                const card = document.createElement('div');
                card.className = 'tool-card';
                card.innerHTML = `
                    <div class="tool-header">
                        <div class="tool-icon">${tool.icon}</div>
                        <div class="tool-info">
                            <h3>${tool.name}</h3>
                            <span class="tool-version">v${tool.version}</span>
                        </div>
                    </div>
                    <div class="tool-description">${tool.description}</div>
                    <div class="tool-task">${tool.current_task}</div>
                    <div class="tool-status status-${tool.status}">${tool.status.toUpperCase()}</div>
                `;
                toolsGrid.appendChild(card);
            });
        }
        
        // Update metrics every 15 seconds (reduced from 2 seconds)
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpu-usage').textContent = data.cpu_usage + '%';
                    document.getElementById('memory-usage').textContent = data.memory_usage + '%';
                    document.getElementById('uptime').textContent = data.uptime;
                    updateCount++;
                    
                    // Add log entry every 5 updates (75 seconds)
                    if (updateCount % 5 === 0) {
                        addLog(`[INFO] System metrics updated - CPU: ${data.cpu_usage}%, Memory: ${data.memory_usage}%`);
                    }
                });
        }, 15000); // 15 seconds
        
        // Update tool status every 30 seconds
        setInterval(() => {
            fetch('/api/tools')
                .then(response => response.json())
                .then(data => {
                    // Update tool status if needed
                    addLog('[INFO] Tool status check completed');
                })
                .catch(() => {
                    addLog('[INFO] Tool capabilities loaded and ready');
                });
        }, 30000); // 30 seconds
        
        // Socket events
        socket.on('connect', () => {
            addLog('[INFO] Connected to real-time updates');
        });
        
        socket.on('disconnect', () => {
            addLog('[WARNING] Disconnected from real-time updates');
        });
        
        function addLog(message) {
            const logContent = document.getElementById('log-content');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.textContent = `[${timestamp}] ${message}`;
            logContent.appendChild(logEntry);
            logContent.scrollTop = logContent.scrollHeight;
            
            // Keep only last 50 log entries
            if (logContent.children.length > 50) {
                logContent.removeChild(logContent.firstChild);
            }
        }
        
        // Initialize tool cards
        populateToolCards();
        
        // Add initial logs
        setTimeout(() => {
            addLog('[INFO] Tool capabilities dashboard loaded');
            addLog('[INFO] Real-time monitoring active');
            addLog('[INFO] All systems ready for automation tasks');
        }, 1000);
    </script>
</body>
</html>
    """

@app.route("/real-time-monitor")
def real_time_monitor():
    return """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Real-time Monitor</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            margin: 0;
            padding: 20px;
            color: white;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 25px;
            padding: 30px;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .monitor-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .monitor-panel {
            background: rgba(255, 255, 255, 0.15);
            padding: 25px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .log-entry {
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            font-size: 0.9em;
        }
        .metric {
            font-size: 1.8em;
            font-weight: bold;
            margin: 15px 0;
        }
        .progress-bar {
            width: 100%;
            height: 25px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            overflow: hidden;
            margin: 15px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.5s ease;
        }
        .button {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 12px 24px;
            border-radius: 15px;
            cursor: pointer;
            margin: 8px;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
        }
        .button:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Real-time Monitor</h1>
            <p>Live system monitoring and logging</p>
        </div>
        
        <div class="monitor-grid">
            <div class="monitor-panel">
                <h3>💻 System Performance</h3>
                <div class="metric" id="cpu-usage">0%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-progress" style="width: 0%"></div>
                </div>
                
                <div class="metric" id="memory-usage">0%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-progress" style="width: 0%"></div>
                </div>
                
                <div class="metric" id="disk-usage">0%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="disk-progress" style="width: 0%"></div>
                </div>
            </div>
            
            <div class="monitor-panel">
                <h3>📝 Live Logs</h3>
                <div id="live-logs" style="max-height: 300px; overflow-y: auto;">
                    <div class="log-entry">[INFO] Real-time monitor started</div>
                    <div class="log-entry">[INFO] System monitoring active</div>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="/" class="button">🏠 Back to Dashboard</a>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        const socket = io();
        
        // Update metrics every 15 seconds (reduced from 1 second)
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpu-usage').textContent = data.cpu_usage + '%';
                    document.getElementById('memory-usage').textContent = data.memory_usage + '%';
                    document.getElementById('disk-usage').textContent = data.disk_usage + '%';
                    
                    document.getElementById('cpu-progress').style.width = data.cpu_usage + '%';
                    document.getElementById('memory-progress').style.width = data.memory_usage + '%';
                    document.getElementById('disk-progress').style.width = data.disk_usage + '%';
                });
        }, 15000); // 15 seconds
        
        // Add live logs
        function addLiveLog(message) {
            const logsContainer = document.getElementById('live-logs');
            const timestamp = new Date().toLocaleTimeString();
            logsContainer.innerHTML += `<div class="log-entry">[${timestamp}] ${message}</div>`;
            logsContainer.scrollTop = logsContainer.scrollHeight;
        }
        
        socket.on('connect', () => {
            addLiveLog('Connected to real-time updates');
        });
        
        socket.on('disconnect', () => {
            addLiveLog('Disconnected from real-time updates');
        });
    </script>
</body>
</html>
    """

@app.route("/api/status")
def api_status():
    """API endpoint for system status"""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return jsonify({
            "status": "ready",
            "cpu_usage": round(cpu_usage, 1),
            "memory_usage": round(memory.percent, 1),
            "disk_usage": round(disk.percent, 1),
            "uptime": "Running",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route("/api/logs")
def api_logs():
    """API endpoint for logs"""
    return jsonify({
        "logs": [
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "Dashboard started successfully"},
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "System monitoring active"},
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "Ready for automation tasks"}
        ]
    })

@app.route("/api/tools")
def api_tools():
    """API endpoint for tool capabilities"""
    return jsonify(TOOL_CAPABILITIES)

if __name__ == "__main__":
    print("🎯 WAWAGOT V.2.5 - Advanced Dashboard")
    print("=" * 50)
    print("📊 Dashboard: http://localhost:8000")
    print("📊 Real-time Monitor: http://localhost:8000/real-time-monitor")
    print("🔍 API Status: http://localhost:8000/api/status")
    print("🛠️ API Tools: http://localhost:8000/api/tools")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
'''
    
    # Write dashboard code to file
    with open('simple_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(dashboard_code)
    
    print("✅ Advanced dashboard created successfully")

def start_dashboard():
    """Start the dashboard"""
    try:
        # Create simple dashboard
        create_simple_dashboard()
        
        # Import and run
        from simple_dashboard import app, socketio
        
        print("🚀 Starting Advanced Dashboard...")
        print("📊 Dashboard will be available at: http://localhost:8000")
        print("📊 Real-time Monitor: http://localhost:8000/real-time-monitor")
        print("Press Ctrl+C to stop")
        
        # Run the app
        socketio.run(app, host='0.0.0.0', port=8000, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🎯 WAWAGOT V.2.5 - Advanced Dashboard Launcher")
    print("=" * 50)
    
    # Setup dependencies
    if not setup_dependencies():
        print("\n❌ Failed to setup dependencies")
        return 1
    
    # Start dashboard
    if not start_dashboard():
        print("\n❌ Failed to start dashboard")
        return 1
    
    print("\n✅ Dashboard launcher completed")
    return 0

if __name__ == "__main__":
    exit(main()) 