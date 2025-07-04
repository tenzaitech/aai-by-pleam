#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Services Dashboard for WAWAGOT - Complete Version
Dashboard สำหรับจัดการ Google Services ทั้งหมด
"""

import os
import json
import requests
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request, redirect, url_for
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Google Services Manager
class GoogleServicesDashboard:
    def __init__(self):
        self.credentials = None
        self.user_info = None
        self.services_status = {}
        self.api_key = "AIzaSyDXoRsK0eZK2nMuVzSLsRItBiH7OEfZ0y0"
        
    def load_credentials(self, filename="google_credentials_complete.json"):
        """โหลด credentials จากไฟล์"""
        try:
            if not os.path.exists(filename):
                return False
                
            with open(filename, "r") as f:
                creds_data = json.load(f)
            
            # สร้าง credentials object
            self.credentials = Credentials(
                token=creds_data.get("access_token"),
                refresh_token=creds_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=creds_data.get("client_id"),
                client_secret=creds_data.get("client_secret"),
                scopes=creds_data.get("scopes", [])
            )
            
            # ตรวจสอบว่า token หมดอายุหรือไม่
            if self.credentials and self.credentials.expired:
                self.credentials.refresh(Request())
                
                # บันทึก token ใหม่
                creds_data["access_token"] = self.credentials.token
                with open(filename, "w") as f:
                    json.dump(creds_data, f, indent=2)
            
            logger.info("✅ โหลด credentials สำเร็จ")
            return True
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถโหลด credentials ได้: {e}")
            return False
    
    def get_user_info(self):
        """ดึงข้อมูลผู้ใช้"""
        if not self.credentials:
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.credentials.token}"}
            response = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
            response.raise_for_status()
            
            self.user_info = response.json()
            return self.user_info
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถดึงข้อมูลผู้ใช้ได้: {e}")
            return None
    
    def test_google_drive(self):
        """ทดสอบ Google Drive"""
        if not self.credentials:
            return {"status": "error", "message": "ไม่มี credentials"}
            
        try:
            service = build("drive", "v3", credentials=self.credentials)
            results = service.files().list(pageSize=5).execute()
            files = results.get("files", [])
            
            return {
                "status": "success",
                "message": f"พบไฟล์ {len(files)} ไฟล์",
                "data": files
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def test_google_calendar(self):
        """ทดสอบ Google Calendar"""
        if not self.credentials:
            return {"status": "error", "message": "ไม่มี credentials"}
            
        try:
            service = build("calendar", "v3", credentials=self.credentials)
            now = datetime.utcnow().isoformat() + "Z"
            events_result = service.events().list(
                calendarId="primary",
                timeMin=now,
                maxResults=5,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            
            events = events_result.get("items", [])
            return {
                "status": "success",
                "message": f"พบ events {len(events)} รายการ",
                "data": events
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def test_gmail(self):
        """ทดสอบ Gmail"""
        if not self.credentials:
            return {"status": "error", "message": "ไม่มี credentials"}
            
        try:
            service = build("gmail", "v1", credentials=self.credentials)
            results = service.users().messages().list(userId="me", maxResults=5).execute()
            messages = results.get("messages", [])
            
            return {
                "status": "success",
                "message": f"พบ emails {len(messages)} ฉบับ",
                "data": messages
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def test_youtube_api(self):
        """ทดสอบ YouTube API"""
        try:
            youtube = build("youtube", "v3", developerKey=self.api_key)
            request = youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="TH",
                maxResults=5
            )
            response = request.execute()
            
            videos = response.get("items", [])
            return {
                "status": "success",
                "message": f"พบ videos {len(videos)} รายการ",
                "data": videos
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def test_gemini_ai(self):
        """ทดสอบ Gemini AI"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content("สวัสดีครับ ฉันคือ WAWAGOT AI Assistant")
            
            return {
                "status": "success",
                "message": "เชื่อมต่อ Gemini AI สำเร็จ",
                "data": {"response": response.text[:100] + "..."}
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def test_all_services(self):
        """ทดสอบ Google Services ทั้งหมด"""
        self.services_status = {
            "user_info": self.get_user_info(),
            "google_drive": self.test_google_drive(),
            "google_calendar": self.test_google_calendar(),
            "gmail": self.test_gmail(),
            "youtube_api": self.test_youtube_api(),
            "gemini_ai": self.test_gemini_ai()
        }
        
        return self.services_status

# สร้าง instance ของ dashboard
dashboard = GoogleServicesDashboard()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Services Dashboard - WAWAGOT</title>
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
            background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
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
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .status-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #4285f4;
            transition: transform 0.3s ease;
        }
        
        .status-card:hover {
            transform: translateY(-5px);
        }
        
        .status-card.success {
            border-left-color: #28a745;
            background: #d4edda;
        }
        
        .status-card.error {
            border-left-color: #dc3545;
            background: #f8d7da;
        }
        
        .status-card h3 {
            color: #333;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        
        .status-card .icon {
            margin-right: 10px;
            font-size: 1.2em;
        }
        
        .status-card .message {
            color: #666;
            margin-bottom: 10px;
            font-weight: bold;
        }
        
        .status-card .data {
            background: white;
            border-radius: 5px;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            max-height: 120px;
            overflow-y: auto;
            border: 1px solid #dee2e6;
        }
        
        .user-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .user-info h2 {
            margin-bottom: 15px;
        }
        
        .user-info .details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .user-info .detail {
            background: rgba(255,255,255,0.1);
            padding: 10px;
            border-radius: 5px;
        }
        
        .actions {
            text-align: center;
            margin-top: 30px;
        }
        
        .btn {
            background: #4285f4;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: #3367d6;
            transform: translateY(-2px);
        }
        
        .btn-success {
            background: #28a745;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .btn-danger {
            background: #dc3545;
        }
        
        .btn-danger:hover {
            background: #c82333;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #4285f4;
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
        
        .stats {
            background: #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .stats h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        
        .stat-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4285f4;
        }
        
        .stat-item.success {
            border-left-color: #28a745;
        }
        
        .stat-item.error {
            border-left-color: #dc3545;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Google Services Dashboard</h1>
            <p>จัดการและทดสอบ Google Services ทั้งหมด - WAWAGOT V.2</p>
        </div>
        
        <div class="content">
            {% if user_info %}
            <div class="user-info">
                <h2>👤 ข้อมูลผู้ใช้</h2>
                <div class="details">
                    <div class="detail">
                        <strong>ชื่อ:</strong> {{ user_info.name }}
                    </div>
                    <div class="detail">
                        <strong>อีเมล:</strong> {{ user_info.email }}
                    </div>
                    <div class="detail">
                        <strong>รูปโปรไฟล์:</strong> 
                        <img src="{{ user_info.picture }}" alt="Profile" style="width: 30px; height: 30px; border-radius: 50%;">
                    </div>
                </div>
            </div>
            {% endif %}
            
            {% if services_status %}
            <div class="stats">
                <h3>📊 สถิติการเชื่อมต่อ</h3>
                <div class="stats-grid">
                    {% set success_count = services_status.values() | selectattr('status', 'equalto', 'success') | list | length %}
                    {% set total_count = services_status | length %}
                    <div class="stat-item success">
                        <div class="stat-number">{{ success_count }}</div>
                        <div class="stat-label">เชื่อมต่อสำเร็จ</div>
                    </div>
                    <div class="stat-item error">
                        <div class="stat-number">{{ total_count - success_count }}</div>
                        <div class="stat-label">เชื่อมต่อล้มเหลว</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{{ "%.1f" | format(success_count / total_count * 100) }}%</div>
                        <div class="stat-label">อัตราความสำเร็จ</div>
                    </div>
                </div>
            </div>
            
            <div class="status-grid">
                {% for service, status in services_status.items() %}
                <div class="status-card {{ 'success' if status.status == 'success' else 'error' }}">
                    <h3>
                        <span class="icon">
                            {% if service == 'user_info' %}👤
                            {% elif service == 'google_drive' %}📁
                            {% elif service == 'google_calendar' %}📅
                            {% elif service == 'gmail' %}📧
                            {% elif service == 'youtube_api' %}🎥
                            {% elif service == 'gemini_ai' %}🤖
                            {% else %}🔧
                            {% endif %}
                        </span>
                        {{ service.replace('_', ' ').title() }}
                    </h3>
                    <div class="message">
                        {% if status.status == 'success' %}
                            ✅ {{ status.message }}
                        {% else %}
                            ❌ {{ status.message }}
                        {% endif %}
                    </div>
                    {% if status.data %}
                    <div class="data">
                        {{ status.data | tojson(indent=2) }}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="loading">
                <div class="spinner"></div>
                <p>กำลังโหลดข้อมูล...</p>
            </div>
            {% endif %}
            
            <div class="actions">
                <a href="/test" class="btn btn-success">🧪 ทดสอบ Services</a>
                <a href="/refresh" class="btn">🔄 รีเฟรช Token</a>
                <a href="/setup" class="btn btn-danger">🔐 ตั้งค่าใหม่</a>
                <a href="/direct" class="btn">⚡ Direct Execution</a>
            </div>
        </div>
    </div>
    
    <script>
        // Auto refresh every 30 seconds
        setTimeout(function() {
            location.reload();
        }, 30000);
        
        // Add click handlers for buttons
        document.addEventListener('DOMContentLoaded', function() {
            const testBtn = document.querySelector('a[href="/test"]');
            if (testBtn) {
                testBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    this.textContent = '🔄 กำลังทดสอบ...';
                    this.style.opacity = '0.7';
                    fetch('/test')
                        .then(response => response.json())
                        .then(data => {
                            location.reload();
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            location.reload();
                        });
                });
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """หน้าแรก - แสดง dashboard"""
    # โหลด credentials
    if dashboard.load_credentials():
        # ดึงข้อมูลผู้ใช้
        user_info = dashboard.get_user_info()
        
        # ทดสอบ services
        services_status = dashboard.test_all_services()
        
        return render_template_string(HTML_TEMPLATE, 
                                    user_info=user_info,
                                    services_status=services_status)
    else:
        return redirect('/setup')

@app.route('/test')
def test_services():
    """ทดสอบ Google Services"""
    if dashboard.load_credentials():
        services_status = dashboard.test_all_services()
        return jsonify(services_status)
    else:
        return jsonify({"error": "ไม่สามารถโหลด credentials ได้"})

@app.route('/refresh')
def refresh_token():
    """รีเฟรช access token"""
    if dashboard.credentials:
        try:
            dashboard.credentials.refresh(Request())
            
            # บันทึก token ใหม่
            creds_data = {
                "client_id": dashboard.credentials.client_id,
                "client_secret": dashboard.credentials.client_secret,
                "refresh_token": dashboard.credentials.refresh_token,
                "access_token": dashboard.credentials.token,
                "token_uri": "https://oauth2.googleapis.com/token",
                "scopes": dashboard.credentials.scopes
            }
            
            with open("google_credentials_complete.json", "w") as f:
                json.dump(creds_data, f, indent=2)
            
            return jsonify({"status": "success", "message": "รีเฟรช token สำเร็จ"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "error", "message": "ไม่มี credentials"})

@app.route('/setup')
def setup():
    """ไปยังหน้า OAuth setup"""
    return redirect('http://localhost:8003')

@app.route('/direct')
def direct_execution():
    """Direct Execution Mode"""
    return redirect('/direct-execution')

def main():
    """Main function"""
    print("🚀 เริ่มต้น Google Services Dashboard - Complete Version")
    print("=" * 60)
    print(f"📍 URL: http://localhost:8004")
    print(f"🔐 API Key: {dashboard.api_key[:20]}...")
    print("=" * 60)
    
    # เริ่ม Flask server
    app.run(host='0.0.0.0', port=8004, debug=True)

if __name__ == "__main__":
    main() 