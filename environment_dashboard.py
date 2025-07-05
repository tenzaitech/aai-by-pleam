# WAWAGOT.AI - Environment Dashboard
# ===============================================================================
# WAWAGOT.AI - Dashboard สำหรับจัดการสภาพแวดล้อม
# ===============================================================================
# Created: 2024-12-19
# Purpose: Dashboard สำหรับจัดการและตรวจสอบสภาพแวดล้อมทั้งหมด
# ===============================================================================

import asyncio
import json
import time
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    TZ_BANGKOK = ZoneInfo("Asia/Bangkok")
except ImportError:
    import pytz
    TZ_BANGKOK = pytz.timezone("Asia/Bangkok")
from typing import Dict, Any
import aiohttp
from aiohttp import web
import psutil
from system_environment_manager import SystemEnvironmentManager

# ===============================================================================
# DASHBOARD APPLICATION
# ===============================================================================

class EnvironmentDashboard:
    """Dashboard สำหรับจัดการสภาพแวดล้อม"""
    
    def __init__(self):
        self.env_manager = SystemEnvironmentManager()
        self.app = web.Application()
        self.setup_routes()
        self.update_interval = 5  # อัพเดททุก 5 วินาที
        
    def setup_routes(self):
        """ตั้งค่า routes"""
        self.app.router.add_get('/', self.dashboard_page)
        self.app.router.add_get('/api/status', self.get_system_status)
        self.app.router.add_get('/api/processes', self.get_processes)
        self.app.router.add_get('/api/network', self.get_network)
        self.app.router.add_get('/api/environment', self.get_environment)
        self.app.router.add_get('/api/services', self.get_services)
        self.app.router.add_post('/api/optimize', self.optimize_system)
        self.app.router.add_post('/api/env/set', self.set_environment_variable)
        self.app.router.add_get('/api/env/get/{name}', self.get_environment_variable)
        self.app.router.add_static('/static', 'static')
    
    async def dashboard_page(self, request):
        """หน้า Dashboard หลัก"""
        html_content = self._generate_dashboard_html()
        return web.Response(text=html_content, content_type='text/html')
    
    def _generate_dashboard_html(self) -> str:
        """สร้าง HTML สำหรับ Dashboard"""
        return """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WAWAGOT.AI - Environment Dashboard</title>
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
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            color: #2c3e50;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            text-align: center;
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding: 10px;
            background: rgba(52, 152, 219, 0.1);
            border-radius: 8px;
        }
        
        .metric-label {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .metric-value {
            font-weight: bold;
            color: #3498db;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #2ecc71, #27ae60);
            transition: width 0.3s ease;
        }
        
        .progress-fill.warning {
            background: linear-gradient(90deg, #f39c12, #e67e22);
        }
        
        .progress-fill.danger {
            background: linear-gradient(90deg, #e74c3c, #c0392b);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online {
            background: #2ecc71;
        }
        
        .status-offline {
            background: #e74c3c;
        }
        
        .status-warning {
            background: #f39c12;
        }
        
        .button {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s ease;
            margin: 5px;
        }
        
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
        }
        
        .button.optimize {
            background: linear-gradient(135deg, #2ecc71, #27ae60);
        }
        
        .button.optimize:hover {
            box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .table th, .table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }
        
        .table th {
            background: rgba(52, 152, 219, 0.1);
            font-weight: 600;
            color: #2c3e50;
        }
        
        .table tr:hover {
            background: rgba(52, 152, 219, 0.05);
        }
        
        .refresh-time {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 20px;
        }
        
        .loading {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 WAWAGOT.AI Environment Dashboard</h1>
            <p>ระบบจัดการและตรวจสอบสภาพแวดล้อมทั้งหมด</p>
        </div>
        
        <div class="grid">
            <!-- System Performance Card -->
            <div class="card">
                <h3>📊 System Performance</h3>
                <div id="performance-metrics">
                    <div class="loading">กำลังโหลด...</div>
                </div>
                <button class="button optimize" onclick="optimizeSystem()">🔧 ปรับปรุงระบบ</button>
            </div>
            
            <!-- System Info Card -->
            <div class="card">
                <h3>💻 System Information</h3>
                <div id="system-info">
                    <div class="loading">กำลังโหลด...</div>
                </div>
            </div>
            
            <!-- Network Status Card -->
            <div class="card">
                <h3>🌐 Network Status</h3>
                <div id="network-status">
                    <div class="loading">กำลังโหลด...</div>
                </div>
            </div>
            
            <!-- Services Status Card -->
            <div class="card">
                <h3>🔧 Services Status</h3>
                <div id="services-status">
                    <div class="loading">กำลังโหลด...</div>
                </div>
            </div>
            
            <!-- Environment Variables Card -->
            <div class="card">
                <h3>⚙️ Environment Variables</h3>
                <div id="env-vars">
                    <div class="loading">กำลังโหลด...</div>
                </div>
                <button class="button" onclick="showEnvForm()">➕ เพิ่ม Environment Variable</button>
            </div>
            
            <!-- Process Monitor Card -->
            <div class="card">
                <h3>📈 Process Monitor</h3>
                <div id="process-monitor">
                    <div class="loading">กำลังโหลด...</div>
                </div>
            </div>

            <!-- Text Generation Card -->
            <div class="card">
                <h3>📝 Text Generation</h3>
                <div class="form-group">
                    <label>Prompt:</label>
                    <textarea id="text-prompt" placeholder="ใส่ข้อความที่ต้องการสร้าง..."></textarea>
                </div>
                <div class="form-group">
                    <label>Provider:</label>
                    <select id="text-provider">
                        <option value="openai">OpenAI</option>
                        <option value="gemini">Gemini</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Device:</label>
                    <select id="text-device">
                        <option value="auto">Auto (GPU/CPU)</option>
                        <option value="gpu">GPU Only</option>
                        <option value="cpu">CPU Only</option>
                    </select>
                </div>
                <button class="button" onclick="generateText()">🚀 สร้างข้อความ</button>
                <div id="text-result" class="result-box" style="display: none;"></div>
            </div>
            
            <!-- Image Processing Card -->
            <div class="card">
                <h3>🖼️ Image Processing</h3>
                <div class="form-group">
                    <label>อัปโหลดภาพ:</label>
                    <input type="file" id="image-file" accept="image/*">
                </div>
                <div class="form-group">
                    <label>Operation:</label>
                    <select id="image-operation">
                        <option value="resize">Resize</option>
                        <option value="filter">Filter</option>
                        <option value="detection">Detection</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Device:</label>
                    <select id="image-device">
                        <option value="auto">Auto (GPU/CPU)</option>
                        <option value="gpu">GPU Only</option>
                        <option value="cpu">CPU Only</option>
                    </select>
                </div>
                <button class="button" onclick="processImage()">🖼️ ประมวลผลภาพ</button>
                <div id="image-result" class="result-box" style="display: none;"></div>
            </div>
        </div>
        
        <div class="refresh-time">
            อัพเดทล่าสุด: <span id="last-update">-</span>
        </div>
    </div>
    
    <!-- Environment Variable Form Modal -->
    <div id="env-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 15px; min-width: 400px;">
            <h3>เพิ่ม Environment Variable</h3>
            <form id="env-form">
                <div style="margin-bottom: 15px;">
                    <label>ชื่อ:</label><br>
                    <input type="text" id="env-name" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label>ค่า:</label><br>
                    <input type="text" id="env-value" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                </div>
                <button type="submit" class="button">บันทึก</button>
                <button type="button" class="button" onclick="hideEnvForm()" style="background: #95a5a6;">ยกเลิก</button>
            </form>
        </div>
    </div>
    
    <script>
        // Global variables
        let updateInterval;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboard();
            updateInterval = setInterval(loadDashboard, 5000); // Update every 5 seconds
        });
        
        async function loadDashboard() {
            try {
                // Load system status
                const statusResponse = await fetch('/api/status');
                const statusData = await statusResponse.json();
                
                if (statusData.success) {
                    updatePerformanceMetrics(statusData);
                    updateSystemInfo(statusData);
                    updateNetworkStatus(statusData);
                    updateServicesStatus(statusData);
                    updateProcessMonitor(statusData);
                    updateEnvironmentVariables(statusData);
                    updateLastUpdate();
                }
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }
        
        function updatePerformanceMetrics(data) {
            const container = document.getElementById('performance-metrics');
            const performance = data.performance;
            
            container.innerHTML = `
                <div class="metric">
                    <span class="metric-label">CPU Usage:</span>
                    <span class="metric-value">${performance.cpu_percent.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${getProgressClass(performance.cpu_percent)}" style="width: ${performance.cpu_percent}%"></div>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Memory Usage:</span>
                    <span class="metric-value">${performance.memory_percent.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${getProgressClass(performance.memory_percent)}" style="width: ${performance.memory_percent}%"></div>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Disk Usage:</span>
                    <span class="metric-value">${performance.disk_percent.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${getProgressClass(performance.disk_percent)}" style="width: ${performance.disk_percent}%"></div>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Process Count:</span>
                    <span class="metric-value">${performance.process_count}</span>
                </div>
            `;
        }
        
        function updateSystemInfo(data) {
            const container = document.getElementById('system-info');
            const systemInfo = data.system_info;
            
            container.innerHTML = `
                <div class="metric">
                    <span class="metric-label">OS:</span>
                    <span class="metric-value">${systemInfo.os_name} ${systemInfo.os_version}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Architecture:</span>
                    <span class="metric-value">${systemInfo.architecture}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Python:</span>
                    <span class="metric-value">${systemInfo.python_version}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">CPU Cores:</span>
                    <span class="metric-value">${systemInfo.cpu_count}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Memory:</span>
                    <span class="metric-value">${(systemInfo.total_memory / 1024 / 1024 / 1024).toFixed(1)} GB</span>
                </div>
            `;
        }
        
        function updateNetworkStatus(data) {
            const container = document.getElementById('network-status');
            const network = data.network;
            
            let networkHtml = '';
            for (const [name, info] of Object.entries(network)) {
                networkHtml += `
                    <div class="metric">
                        <span class="metric-label">${name}:</span>
                        <span class="metric-value">${info.ip_address || 'N/A'}</span>
                    </div>
                `;
            }
            
            container.innerHTML = networkHtml || '<div class="loading">ไม่พบข้อมูลเครือข่าย</div>';
        }
        
        function updateServicesStatus(data) {
            const container = document.getElementById('services-status');
            const services = data.services;
            
            let servicesHtml = '';
            for (const [name, service] of Object.entries(services)) {
                const statusClass = service.status === 'running' ? 'status-online' : 'status-offline';
                servicesHtml += `
                    <div class="metric">
                        <span class="metric-label">
                            <span class="status-indicator ${statusClass}"></span>
                            ${name}:
                        </span>
                        <span class="metric-value">${service.status}</span>
                    </div>
                `;
            }
            
            container.innerHTML = servicesHtml || '<div class="loading">ไม่พบข้อมูลบริการ</div>';
        }
        
        function updateProcessMonitor(data) {
            const container = document.getElementById('process-monitor');
            const processes = data.processes;
            
            // Get top 5 processes by CPU usage
            const topProcesses = Object.values(processes)
                .sort((a, b) => b.cpu_percent - a.cpu_percent)
                .slice(0, 5);
            
            let processesHtml = '<table class="table"><thead><tr><th>Process</th><th>CPU %</th><th>Memory MB</th></tr></thead><tbody>';
            
            for (const process of topProcesses) {
                processesHtml += `
                    <tr>
                        <td>${process.name}</td>
                        <td>${process.cpu_percent.toFixed(1)}%</td>
                        <td>${process.memory_mb}</td>
                    </tr>
                `;
            }
            
            processesHtml += '</tbody></table>';
            container.innerHTML = processesHtml;
        }
        
        function updateEnvironmentVariables(data) {
            const container = document.getElementById('env-vars');
            const envVars = data.environment_variables;
            
            // Show only first 10 environment variables
            const envVarsList = Object.entries(envVars).slice(0, 10);
            
            let envHtml = '';
            for (const [name, env] of envVarsList) {
                envHtml += `
                    <div class="metric">
                        <span class="metric-label">${name}:</span>
                        <span class="metric-value">${env.value}</span>
                    </div>
                `;
            }
            
            container.innerHTML = envHtml || '<div class="loading">ไม่พบ Environment Variables</div>';
        }
        
        function updateLastUpdate() {
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString('th-TH');
        }
        
        function getProgressClass(value) {
            if (value >= 90) return 'danger';
            if (value >= 70) return 'warning';
            return '';
        }
        
        async function optimizeSystem() {
            try {
                const response = await fetch('/api/optimize', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    alert('ปรับปรุงระบบสำเร็จ!');
                    loadDashboard(); // Reload dashboard
                } else {
                    alert('เกิดข้อผิดพลาดในการปรับปรุงระบบ: ' + result.error);
                }
            } catch (error) {
                alert('เกิดข้อผิดพลาดในการเชื่อมต่อ: ' + error.message);
            }
        }
        
        function showEnvForm() {
            document.getElementById('env-modal').style.display = 'block';
        }
        
        function hideEnvForm() {
            document.getElementById('env-modal').style.display = 'none';
        }
        
        document.getElementById('env-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const name = document.getElementById('env-name').value;
            const value = document.getElementById('env-value').value;
            
            try {
                const response = await fetch('/api/env/set', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, value })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('ตั้งค่า Environment Variable สำเร็จ!');
                    hideEnvForm();
                    loadDashboard(); // Reload dashboard
                } else {
                    alert('เกิดข้อผิดพลาด: ' + result.error);
                }
            } catch (error) {
                alert('เกิดข้อผิดพลาดในการเชื่อมต่อ: ' + error.message);
            }
        });

        async function generateText() {
            const prompt = document.getElementById('text-prompt').value;
            const provider = document.getElementById('text-provider').value;
            const device = document.getElementById('text-device').value;
            
            if (!prompt) {
                alert('กรุณาใส่ข้อความ');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/api/ai/text/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: prompt,
                        provider: provider,
                        device: device,
                        max_tokens: 1000,
                        temperature: 0.7
                    })
                });
                
                const result = await response.json();
                const resultBox = document.getElementById('text-result');
                
                if (result.success) {
                    resultBox.innerHTML = `
                        <div class="success">✅ สร้างข้อความสำเร็จ!</div>
                        <strong>ผลลัพธ์:</strong><br>
                        ${result.text}<br><br>
                        <strong>Provider:</strong> ${result.provider}<br>
                        <strong>Device Used:</strong> ${result.device_used}<br>
                        <strong>GPU Accelerated:</strong> ${result.gpu_accelerated ? 'ใช่' : 'ไม่'}<br>
                        <strong>Processing Time:</strong> ${result.processing_time}s
                    `;
                } else {
                    resultBox.innerHTML = `<div class="error">❌ เกิดข้อผิดพลาด: ${result.error}</div>`;
                }
                
                resultBox.style.display = 'block';
            } catch (error) {
                alert('เกิดข้อผิดพลาด: ' + error.message);
            }
        }
        
        async function processImage() {
            const fileInput = document.getElementById('image-file');
            const operation = document.getElementById('image-operation').value;
            const device = document.getElementById('image-device').value;
            
            if (!fileInput.files[0]) {
                alert('กรุณาเลือกไฟล์ภาพ');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('operation', operation);
            formData.append('device', device);
            
            try {
                const response = await fetch(`${API_BASE_URL}/api/ai/image/process`, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                const resultBox = document.getElementById('image-result');
                
                if (result.success) {
                    resultBox.innerHTML = `
                        <div class="success">✅ ประมวลผลภาพสำเร็จ!</div>
                        <strong>Operation:</strong> ${result.operation}<br>
                        <strong>Device Used:</strong> ${result.device_used}<br>
                        <strong>GPU Accelerated:</strong> ${result.gpu_accelerated ? 'ใช่' : 'ไม่'}<br>
                        <strong>Processing Time:</strong> ${result.processing_time}s<br><br>
                        <img src="data:image/jpeg;base64,${result.image_data}" style="max-width: 100%; height: auto;">
                    `;
                } else {
                    resultBox.innerHTML = `<div class="error">❌ เกิดข้อผิดพลาด: ${result.error}</div>`;
                }
                
                resultBox.style.display = 'block';
            } catch (error) {
                alert('เกิดข้อผิดพลาด: ' + error.message);
            }
        }
    </script>
</body>
</html>
        """
    
    async def get_system_status(self, request):
        """API สำหรับดึงสถานะระบบ"""
        try:
            status = await self.env_manager.get_system_status()
            return web.json_response(status)
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)})
    
    async def get_processes(self, request):
        """API สำหรับดึงข้อมูล Process"""
        try:
            status = await self.env_manager.get_system_status()
            return web.json_response({
                "success": True,
                "processes": status.get("processes", {})
            })
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)})
    
    async def get_network(self, request):
        """API สำหรับดึงข้อมูลเครือข่าย"""
        try:
            status = await self.env_manager.get_system_status()
            return web.json_response({
                "success": True,
                "network": status.get("network", {})
            })
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)})
    
    async def get_environment(self, request):
        """API สำหรับดึงข้อมูล Environment Variables"""
        try:
            status = await self.env_manager.get_system_status()
            return web.json_response({
                "success": True,
                "environment_variables": status.get("environment_variables", {})
            })
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)})
    
    async def get_services(self, request):
        """API สำหรับดึงข้อมูลบริการ"""
        try:
            status = await self.env_manager.get_system_status()
            return web.json_response({
                "success": True,
                "services": status.get("services", {})
            })
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)})
    
    async def optimize_system(self, request):
        """API สำหรับปรับปรุงระบบ"""
        try:
            optimization = await self.env_manager.optimize_environment()
            return web.json_response(optimization)
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)})
    
    async def set_environment_variable(self, request):
        """API สำหรับตั้งค่า Environment Variable"""
        try:
            data = await request.json()
            name = data.get("name")
            value = data.get("value")
            
            if not name or not value:
                return web.json_response({
                    "success": False,
                    "error": "ต้องระบุ name และ value"
                })
            
            result = await self.env_manager.set_environment_variable(name, value)
            return web.json_response(result)
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)})
    
    async def get_environment_variable(self, request):
        """API สำหรับดึง Environment Variable"""
        try:
            name = request.match_info['name']
            result = await self.env_manager.get_environment_variable(name)
            return web.json_response(result)
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)})
    
    async def start_dashboard(self, host="0.0.0.0", port=8080):
        """เริ่มต้น Dashboard"""
        # เริ่มต้น Environment Manager
        await self.env_manager.initialize_system()
        
        # เริ่มต้น web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        
        print(f"🚀 Environment Dashboard เริ่มต้นที่: http://{host}:{port}")
        print("📊 ระบบพร้อมใช้งาน!")
        
        await site.start()
        
        # รอสัญญาณหยุด
        try:
            await asyncio.Future()  # รอตลอดไป
        except KeyboardInterrupt:
            print("\n🛑 หยุด Dashboard...")
            await runner.cleanup()

# ===============================================================================
# MAIN EXECUTION
# ===============================================================================

async def main():
    """ฟังก์ชันหลัก"""
    dashboard = EnvironmentDashboard()
    await dashboard.start_dashboard()

if __name__ == "__main__":
    asyncio.run(main()) 