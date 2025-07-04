#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Execution System for Google Services - WAWAGOT V.2
ระบบ Direct Execution สำหรับใช้งาน Google Services โดยตรง
"""

import os
import json
import requests
import logging
import subprocess
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request, redirect
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class DirectExecutionSystem:
    def __init__(self):
        self.credentials = None
        self.api_key = "AIzaSyDXoRsK0eZK2nMuVzSLsRItBiH7OEfZ0y0"
        self.execution_history = []
        self.active_tasks = {}
        
    def load_credentials(self):
        """โหลด credentials"""
        try:
            if os.path.exists("google_credentials_complete.json"):
                with open("google_credentials_complete.json", "r") as f:
                    creds_data = json.load(f)
                
                self.credentials = Credentials(
                    token=creds_data.get("access_token"),
                    refresh_token=creds_data.get("refresh_token"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=creds_data.get("client_id"),
                    client_secret=creds_data.get("client_secret"),
                    scopes=creds_data.get("scopes", [])
                )
                
                if self.credentials and self.credentials.expired:
                    self.credentials.refresh(Request())
                
                return True
            return False
        except Exception as e:
            logger.error(f"❌ ไม่สามารถโหลด credentials ได้: {e}")
            return False
    
    def execute_gemini_command(self, prompt, task_id):
        """Execute Gemini AI Command"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            
            result = {
                "task_id": task_id,
                "service": "gemini_ai",
                "status": "success",
                "result": response.text,
                "timestamp": datetime.now().isoformat()
            }
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            result = {
                "task_id": task_id,
                "service": "gemini_ai",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(result)
            return result
    
    def execute_drive_command(self, command, task_id):
        """Execute Google Drive Command"""
        try:
            if not self.credentials:
                raise Exception("ไม่มี credentials")
            
            service = build("drive", "v3", credentials=self.credentials)
            
            if command == "list_files":
                results = service.files().list(pageSize=20).execute()
                files = results.get("files", [])
                result = {
                    "task_id": task_id,
                    "service": "google_drive",
                    "status": "success",
                    "result": files,
                    "timestamp": datetime.now().isoformat()
                }
            elif command == "get_storage":
                about = service.about().get(fields="storageQuota").execute()
                result = {
                    "task_id": task_id,
                    "service": "google_drive",
                    "status": "success",
                    "result": about,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception(f"คำสั่งไม่รู้จัก: {command}")
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            result = {
                "task_id": task_id,
                "service": "google_drive",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(result)
            return result
    
    def execute_calendar_command(self, command, task_id):
        """Execute Google Calendar Command"""
        try:
            if not self.credentials:
                raise Exception("ไม่มี credentials")
            
            service = build("calendar", "v3", credentials=self.credentials)
            
            if command == "list_events":
                now = datetime.utcnow().isoformat() + "Z"
                events_result = service.events().list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime"
                ).execute()
                
                events = events_result.get("items", [])
                result = {
                    "task_id": task_id,
                    "service": "google_calendar",
                    "status": "success",
                    "result": events,
                    "timestamp": datetime.now().isoformat()
                }
            elif command == "list_calendars":
                calendars = service.calendarList().list().execute()
                result = {
                    "task_id": task_id,
                    "service": "google_calendar",
                    "status": "success",
                    "result": calendars,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception(f"คำสั่งไม่รู้จัก: {command}")
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            result = {
                "task_id": task_id,
                "service": "google_calendar",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(result)
            return result
    
    def execute_gmail_command(self, command, task_id):
        """Execute Gmail Command"""
        try:
            if not self.credentials:
                raise Exception("ไม่มี credentials")
            
            service = build("gmail", "v1", credentials=self.credentials)
            
            if command == "list_messages":
                results = service.users().messages().list(userId="me", maxResults=10).execute()
                messages = results.get("messages", [])
                result = {
                    "task_id": task_id,
                    "service": "gmail",
                    "status": "success",
                    "result": messages,
                    "timestamp": datetime.now().isoformat()
                }
            elif command == "get_profile":
                profile = service.users().getProfile(userId="me").execute()
                result = {
                    "task_id": task_id,
                    "service": "gmail",
                    "status": "success",
                    "result": profile,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception(f"คำสั่งไม่รู้จัก: {command}")
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            result = {
                "task_id": task_id,
                "service": "gmail",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(result)
            return result
    
    def execute_youtube_command(self, command, task_id):
        """Execute YouTube Command"""
        try:
            youtube = build("youtube", "v3", developerKey=self.api_key)
            
            if command == "trending_videos":
                request = youtube.videos().list(
                    part="snippet,statistics",
                    chart="mostPopular",
                    regionCode="TH",
                    maxResults=10
                )
                response = request.execute()
                
                videos = response.get("items", [])
                result = {
                    "task_id": task_id,
                    "service": "youtube",
                    "status": "success",
                    "result": videos,
                    "timestamp": datetime.now().isoformat()
                }
            elif command == "search_videos":
                # ใช้คำค้นหาเริ่มต้น
                request = youtube.search().list(
                    part="snippet",
                    q="WAWAGOT AI",
                    type="video",
                    maxResults=5
                )
                response = request.execute()
                
                videos = response.get("items", [])
                result = {
                    "task_id": task_id,
                    "service": "youtube",
                    "status": "success",
                    "result": videos,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception(f"คำสั่งไม่รู้จัก: {command}")
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            result = {
                "task_id": task_id,
                "service": "youtube",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(result)
            return result
    
    def execute_system_command(self, command, task_id):
        """Execute System Command"""
        try:
            # ตรวจสอบคำสั่งที่ปลอดภัย
            safe_commands = [
                "system_info", "disk_usage", "memory_usage", 
                "network_status", "process_list"
            ]
            
            if command not in safe_commands:
                raise Exception(f"คำสั่งไม่ปลอดภัย: {command}")
            
            if command == "system_info":
                import platform
                info = {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor()
                }
                result = {
                    "task_id": task_id,
                    "service": "system",
                    "status": "success",
                    "result": info,
                    "timestamp": datetime.now().isoformat()
                }
            elif command == "disk_usage":
                import shutil
                total, used, free = shutil.disk_usage("/")
                info = {
                    "total": total // (2**30),  # GB
                    "used": used // (2**30),    # GB
                    "free": free // (2**30)     # GB
                }
                result = {
                    "task_id": task_id,
                    "service": "system",
                    "status": "success",
                    "result": info,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception(f"คำสั่งไม่รู้จัก: {command}")
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            result = {
                "task_id": task_id,
                "service": "system",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(result)
            return result
    
    def execute_command(self, service, command, prompt=None):
        """Execute Command โดยรวม"""
        task_id = f"task_{int(time.time())}"
        
        # เพิ่ม task ลงใน active tasks
        self.active_tasks[task_id] = {
            "service": service,
            "command": command,
            "status": "running",
            "start_time": datetime.now().isoformat()
        }
        
        try:
            if service == "gemini_ai":
                result = self.execute_gemini_command(prompt or "สวัสดีครับ", task_id)
            elif service == "google_drive":
                result = self.execute_drive_command(command, task_id)
            elif service == "google_calendar":
                result = self.execute_calendar_command(command, task_id)
            elif service == "gmail":
                result = self.execute_gmail_command(command, task_id)
            elif service == "youtube":
                result = self.execute_youtube_command(command, task_id)
            elif service == "system":
                result = self.execute_system_command(command, task_id)
            else:
                raise Exception(f"Service ไม่รู้จัก: {service}")
            
            # อัปเดต task status
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["end_time"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            # อัปเดต task status
            self.active_tasks[task_id]["status"] = "failed"
            self.active_tasks[task_id]["end_time"] = datetime.now().isoformat()
            self.active_tasks[task_id]["error"] = str(e)
            
            result = {
                "task_id": task_id,
                "service": service,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.execution_history.append(result)
            return result

# สร้าง instance ของ Direct Execution System
direct_system = DirectExecutionSystem()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Direct Execution System - WAWAGOT</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .execution-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .command-panel {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border: 2px solid #e9ecef;
        }
        
        .command-panel h3 {
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        
        .command-panel .icon {
            margin-right: 10px;
            font-size: 1.2em;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        
        .form-group select,
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .form-group textarea {
            height: 100px;
            resize: vertical;
        }
        
        .btn {
            background: #ff6b6b;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px 5px;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: #ee5a24;
            transform: translateY(-2px);
        }
        
        .btn-success {
            background: #28a745;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .results-panel {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border: 2px solid #e9ecef;
            max-height: 600px;
            overflow-y: auto;
        }
        
        .result-item {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #4285f4;
        }
        
        .result-item.success {
            border-left-color: #28a745;
        }
        
        .result-item.error {
            border-left-color: #dc3545;
        }
        
        .result-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .result-service {
            font-weight: bold;
            color: #333;
        }
        
        .result-status {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .result-status.success {
            background: #d4edda;
            color: #155724;
        }
        
        .result-status.error {
            background: #f8d7da;
            color: #721c24;
        }
        
        .result-timestamp {
            font-size: 12px;
            color: #666;
        }
        
        .result-content {
            background: #f8f9fa;
            border-radius: 5px;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        
        .quick-commands {
            background: #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .quick-commands h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .quick-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        
        .quick-btn {
            background: #6c757d;
            color: white;
            padding: 8px 15px;
            border: none;
            border-radius: 15px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .quick-btn:hover {
            background: #5a6268;
            transform: translateY(-1px);
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #ff6b6b;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ Direct Execution System</h1>
            <p>ระบบ Direct Execution สำหรับ Google Services - WAWAGOT V.2</p>
        </div>
        
        <div class="content">
            <div class="quick-commands">
                <h3>🚀 Quick Commands</h3>
                <div class="quick-buttons">
                    <button class="quick-btn" onclick="executeQuick('gemini_ai', 'hello', 'สวัสดีครับ ฉันคือ WAWAGOT AI Assistant')">🤖 Gemini AI</button>
                    <button class="quick-btn" onclick="executeQuick('google_drive', 'list_files')">📁 Drive Files</button>
                    <button class="quick-btn" onclick="executeQuick('google_calendar', 'list_events')">📅 Calendar Events</button>
                    <button class="quick-btn" onclick="executeQuick('gmail', 'list_messages')">📧 Gmail Messages</button>
                    <button class="quick-btn" onclick="executeQuick('youtube', 'trending_videos')">🎥 YouTube Trending</button>
                    <button class="quick-btn" onclick="executeQuick('system', 'system_info')">💻 System Info</button>
                </div>
            </div>
            
            <div class="execution-panel">
                <div class="command-panel">
                    <h3><span class="icon">⚙️</span> Command Panel</h3>
                    
                    <form id="executionForm">
                        <div class="form-group">
                            <label for="service">Service:</label>
                            <select id="service" name="service" required>
                                <option value="">เลือก Service</option>
                                <option value="gemini_ai">🤖 Gemini AI</option>
                                <option value="google_drive">📁 Google Drive</option>
                                <option value="google_calendar">📅 Google Calendar</option>
                                <option value="gmail">📧 Gmail</option>
                                <option value="youtube">🎥 YouTube</option>
                                <option value="system">💻 System</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="command">Command:</label>
                            <input type="text" id="command" name="command" placeholder="ใส่คำสั่ง..." required>
                        </div>
                        
                        <div class="form-group" id="promptGroup" style="display: none;">
                            <label for="prompt">Prompt:</label>
                            <textarea id="prompt" name="prompt" placeholder="ใส่ prompt สำหรับ Gemini AI..."></textarea>
                        </div>
                        
                        <button type="submit" class="btn">⚡ Execute Command</button>
                        <button type="button" class="btn btn-success" onclick="clearResults()">🗑️ Clear Results</button>
                    </form>
                </div>
                
                <div class="results-panel">
                    <h3><span class="icon">📊</span> Execution Results</h3>
                    <div id="results">
                        <div class="loading">
                            <div class="spinner"></div>
                            <p>รอคำสั่ง...</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="actions">
                <a href="/" class="btn">🏠 กลับหน้าแรก</a>
                <a href="/dashboard" class="btn">📊 Dashboard</a>
                <a href="/history" class="btn">📜 Execution History</a>
            </div>
        </div>
    </div>
    
    <script>
        // Show/hide prompt field based on service
        document.getElementById('service').addEventListener('change', function() {
            const promptGroup = document.getElementById('promptGroup');
            if (this.value === 'gemini_ai') {
                promptGroup.style.display = 'block';
            } else {
                promptGroup.style.display = 'none';
            }
        });
        
        // Handle form submission
        document.getElementById('executionForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                service: formData.get('service'),
                command: formData.get('command'),
                prompt: formData.get('prompt')
            };
            
            executeCommand(data);
        });
        
        function executeCommand(data) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>กำลังประมวลผล...</p></div>';
            
            fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                displayResult(result);
            })
            .catch(error => {
                console.error('Error:', error);
                resultsDiv.innerHTML = '<div class="result-item error"><div class="result-header"><span class="result-service">Error</span><span class="result-status error">Failed</span></div><div class="result-content">' + error.message + '</div></div>';
            });
        }
        
        function executeQuick(service, command, prompt = null) {
            const data = { service, command };
            if (prompt) data.prompt = prompt;
            executeCommand(data);
        }
        
        function displayResult(result) {
            const resultsDiv = document.getElementById('results');
            const resultHtml = `
                <div class="result-item ${result.status}">
                    <div class="result-header">
                        <span class="result-service">${result.service}</span>
                        <span class="result-status ${result.status}">${result.status}</span>
                    </div>
                    <div class="result-timestamp">${result.timestamp}</div>
                    <div class="result-content">${JSON.stringify(result.result || result.error, null, 2)}</div>
                </div>
            `;
            
            resultsDiv.innerHTML = resultHtml + resultsDiv.innerHTML;
        }
        
        function clearResults() {
            document.getElementById('results').innerHTML = '<div class="loading"><div class="spinner"></div><p>รอคำสั่ง...</p></div>';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """หน้าแรก - Direct Execution"""
    if not direct_system.load_credentials():
        return redirect('/setup')
    
    return render_template_string(HTML_TEMPLATE)

@app.route('/execute', methods=['POST'])
def execute_command():
    """Execute Command"""
    try:
        data = request.get_json()
        service = data.get('service')
        command = data.get('command')
        prompt = data.get('prompt')
        
        result = direct_system.execute_command(service, command, prompt)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route('/dashboard')
def dashboard():
    """ไปยัง Google Services Dashboard"""
    return redirect('http://localhost:8004')

@app.route('/setup')
def setup():
    """ไปยังหน้า OAuth setup"""
    return redirect('http://localhost:8003')

@app.route('/history')
def history():
    """แสดง Execution History"""
    return jsonify(direct_system.execution_history)

def main():
    """Main function"""
    print("⚡ เริ่มต้น Direct Execution System")
    print("=" * 60)
    print(f"📍 URL: http://localhost:8005")
    print(f"🔐 API Key: {direct_system.api_key[:20]}...")
    print("=" * 60)
    
    # เริ่ม Flask server
    app.run(host='0.0.0.0', port=8005, debug=True)

if __name__ == "__main__":
    main() 