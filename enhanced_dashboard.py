#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI - Enhanced Dashboard
ระบบ Dashboard สำหรับจัดการระบบ Backup, Monitoring และ Integration
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for
from core.logger import get_logger

# Import our enhanced systems
from enhanced_backup_manager import EnhancedBackupManager
from enhanced_monitoring_system import EnhancedMonitoringSystem
from enhanced_integration_manager import EnhancedIntegrationManager
from enhanced_service_manager import EnhancedServiceManager

app = Flask(__name__)
app.secret_key = 'wawagot_enhanced_dashboard_secret_key'

class EnhancedDashboard:
    def __init__(self):
        self.logger = get_logger("enhanced_dashboard")
        self.project_root = Path(__file__).parent
        
        # Initialize systems
        self.backup_manager = None
        self.monitoring_system = None
        self.integration_manager = None
        self.service_manager = None
        
        # Dashboard configuration
        self.config = {
            "dashboard_enabled": True,
            "port": 5001,
            "host": "0.0.0.0",
            "debug": False,
            "auto_refresh": True,
            "refresh_interval": 30
        }
        
        # Load configuration
        self.load_config()
        
        # Initialize systems
        self.initialize_systems()
        
        # Setup routes
        self.setup_routes()

    def load_config(self):
        """Load dashboard configuration"""
        config_file = self.project_root / "config" / "dashboard_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                self.logger.info("Loaded dashboard configuration")
            except Exception as e:
                self.logger.error(f"Error loading dashboard config: {e}")

    def save_config(self):
        """Save dashboard configuration"""
        config_file = self.project_root / "config" / "dashboard_config.json"
        config_file.parent.mkdir(exist_ok=True)
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info("Saved dashboard configuration")
        except Exception as e:
            self.logger.error(f"Error saving dashboard config: {e}")

    def initialize_systems(self):
        """Initialize all systems"""
        try:
            self.logger.info("Initializing dashboard systems...")
            
            # Initialize backup manager
            self.backup_manager = EnhancedBackupManager()
            self.logger.info("Backup manager initialized")
            
            # Initialize monitoring system
            self.monitoring_system = EnhancedMonitoringSystem()
            self.logger.info("Monitoring system initialized")
            
            # Initialize integration manager
            self.integration_manager = EnhancedIntegrationManager()
            self.logger.info("Integration manager initialized")
            
            # Initialize service manager
            self.service_manager = EnhancedServiceManager()
            self.logger.info("Service manager initialized")
            
            self.logger.info("All dashboard systems initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing dashboard systems: {e}")

    def setup_routes(self):
        """Setup Flask routes"""
        
        @app.route('/')
        def index():
            """Main dashboard page"""
            try:
                # Get system status
                dashboard_data = self.get_dashboard_data()
                return render_template('enhanced_dashboard.html', data=dashboard_data)
            except Exception as e:
                self.logger.error(f"Error rendering dashboard: {e}")
                return f"Dashboard Error: {e}", 500

        @app.route('/api/status')
        def api_status():
            """API endpoint for system status"""
            try:
                return jsonify(self.get_dashboard_data())
            except Exception as e:
                self.logger.error(f"Error getting status: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route('/api/backup/status')
        def api_backup_status():
            """API endpoint for backup status"""
            try:
                if self.backup_manager:
                    return jsonify(self.backup_manager.get_backup_status())
                else:
                    return jsonify({"error": "Backup manager not initialized"}), 500
            except Exception as e:
                self.logger.error(f"Error getting backup status: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route('/api/backup/create', methods=['POST'])
        def api_create_backup():
            """API endpoint for creating backup"""
            try:
                backup_type = request.json.get('type', 'full')
                if self.backup_manager:
                    success = self.backup_manager.create_backup(backup_type)
                    return jsonify({
                        "status": "success" if success else "failed",
                        "type": backup_type
                    })
                else:
                    return jsonify({"error": "Backup manager not initialized"}), 500
            except Exception as e:
                self.logger.error(f"Error creating backup: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route('/api/monitoring/status')
        def api_monitoring_status():
            """API endpoint for monitoring status"""
            try:
                if self.monitoring_system:
                    return jsonify(self.monitoring_system.get_monitoring_status())
                else:
                    return jsonify({"error": "Monitoring system not initialized"}), 500
            except Exception as e:
                self.logger.error(f"Error getting monitoring status: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route('/api/monitoring/alerts')
        def api_monitoring_alerts():
            """API endpoint for monitoring alerts"""
            try:
                limit = request.args.get('limit', 10, type=int)
                if self.monitoring_system:
                    return jsonify(self.monitoring_system.get_alerts(limit=limit))
                else:
                    return jsonify({"error": "Monitoring system not initialized"}), 500
            except Exception as e:
                self.logger.error(f"Error getting alerts: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route('/api/monitoring/clear_alerts', methods=['POST'])
        def api_clear_alerts():
            """API endpoint for clearing alerts"""
            try:
                if self.monitoring_system:
                    success = self.monitoring_system.clear_alerts()
                    return jsonify({"status": "success" if success else "failed"})
                else:
                    return jsonify({"error": "Monitoring system not initialized"}), 500
            except Exception as e:
                self.logger.error(f"Error clearing alerts: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route('/api/integration/status')
        def api_integration_status():
            """API endpoint for integration status"""
            try:
                if self.integration_manager:
                    return jsonify(self.integration_manager.get_integration_status())
                else:
                    return jsonify({"error": "Integration manager not initialized"}), 500
            except Exception as e:
                self.logger.error(f"Error getting integration status: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route('/api/service/status')
        def api_service_status():
            """API endpoint for service status"""
            try:
                if self.service_manager:
                    return jsonify(self.service_manager.get_service_info())
                else:
                    return jsonify({"error": "Service manager not initialized"}), 500
            except Exception as e:
                self.logger.error(f"Error getting service status: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route('/api/service/control', methods=['POST'])
        def api_service_control():
            """API endpoint for service control"""
            try:
                action = request.json.get('action')
                if not action:
                    return jsonify({"error": "Action required"}), 400
                
                if self.service_manager:
                    success = False
                    message = ""
                    
                    if action == 'start':
                        success = self.service_manager.start_service()
                        message = "Service started successfully" if success else "Failed to start service"
                    elif action == 'stop':
                        success = self.service_manager.stop_service()
                        message = "Service stopped successfully" if success else "Failed to stop service"
                    elif action == 'restart':
                        success = self.service_manager.restart_service()
                        message = "Service restarted successfully" if success else "Failed to restart service"
                    elif action == 'install':
                        success = self.service_manager.install_service()
                        message = "Service installed successfully" if success else "Failed to install service"
                    elif action == 'uninstall':
                        success = self.service_manager.uninstall_service()
                        message = "Service uninstalled successfully" if success else "Failed to uninstall service"
                    else:
                        return jsonify({"error": "Invalid action"}), 400
                    
                    return jsonify({
                        "status": "success" if success else "failed",
                        "action": action,
                        "message": message
                    })
                else:
                    return jsonify({"error": "Service manager not initialized"}), 500
            except Exception as e:
                self.logger.error(f"Error controlling service: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route('/api/health')
        def api_health():
            """API endpoint for health check"""
            try:
                if self.integration_manager:
                    health = self.integration_manager.perform_health_check()
                    return jsonify(health)
                else:
                    return jsonify({"error": "Integration manager not initialized"}), 500
            except Exception as e:
                self.logger.error(f"Error performing health check: {e}")
                return jsonify({"error": str(e)}), 500

    def get_dashboard_data(self):
        """Get comprehensive dashboard data"""
        try:
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "dashboard_config": self.config,
                "systems": {}
            }
            
            # Backup system data
            if self.backup_manager:
                dashboard_data["systems"]["backup"] = self.backup_manager.get_backup_status()
            
            # Monitoring system data
            if self.monitoring_system:
                dashboard_data["systems"]["monitoring"] = self.monitoring_system.get_monitoring_status()
                dashboard_data["systems"]["alerts"] = self.monitoring_system.get_alerts(limit=5)
            
            # Integration system data
            if self.integration_manager:
                dashboard_data["systems"]["integration"] = self.integration_manager.get_integration_status()
            
            # Service system data
            if self.service_manager:
                dashboard_data["systems"]["service"] = self.service_manager.get_service_info()
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {"error": str(e)}

    def start_dashboard(self):
        """Start the dashboard"""
        try:
            if not self.config["dashboard_enabled"]:
                self.logger.info("Dashboard disabled in configuration")
                return
            
            self.logger.info(f"Starting enhanced dashboard on {self.config['host']}:{self.config['port']}")
            
            # Create templates directory if it doesn't exist
            templates_dir = self.project_root / "templates"
            templates_dir.mkdir(exist_ok=True)
            
            # Create enhanced dashboard template
            self.create_dashboard_template()
            
            # Start Flask app
            app.run(
                host=self.config["host"],
                port=self.config["port"],
                debug=self.config["debug"]
            )
            
        except Exception as e:
            self.logger.error(f"Error starting dashboard: {e}")

    def create_dashboard_template(self):
        """Create enhanced dashboard template"""
        template_content = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WAWAGOT.AI - Enhanced Dashboard</title>
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
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            color: #4a5568;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            text-align: center;
            color: #718096;
            font-size: 1.1em;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .card h2 {
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-healthy { background-color: #48bb78; }
        .status-warning { background-color: #ed8936; }
        .status-error { background-color: #f56565; }
        .status-unknown { background-color: #a0aec0; }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f7fafc;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 500;
            color: #4a5568;
        }
        
        .metric-value {
            font-weight: 600;
            color: #2d3748;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background-color: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin: 5px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #48bb78, #38a169);
            transition: width 0.3s ease;
        }
        
        .progress-fill.warning {
            background: linear-gradient(90deg, #ed8936, #dd6b20);
        }
        
        .progress-fill.error {
            background: linear-gradient(90deg, #f56565, #e53e3e);
        }
        
        .button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: transform 0.2s ease;
            margin: 5px;
        }
        
        .button:hover {
            transform: translateY(-2px);
        }
        
        .button:active {
            transform: translateY(0);
        }
        
        .button.danger {
            background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        }
        
        .button.success {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        }
        
        .button.warning {
            background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        }
        
        .alert {
            padding: 12px;
            border-radius: 8px;
            margin: 10px 0;
            font-weight: 500;
        }
        
        .alert.warning {
            background-color: #fed7d7;
            color: #c53030;
            border: 1px solid #feb2b2;
        }
        
        .alert.info {
            background-color: #bee3f8;
            color: #2b6cb0;
            border: 1px solid #90cdf4;
        }
        
        .alert.success {
            background-color: #c6f6d5;
            color: #22543d;
            border: 1px solid #9ae6b4;
        }
        
        .refresh-info {
            text-align: center;
            color: #718096;
            font-size: 0.9em;
            margin-top: 20px;
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
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
            <h1>🚀 WAWAGOT.AI Enhanced Dashboard</h1>
            <p>ระบบจัดการ Backup, Monitoring และ Integration แบบครบวงจร</p>
        </div>
        
        <div class="dashboard-grid">
            <!-- Backup System Card -->
            <div class="card">
                <h2>💾 Backup System</h2>
                <div id="backup-status">
                    <div class="metric">
                        <span class="metric-label">สถานะ:</span>
                        <span class="metric-value">
                            <span class="status-indicator status-unknown"></span>
                            กำลังโหลด...
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Backup ล่าสุด:</span>
                        <span class="metric-value" id="last-backup">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">จำนวน Backup:</span>
                        <span class="metric-value" id="backup-count">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">ขนาด Backup:</span>
                        <span class="metric-value" id="backup-size">-</span>
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="button success" onclick="createBackup('full')">สร้าง Full Backup</button>
                        <button class="button" onclick="createBackup('config')">สร้าง Config Backup</button>
                    </div>
                </div>
            </div>
            
            <!-- Monitoring System Card -->
            <div class="card">
                <h2>📊 Monitoring System</h2>
                <div id="monitoring-status">
                    <div class="metric">
                        <span class="metric-label">สถานะ:</span>
                        <span class="metric-value">
                            <span class="status-indicator status-unknown"></span>
                            กำลังโหลด...
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">CPU Usage:</span>
                        <span class="metric-value" id="cpu-usage">-</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="cpu-progress" style="width: 0%"></div>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Memory Usage:</span>
                        <span class="metric-value" id="memory-usage">-</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="memory-progress" style="width: 0%"></div>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Alerts:</span>
                        <span class="metric-value" id="alerts-count">-</span>
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="button" onclick="clearAlerts()">ล้าง Alerts</button>
                        <button class="button" onclick="refreshMonitoring()">รีเฟรช</button>
                    </div>
                </div>
            </div>
            
            <!-- Integration System Card -->
            <div class="card">
                <h2>🔗 Integration System</h2>
                <div id="integration-status">
                    <div class="metric">
                        <span class="metric-label">สถานะ:</span>
                        <span class="metric-value">
                            <span class="status-indicator status-unknown"></span>
                            กำลังโหลด...
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Integration Enabled:</span>
                        <span class="metric-value" id="integration-enabled">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Health Check:</span>
                        <span class="metric-value" id="health-status">-</span>
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="button" onclick="performHealthCheck()">Health Check</button>
                        <button class="button" onclick="refreshIntegration()">รีเฟรช</button>
                    </div>
                </div>
            </div>
            
            <!-- Service System Card -->
            <div class="card">
                <h2>⚙️ Service System</h2>
                <div id="service-status">
                    <div class="metric">
                        <span class="metric-label">สถานะ:</span>
                        <span class="metric-value">
                            <span class="status-indicator status-unknown"></span>
                            กำลังโหลด...
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Service Status:</span>
                        <span class="metric-value" id="service-status-value">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Installed:</span>
                        <span class="metric-value" id="service-installed">-</span>
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="button warning" onclick="controlService('install')">Install</button>
                        <button class="button success" onclick="controlService('start')">Start</button>
                        <button class="button danger" onclick="controlService('stop')">Stop</button>
                        <button class="button" onclick="controlService('restart')">Restart</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="refresh-info">
            <p>🔄 ข้อมูลจะอัพเดทอัตโนมัติทุก 30 วินาที | Last Update: <span id="last-update">-</span></p>
        </div>
    </div>

    <script>
        // Global variables
        let refreshInterval;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboardData();
            startAutoRefresh();
        });
        
        // Load dashboard data
        async function loadDashboardData() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                if (data.error) {
                    console.error('Error loading dashboard data:', data.error);
                    return;
                }
                
                updateDashboard(data);
                document.getElementById('last-update').textContent = new Date().toLocaleString('th-TH');
                
            } catch (error) {
                console.error('Error loading dashboard data:', error);
            }
        }
        
        // Update dashboard with data
        function updateDashboard(data) {
            // Update backup system
            if (data.systems && data.systems.backup) {
                updateBackupStatus(data.systems.backup);
            }
            
            // Update monitoring system
            if (data.systems && data.systems.monitoring) {
                updateMonitoringStatus(data.systems.monitoring);
            }
            
            // Update integration system
            if (data.systems && data.systems.integration) {
                updateIntegrationStatus(data.systems.integration);
            }
            
            // Update service system
            if (data.systems && data.systems.service) {
                updateServiceStatus(data.systems.service);
            }
        }
        
        // Update backup status
        function updateBackupStatus(backupData) {
            const statusElement = document.querySelector('#backup-status .metric:first-child .metric-value');
            const lastBackupElement = document.getElementById('last-backup');
            const backupCountElement = document.getElementById('backup-count');
            const backupSizeElement = document.getElementById('backup-size');
            
            if (backupData.error) {
                statusElement.innerHTML = '<span class="status-indicator status-error"></span>Error';
                lastBackupElement.textContent = 'Error';
                backupCountElement.textContent = 'Error';
                backupSizeElement.textContent = 'Error';
            } else {
                statusElement.innerHTML = '<span class="status-indicator status-healthy"></span>Healthy';
                lastBackupElement.textContent = backupData.last_backup || 'Never';
                backupCountElement.textContent = backupData.backup_count || 0;
                backupSizeElement.textContent = backupData.backup_size || '0 MB';
            }
        }
        
        // Update monitoring status
        function updateMonitoringStatus(monitoringData) {
            const statusElement = document.querySelector('#monitoring-status .metric:first-child .metric-value');
            const cpuUsageElement = document.getElementById('cpu-usage');
            const memoryUsageElement = document.getElementById('memory-usage');
            const alertsCountElement = document.getElementById('alerts-count');
            const cpuProgressElement = document.getElementById('cpu-progress');
            const memoryProgressElement = document.getElementById('memory-progress');
            
            if (monitoringData.error) {
                statusElement.innerHTML = '<span class="status-indicator status-error"></span>Error';
                cpuUsageElement.textContent = 'Error';
                memoryUsageElement.textContent = 'Error';
                alertsCountElement.textContent = 'Error';
            } else {
                statusElement.innerHTML = '<span class="status-indicator status-healthy"></span>Healthy';
                
                const systemStatus = monitoringData.system_status || {};
                const cpuUsage = systemStatus.cpu_usage || 0;
                const memoryUsage = systemStatus.memory_usage || 0;
                const alertsCount = monitoringData.alerts_count || 0;
                
                cpuUsageElement.textContent = cpuUsage.toFixed(1) + '%';
                memoryUsageElement.textContent = memoryUsage.toFixed(1) + '%';
                alertsCountElement.textContent = alertsCount;
                
                cpuProgressElement.style.width = cpuUsage + '%';
                cpuProgressElement.className = 'progress-fill' + (cpuUsage > 80 ? ' warning' : '') + (cpuUsage > 90 ? ' error' : '');
                
                memoryProgressElement.style.width = memoryUsage + '%';
                memoryProgressElement.className = 'progress-fill' + (memoryUsage > 80 ? ' warning' : '') + (memoryUsage > 90 ? ' error' : '');
            }
        }
        
        // Update integration status
        function updateIntegrationStatus(integrationData) {
            const statusElement = document.querySelector('#integration-status .metric:first-child .metric-value');
            const enabledElement = document.getElementById('integration-enabled');
            
            if (integrationData.error) {
                statusElement.innerHTML = '<span class="status-indicator status-error"></span>Error';
                enabledElement.textContent = 'Error';
            } else {
                statusElement.innerHTML = '<span class="status-indicator status-healthy"></span>Healthy';
                enabledElement.textContent = integrationData.integration_enabled ? 'Yes' : 'No';
            }
        }
        
        // Update service status
        function updateServiceStatus(serviceData) {
            const statusElement = document.querySelector('#service-status .metric:first-child .metric-value');
            const serviceStatusElement = document.getElementById('service-status-value');
            const installedElement = document.getElementById('service-installed');
            
            if (serviceData.error) {
                statusElement.innerHTML = '<span class="status-indicator status-error"></span>Error';
                serviceStatusElement.textContent = 'Error';
                installedElement.textContent = 'Error';
            } else {
                const serviceStatus = serviceData.status || 'Unknown';
                const isInstalled = serviceData.installed || false;
                
                let statusClass = 'status-unknown';
                if (serviceStatus === 'Running') statusClass = 'status-healthy';
                else if (serviceStatus === 'Stopped') statusClass = 'status-warning';
                else if (serviceStatus === 'Error') statusClass = 'status-error';
                
                statusElement.innerHTML = `<span class="status-indicator ${statusClass}"></span>${serviceStatus}`;
                serviceStatusElement.textContent = serviceStatus;
                installedElement.textContent = isInstalled ? 'Yes' : 'No';
            }
        }
        
        // Create backup
        async function createBackup(type) {
            try {
                const response = await fetch('/api/backup/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ type: type })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    alert(`Backup created successfully: ${type}`);
                    loadDashboardData();
                } else {
                    alert(`Backup failed: ${result.error || 'Unknown error'}`);
                }
                
            } catch (error) {
                console.error('Error creating backup:', error);
                alert('Error creating backup');
            }
        }
        
        // Clear alerts
        async function clearAlerts() {
            try {
                const response = await fetch('/api/monitoring/clear_alerts', {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    alert('Alerts cleared successfully');
                    loadDashboardData();
                } else {
                    alert(`Failed to clear alerts: ${result.error || 'Unknown error'}`);
                }
                
            } catch (error) {
                console.error('Error clearing alerts:', error);
                alert('Error clearing alerts');
            }
        }
        
        // Control service
        async function controlService(action) {
            try {
                const response = await fetch('/api/service/control', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ action: action })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    alert(`Service ${action} successful: ${result.message}`);
                    loadDashboardData();
                } else {
                    alert(`Service ${action} failed: ${result.error || 'Unknown error'}`);
                }
                
            } catch (error) {
                console.error('Error controlling service:', error);
                alert('Error controlling service');
            }
        }
        
        // Perform health check
        async function performHealthCheck() {
            try {
                const response = await fetch('/api/health');
                const result = await response.json();
                
                if (result.error) {
                    alert(`Health check failed: ${result.error}`);
                } else {
                    alert(`Health check completed. Status: ${result.integration_status || 'Unknown'}`);
                }
                
            } catch (error) {
                console.error('Error performing health check:', error);
                alert('Error performing health check');
            }
        }
        
        // Refresh functions
        function refreshMonitoring() {
            loadDashboardData();
        }
        
        function refreshIntegration() {
            loadDashboardData();
        }
        
        // Start auto refresh
        function startAutoRefresh() {
            refreshInterval = setInterval(loadDashboardData, 30000); // 30 seconds
        }
        
        // Stop auto refresh
        function stopAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        }
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', stopAutoRefresh);
    </script>
</body>
</html>
        """
        
        template_file = self.project_root / "templates" / "enhanced_dashboard.html"
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            self.logger.info("Enhanced dashboard template created")
        except Exception as e:
            self.logger.error(f"Error creating dashboard template: {e}")

def main():
    """Main function"""
    dashboard = EnhancedDashboard()
    dashboard.start_dashboard()

if __name__ == "__main__":
    main() 