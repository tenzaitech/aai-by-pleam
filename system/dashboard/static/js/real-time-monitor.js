/**
 * Real-time Monitor - JavaScript สำหรับ real-time monitoring
 * จัดการการแสดงผล log, workflow, performance และ alerts แบบ real-time
 */

class RealTimeMonitor {
    constructor() {
        this.apiBase = '/api/logging';
        this.websocket = null;
        this.updateInterval = null;
        this.isConnected = false;
        
        // DOM elements
        this.logContainer = document.getElementById('log-container');
        this.workflowContainer = document.getElementById('workflow-container');
        this.performanceContainer = document.getElementById('performance-container');
        this.alertContainer = document.getElementById('alert-container');
        this.statusIndicator = document.getElementById('status-indicator');
        this.resetStatusPopup = document.getElementById('reset-status-popup');
        
        // Data buffers
        this.logBuffer = [];
        this.workflowBuffer = [];
        this.performanceBuffer = [];
        this.alertBuffer = [];
        
        // Configuration
        this.config = {
            maxLogs: 1000,
            maxWorkflows: 100,
            maxPerformance: 200,
            maxAlerts: 50,
            updateInterval: 5000, // 5 seconds
            logRetention: 24 // hours
        };
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Initializing Real-time Monitor...');
        
        // เริ่ม WebSocket connection
        this.connectWebSocket();
        
        // เริ่ม periodic updates
        this.startPeriodicUpdates();
        
        // โหลดข้อมูลเริ่มต้น
        await this.loadInitialData();
        
        // ตั้งค่า event listeners
        this.setupEventListeners();
        
        console.log('✅ Real-time Monitor initialized');
    }
    
    connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}${this.apiBase}/ws`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('🔗 WebSocket connected');
                this.isConnected = true;
                this.updateStatusIndicator('connected');
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('❌ Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('🔌 WebSocket disconnected');
                this.isConnected = false;
                this.updateStatusIndicator('disconnected');
                
                // Reconnect after 5 seconds
                setTimeout(() => this.connectWebSocket(), 5000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                this.updateStatusIndicator('error');
            };
            
        } catch (error) {
            console.error('❌ Error connecting WebSocket:', error);
            this.updateStatusIndicator('error');
        }
    }
    
    handleWebSocketMessage(data) {
        if (data.type === 'real_time_update') {
            this.updateDashboardStats(data);
        }
    }
    
    startPeriodicUpdates() {
        this.updateInterval = setInterval(() => {
            this.updateAllData();
        }, this.config.updateInterval);
    }
    
    async loadInitialData() {
        try {
            console.log('📊 Loading initial data...');
            
            // โหลดข้อมูลพร้อมกัน
            const [logs, workflows, performance, alerts, resetStatus] = await Promise.all([
                this.fetchLogs(),
                this.fetchWorkflows(),
                this.fetchPerformance(),
                this.fetchAlerts(),
                this.fetchResetStatus()
            ]);
            
            // อัปเดต UI
            this.updateLogDisplay(logs);
            this.updateWorkflowDisplay(workflows);
            this.updatePerformanceDisplay(performance);
            this.updateAlertDisplay(alerts);
            this.updateResetStatus(resetStatus);
            
            console.log('✅ Initial data loaded');
            
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
        }
    }
    
    async updateAllData() {
        try {
            const [logs, workflows, performance, alerts] = await Promise.all([
                this.fetchLogs(),
                this.fetchWorkflows(),
                this.fetchPerformance(),
                this.fetchAlerts()
            ]);
            
            this.updateLogDisplay(logs);
            this.updateWorkflowDisplay(workflows);
            this.updatePerformanceDisplay(performance);
            this.updateAlertDisplay(alerts);
            
        } catch (error) {
            console.error('❌ Error updating data:', error);
        }
    }
    
    async fetchLogs(limit = 100, module = null, level = null) {
        try {
            let url = `${this.apiBase}/logs/recent?limit=${limit}`;
            if (module) url += `&module=${module}`;
            if (level) url += `&level=${level}`;
            
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            return data.logs || [];
            
        } catch (error) {
            console.error('❌ Error fetching logs:', error);
            return [];
        }
    }
    
    async fetchWorkflows() {
        try {
            const [active, history] = await Promise.all([
                fetch(`${this.apiBase}/workflows/active`),
                fetch(`${this.apiBase}/workflows/history?limit=20`)
            ]);
            
            const activeData = await active.json();
            const historyData = await history.json();
            
            return {
                active: activeData.workflows || [],
                history: historyData.workflows || []
            };
            
        } catch (error) {
            console.error('❌ Error fetching workflows:', error);
            return { active: [], history: [] };
        }
    }
    
    async fetchPerformance() {
        try {
            const [metrics, summary] = await Promise.all([
                fetch(`${this.apiBase}/performance/metrics?hours=1`),
                fetch(`${this.apiBase}/performance/summary`)
            ]);
            
            const metricsData = await metrics.json();
            const summaryData = await summary.json();
            
            return {
                metrics: metricsData,
                summary: summaryData.summary || {}
            };
            
        } catch (error) {
            console.error('❌ Error fetching performance:', error);
            return { metrics: {}, summary: {} };
        }
    }
    
    async fetchAlerts() {
        try {
            const [active, summary] = await Promise.all([
                fetch(`${this.apiBase}/alerts/active`),
                fetch(`${this.apiBase}/alerts/summary`)
            ]);
            
            const activeData = await active.json();
            const summaryData = await summary.json();
            
            return {
                active: activeData.alerts || [],
                summary: summaryData.summary || {}
            };
            
        } catch (error) {
            console.error('❌ Error fetching alerts:', error);
            return { active: [], summary: {} };
        }
    }
    
    async fetchResetStatus() {
        try {
            const response = await fetch(`${this.apiBase}/reset/status`);
            const data = await response.json();
            return data.reset_status || {};
            
        } catch (error) {
            console.error('❌ Error fetching reset status:', error);
            return {};
        }
    }
    
    updateLogDisplay(logs) {
        if (!this.logContainer) return;
        
        // อัปเดต buffer
        this.logBuffer = logs.slice(0, this.config.maxLogs);
        
        // สร้าง HTML
        const html = this.logBuffer.map(log => this.createLogEntry(log)).join('');
        
        // อัปเดต DOM
        this.logContainer.innerHTML = html;
        
        // Auto-scroll to bottom
        this.logContainer.scrollTop = this.logContainer.scrollHeight;
    }
    
    createLogEntry(log) {
        const timestamp = new Date(log.timestamp).toLocaleTimeString();
        const levelClass = this.getLevelClass(log.level);
        const moduleBadge = log.module ? `<span class="badge badge-secondary">${log.module}</span>` : '';
        const workflowBadge = log.workflow_id ? `<span class="badge badge-info">${log.workflow_id.slice(0, 8)}</span>` : '';
        
        return `
            <div class="log-entry ${levelClass}">
                <div class="log-header">
                    <span class="log-timestamp">${timestamp}</span>
                    <span class="log-level ${levelClass}">${log.level.toUpperCase()}</span>
                    ${moduleBadge}
                    ${workflowBadge}
                </div>
                <div class="log-message">${this.escapeHtml(log.message)}</div>
                ${log.duration_ms ? `<div class="log-duration">Duration: ${log.duration_ms}ms</div>` : ''}
            </div>
        `;
    }
    
    updateWorkflowDisplay(workflows) {
        if (!this.workflowContainer) return;
        
        this.workflowBuffer = workflows;
        
        // สร้าง HTML สำหรับ active workflows
        const activeHtml = workflows.active.map(workflow => this.createWorkflowEntry(workflow)).join('');
        
        // สร้าง HTML สำหรับ workflow history
        const historyHtml = workflows.history.map(workflow => this.createWorkflowHistoryEntry(workflow)).join('');
        
        // อัปเดต DOM
        const activeSection = this.workflowContainer.querySelector('.active-workflows');
        const historySection = this.workflowContainer.querySelector('.workflow-history');
        
        if (activeSection) activeSection.innerHTML = activeHtml;
        if (historySection) historySection.innerHTML = historyHtml;
    }
    
    createWorkflowEntry(workflow) {
        const startTime = new Date(workflow.start_time).toLocaleTimeString();
        const statusClass = this.getWorkflowStatusClass(workflow.status);
        const progress = workflow.progress_percentage || 0;
        
        return `
            <div class="workflow-entry ${statusClass}">
                <div class="workflow-header">
                    <span class="workflow-id">${workflow.workflow_id.slice(0, 12)}...</span>
                    <span class="workflow-type">${workflow.workflow_type}</span>
                    <span class="workflow-status ${statusClass}">${workflow.status}</span>
                </div>
                <div class="workflow-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <span class="progress-text">${progress.toFixed(1)}%</span>
                </div>
                <div class="workflow-stats">
                    <span>Steps: ${workflow.completed_steps}/${workflow.total_steps}</span>
                    <span>Started: ${startTime}</span>
                </div>
            </div>
        `;
    }
    
    createWorkflowHistoryEntry(workflow) {
        const startTime = new Date(workflow.start_time).toLocaleTimeString();
        const endTime = workflow.end_time ? new Date(workflow.end_time).toLocaleTimeString() : 'Running';
        const duration = workflow.total_duration_ms ? `${(workflow.total_duration_ms / 1000).toFixed(1)}s` : 'N/A';
        const statusClass = this.getWorkflowStatusClass(workflow.status);
        
        return `
            <div class="workflow-history-entry ${statusClass}">
                <div class="workflow-history-header">
                    <span class="workflow-type">${workflow.workflow_type}</span>
                    <span class="workflow-status ${statusClass}">${workflow.status}</span>
                </div>
                <div class="workflow-history-details">
                    <span>Duration: ${duration}</span>
                    <span>Steps: ${workflow.completed_steps}/${workflow.total_steps}</span>
                </div>
                <div class="workflow-history-time">
                    <span>Start: ${startTime}</span>
                    <span>End: ${endTime}</span>
                </div>
            </div>
        `;
    }
    
    updatePerformanceDisplay(performance) {
        if (!this.performanceContainer) return;
        
        this.performanceBuffer = performance;
        
        // อัปเดต summary
        const summary = performance.summary;
        if (summary) {
            this.updatePerformanceSummary(summary);
        }
        
        // อัปเดต charts (ถ้ามี)
        this.updatePerformanceCharts(performance.metrics);
    }
    
    updatePerformanceSummary(summary) {
        const current = summary.current || {};
        const average = summary.average_1h || {};
        
        // อัปเดต current metrics
        this.updateMetric('cpu-current', current.cpu_percent || 0, '%');
        this.updateMetric('memory-current', current.memory_percent || 0, '%');
        this.updateMetric('disk-current', current.disk_usage_percent || 0, '%');
        this.updateMetric('processes-current', current.active_processes || 0, '');
        
        // อัปเดต average metrics
        this.updateMetric('cpu-average', average.cpu_percent || 0, '%');
        this.updateMetric('memory-average', average.memory_percent || 0, '%');
        this.updateMetric('disk-average', average.disk_usage_percent || 0, '%');
        
        // อัปเดต alerts
        this.updateMetric('alerts-total', summary.alerts_count || 0, '');
        this.updateMetric('alerts-critical', summary.critical_alerts || 0, '');
        this.updateMetric('alerts-warning', summary.warning_alerts || 0, '');
    }
    
    updateMetric(elementId, value, unit) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = `${value.toFixed(1)}${unit}`;
            
            // เพิ่ม CSS class ตามค่า
            element.className = element.className.replace(/metric-\w+/g, '');
            if (value > 80) element.classList.add('metric-high');
            else if (value > 60) element.classList.add('metric-medium');
            else element.classList.add('metric-low');
        }
    }
    
    updatePerformanceCharts(metrics) {
        // สร้าง charts สำหรับ performance metrics
        // (สามารถใช้ Chart.js หรือ library อื่นๆ ได้)
        console.log('📊 Updating performance charts:', metrics);
    }
    
    updateAlertDisplay(alerts) {
        if (!this.alertContainer) return;
        
        this.alertBuffer = alerts;
        
        // สร้าง HTML สำหรับ active alerts
        const activeHtml = alerts.active.map(alert => this.createAlertEntry(alert)).join('');
        
        // อัปเดต DOM
        this.alertContainer.innerHTML = activeHtml;
        
        // อัปเดต alert counter
        this.updateAlertCounter(alerts.summary);
    }
    
    createAlertEntry(alert) {
        const timestamp = new Date(alert.timestamp).toLocaleTimeString();
        const severityClass = this.getAlertSeverityClass(alert.severity);
        const moduleBadge = alert.module ? `<span class="badge badge-secondary">${alert.module}</span>` : '';
        
        return `
            <div class="alert-entry ${severityClass}">
                <div class="alert-header">
                    <span class="alert-severity ${severityClass}">${alert.severity.toUpperCase()}</span>
                    <span class="alert-type">${alert.type}</span>
                    ${moduleBadge}
                    <span class="alert-timestamp">${timestamp}</span>
                </div>
                <div class="alert-title">${this.escapeHtml(alert.title)}</div>
                <div class="alert-message">${this.escapeHtml(alert.message)}</div>
                <div class="alert-actions">
                    ${!alert.acknowledged ? `<button class="btn btn-sm btn-primary" onclick="monitor.acknowledgeAlert('${alert.id}')">Acknowledge</button>` : ''}
                    <button class="btn btn-sm btn-secondary" onclick="monitor.dismissAlert('${alert.id}')">Dismiss</button>
                </div>
            </div>
        `;
    }
    
    updateAlertCounter(summary) {
        const totalElement = document.getElementById('alert-total');
        const criticalElement = document.getElementById('alert-critical');
        const warningElement = document.getElementById('alert-warning');
        
        if (totalElement) totalElement.textContent = summary.total_active || 0;
        if (criticalElement) criticalElement.textContent = summary.critical_alerts || 0;
        if (warningElement) warningElement.textContent = summary.warning_alerts || 0;
    }
    
    updateResetStatus(resetStatus) {
        if (!this.resetStatusPopup) return;
        
        const lastReset = new Date(resetStatus.last_reset_time || Date.now()).toLocaleString();
        const status = resetStatus.reset_status || 'unknown';
        
        this.resetStatusPopup.innerHTML = `
            <div class="reset-status-content">
                <h4>Log Reset Status</h4>
                <p><strong>Last Reset:</strong> ${lastReset}</p>
                <p><strong>Status:</strong> <span class="status-${status}">${status}</span></p>
                <p><strong>Retention:</strong> ${resetStatus.retention_days || 1} day(s)</p>
                <button class="btn btn-primary" onclick="monitor.cleanupLogs()">Cleanup Now</button>
            </div>
        `;
    }
    
    updateDashboardStats(data) {
        // อัปเดต statistics แบบ real-time
        const statsContainer = document.getElementById('dashboard-stats');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="stat-item">
                    <span class="stat-label">Logs</span>
                    <span class="stat-value">${data.logs_count}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Active Workflows</span>
                    <span class="stat-value">${data.active_workflows}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Active Alerts</span>
                    <span class="stat-value">${data.active_alerts}</span>
                </div>
            `;
        }
    }
    
    updateStatusIndicator(status) {
        if (!this.statusIndicator) return;
        
        this.statusIndicator.className = `status-indicator status-${status}`;
        this.statusIndicator.title = `Connection: ${status}`;
    }
    
    async acknowledgeAlert(alertId) {
        try {
            const response = await fetch(`${this.apiBase}/alerts/${alertId}/acknowledge`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user: 'dashboard' })
            });
            
            if (response.ok) {
                // อัปเดต UI
                await this.updateAllData();
                this.showNotification('Alert acknowledged successfully', 'success');
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Error acknowledging alert:', error);
            this.showNotification('Failed to acknowledge alert', 'error');
        }
    }
    
    async dismissAlert(alertId) {
        try {
            const response = await fetch(`${this.apiBase}/alerts/${alertId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user: 'dashboard' })
            });
            
            if (response.ok) {
                // อัปเดต UI
                await this.updateAllData();
                this.showNotification('Alert dismissed successfully', 'success');
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Error dismissing alert:', error);
            this.showNotification('Failed to dismiss alert', 'error');
        }
    }
    
    async cleanupLogs() {
        try {
            const response = await fetch(`${this.apiBase}/reset/cleanup`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showNotification('Log cleanup completed', 'success');
                // อัปเดต reset status
                const resetStatus = await this.fetchResetStatus();
                this.updateResetStatus(resetStatus);
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            
        } catch (error) {
            console.error('❌ Error cleaning up logs:', error);
            this.showNotification('Failed to cleanup logs', 'error');
        }
    }
    
    setupEventListeners() {
        // Filter controls
        const logLevelFilter = document.getElementById('log-level-filter');
        const moduleFilter = document.getElementById('module-filter');
        
        if (logLevelFilter) {
            logLevelFilter.addEventListener('change', async (e) => {
                const level = e.target.value;
                const logs = await this.fetchLogs(100, null, level || null);
                this.updateLogDisplay(logs);
            });
        }
        
        if (moduleFilter) {
            moduleFilter.addEventListener('change', async (e) => {
                const module = e.target.value;
                const logs = await this.fetchLogs(100, module || null, null);
                this.updateLogDisplay(logs);
            });
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.updateAllData();
                this.showNotification('Data refreshed', 'info');
            });
        }
        
        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startPeriodicUpdates();
                } else {
                    this.stopPeriodicUpdates();
                }
            });
        }
    }
    
    stopPeriodicUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    showNotification(message, type = 'info') {
        // สร้าง notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">&times;</button>
        `;
        
        // เพิ่มในหน้า
        document.body.appendChild(notification);
        
        // ลบหลังจาก 3 วินาที
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }
    
    // Utility functions
    getLevelClass(level) {
        const levelMap = {
            'debug': 'level-debug',
            'info': 'level-info',
            'warning': 'level-warning',
            'error': 'level-error',
            'critical': 'level-critical'
        };
        return levelMap[level.toLowerCase()] || 'level-info';
    }
    
    getWorkflowStatusClass(status) {
        const statusMap = {
            'pending': 'status-pending',
            'running': 'status-running',
            'completed': 'status-completed',
            'failed': 'status-failed',
            'cancelled': 'status-cancelled'
        };
        return statusMap[status.toLowerCase()] || 'status-unknown';
    }
    
    getAlertSeverityClass(severity) {
        const severityMap = {
            'info': 'severity-info',
            'warning': 'severity-warning',
            'error': 'severity-error',
            'critical': 'severity-critical'
        };
        return severityMap[severity.toLowerCase()] || 'severity-info';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    destroy() {
        // Cleanup
        this.stopPeriodicUpdates();
        
        if (this.websocket) {
            this.websocket.close();
        }
        
        console.log('🧹 Real-time Monitor destroyed');
    }
}

// Global instance
let monitor = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    monitor = new RealTimeMonitor();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (monitor) {
        monitor.destroy();
    }
}); 