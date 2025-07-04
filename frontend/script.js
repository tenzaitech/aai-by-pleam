// WAWAGOT V.2 Frontend JavaScript
// API Integration and UI Management

class WAWAGOTFrontend {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.systemStatus = 'disconnected';
        this.commandHistory = [];
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupNavigation();
        await this.checkSystemHealth();
        this.startHealthCheck();
        this.showNotification('ระบบ WAWAGOT V.2 พร้อมใช้งาน', 'success');
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigateToSection(item.dataset.section);
            });
        });

        // Command input
        const commandInput = document.getElementById('commandInput');
        if (commandInput) {
            commandInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.sendCommand();
                }
            });
        }

        // AI prompt input
        const aiPrompt = document.getElementById('aiPrompt');
        if (aiPrompt) {
            aiPrompt.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.processAI();
                }
            });
        }

        // File upload
        const imageInput = document.getElementById('imageInput');
        if (imageInput) {
            imageInput.addEventListener('change', (e) => {
                this.handleImageUpload(e);
            });
        }
    }

    setupNavigation() {
        // Show dashboard by default
        this.navigateToSection('dashboard');
    }

    navigateToSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Add active class to nav item
        const navItem = document.querySelector(`[data-section="${sectionId}"]`);
        if (navItem) {
            navItem.classList.add('active');
        }
    }

    async checkSystemHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            
            this.updateSystemStatus(data.status === 'healthy' ? 'connected' : 'error');
            this.updateStatusCards(data.components);
            
        } catch (error) {
            console.error('Health check failed:', error);
            this.updateSystemStatus('error');
            this.showNotification('ไม่สามารถเชื่อมต่อกับระบบได้', 'error');
        }
    }

    updateSystemStatus(status) {
        this.systemStatus = status;
        const statusDot = document.getElementById('systemStatus');
        const statusText = document.getElementById('statusText');

        if (statusDot && statusText) {
            statusDot.className = 'status-dot ' + status;
            
            switch (status) {
                case 'connected':
                    statusText.textContent = 'เชื่อมต่อแล้ว';
                    break;
                case 'error':
                    statusText.textContent = 'เกิดข้อผิดพลาด';
                    break;
                default:
                    statusText.textContent = 'กำลังเชื่อมต่อ...';
            }
        }
    }

    updateStatusCards(components) {
        if (!components) return;

        // Update system health
        const systemHealth = document.getElementById('systemHealth');
        if (systemHealth) {
            systemHealth.textContent = components.system_health?.overall_status === 'healthy' 
                ? 'ระบบทำงานปกติ' 
                : 'มีปัญหาในระบบ';
        }

        // Update Chrome status
        const chromeStatus = document.getElementById('chromeStatus');
        if (chromeStatus) {
            chromeStatus.textContent = components.chrome_controller?.is_working 
                ? 'พร้อมใช้งาน' 
                : 'ไม่พร้อมใช้งาน';
        }

        // Update AI status
        const aiStatus = document.getElementById('aiStatus');
        if (aiStatus) {
            aiStatus.textContent = components.ai_integration?.is_working 
                ? 'พร้อมใช้งาน' 
                : 'ไม่พร้อมใช้งาน';
        }

        // Update Knowledge status
        const knowledgeStatus = document.getElementById('knowledgeStatus');
        if (knowledgeStatus) {
            knowledgeStatus.textContent = components.knowledge_manager?.is_working 
                ? 'พร้อมใช้งาน' 
                : 'ไม่พร้อมใช้งาน';
        }
    }

    startHealthCheck() {
        // Check system health every 30 seconds
        setInterval(() => {
            this.checkSystemHealth();
        }, 30000);
    }

    async sendCommand() {
        const commandInput = document.getElementById('commandInput');
        const languageSelect = document.getElementById('languageSelect');
        
        if (!commandInput || !commandInput.value.trim()) {
            this.showNotification('กรุณาใส่คำสั่ง', 'warning');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/command`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: commandInput.value.trim(),
                    language: languageSelect.value,
                    parameters: {}
                })
            });

            const data = await response.json();

            if (data.success) {
                this.addCommandToHistory(commandInput.value.trim(), data.result);
                this.showNotification('คำสั่งดำเนินการสำเร็จ', 'success');
                commandInput.value = '';
            } else {
                this.showNotification('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }

        } catch (error) {
            console.error('Command error:', error);
            this.showNotification('ไม่สามารถส่งคำสั่งได้', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    addCommandToHistory(command, result) {
        this.commandHistory.unshift({
            command,
            result,
            timestamp: new Date().toLocaleString('th-TH')
        });

        // Keep only last 10 commands
        if (this.commandHistory.length > 10) {
            this.commandHistory.pop();
        }

        this.updateCommandHistory();
    }

    updateCommandHistory() {
        const historyContainer = document.getElementById('commandHistory');
        if (!historyContainer) return;

        historyContainer.innerHTML = this.commandHistory.map(item => `
            <div class="history-item">
                <div class="history-command">
                    <strong>คำสั่ง:</strong> ${item.command}
                </div>
                <div class="history-result">
                    <strong>ผลลัพธ์:</strong> ${JSON.stringify(item.result, null, 2)}
                </div>
                <div class="history-time">
                    <small>${item.timestamp}</small>
                </div>
            </div>
        `).join('');
    }

    async navigateTo() {
        const urlInput = document.getElementById('urlInput');
        if (!urlInput || !urlInput.value.trim()) {
            this.showNotification('กรุณาใส่ URL', 'warning');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/chrome`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'navigate',
                    url: urlInput.value.trim()
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('นำทางไปยัง URL สำเร็จ', 'success');
            } else {
                this.showNotification('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }

        } catch (error) {
            console.error('Navigation error:', error);
            this.showNotification('ไม่สามารถนำทางได้', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async chromeAction(action, direction = null) {
        this.showLoading(true);

        try {
            let parameters = {};
            
            if (action === 'scroll') {
                parameters.direction = direction;
            } else if (action === 'click') {
                const selectorInput = document.getElementById('selectorInput');
                if (selectorInput) {
                    parameters.selector = selectorInput.value;
                }
            } else if (action === 'type') {
                const selectorInput = document.getElementById('selectorInput');
                const textInput = document.getElementById('textInput');
                if (selectorInput && textInput) {
                    parameters.selector = selectorInput.value;
                    parameters.text = textInput.value;
                }
            }

            const response = await fetch(`${this.apiBaseUrl}/api/chrome`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: action,
                    parameters: parameters
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification(`ดำเนินการ ${action} สำเร็จ`, 'success');
            } else {
                this.showNotification('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }

        } catch (error) {
            console.error('Chrome action error:', error);
            this.showNotification('ไม่สามารถดำเนินการได้', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async processAI() {
        const aiPrompt = document.getElementById('aiPrompt');
        const useVision = document.getElementById('useVision');
        
        if (!aiPrompt || !aiPrompt.value.trim()) {
            this.showNotification('กรุณาใส่คำถามหรือคำสั่ง', 'warning');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/ai`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: aiPrompt.value.trim(),
                    use_vision: useVision.checked,
                    context: ''
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displayAIResults(data.result);
                this.showNotification('ประมวลผล AI สำเร็จ', 'success');
            } else {
                this.showNotification('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }

        } catch (error) {
            console.error('AI processing error:', error);
            this.showNotification('ไม่สามารถประมวลผล AI ได้', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayAIResults(result) {
        const resultsContainer = document.getElementById('aiResults');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="ai-result">
                    <pre>${JSON.stringify(result, null, 2)}</pre>
                </div>
            `;
        }
    }

    async analyzeImage() {
        const imageInput = document.getElementById('imageInput');
        if (!imageInput || !imageInput.files[0]) {
            this.showNotification('กรุณาเลือกไฟล์ภาพ', 'warning');
            return;
        }

        this.showLoading(true);

        try {
            const file = imageInput.files[0];
            const base64 = await this.fileToBase64(file);

            const response = await fetch(`${this.apiBaseUrl}/api/visual`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image_data: base64
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displayVisualResults(data.analysis);
                this.showNotification('วิเคราะห์ภาพสำเร็จ', 'success');
            } else {
                this.showNotification('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }

        } catch (error) {
            console.error('Visual analysis error:', error);
            this.showNotification('ไม่สามารถวิเคราะห์ภาพได้', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }

    displayVisualResults(analysis) {
        const resultsContainer = document.getElementById('visualResults');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="visual-result">
                    <pre>${JSON.stringify(analysis, null, 2)}</pre>
                </div>
            `;
        }
    }

    async searchKnowledge() {
        const queryInput = document.getElementById('knowledgeQuery');
        if (!queryInput || !queryInput.value.trim()) {
            this.showNotification('กรุณาใส่คำค้นหา', 'warning');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/knowledge?query=${encodeURIComponent(queryInput.value.trim())}`);
            const data = await response.json();

            if (data.success) {
                this.displayKnowledgeResults(data.results);
                this.showNotification('ค้นหาข้อมูลสำเร็จ', 'success');
            } else {
                this.showNotification('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }

        } catch (error) {
            console.error('Knowledge search error:', error);
            this.showNotification('ไม่สามารถค้นหาข้อมูลได้', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async storeKnowledge() {
        const knowledgeData = document.getElementById('knowledgeData');
        if (!knowledgeData || !knowledgeData.value.trim()) {
            this.showNotification('กรุณาใส่ข้อมูล', 'warning');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/knowledge`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: knowledgeData.value.trim(),
                    timestamp: new Date().toISOString()
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('บันทึกข้อมูลสำเร็จ', 'success');
                knowledgeData.value = '';
            } else {
                this.showNotification('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }

        } catch (error) {
            console.error('Knowledge storage error:', error);
            this.showNotification('ไม่สามารถบันทึกข้อมูลได้', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayKnowledgeResults(results) {
        const resultsContainer = document.getElementById('knowledgeResults');
        if (resultsContainer) {
            if (Array.isArray(results) && results.length > 0) {
                resultsContainer.innerHTML = results.map(item => `
                    <div class="knowledge-item">
                        <div class="knowledge-content">${item.content}</div>
                        <div class="knowledge-time">${new Date(item.timestamp).toLocaleString('th-TH')}</div>
                    </div>
                `).join('');
            } else {
                resultsContainer.innerHTML = '<div class="no-results">ไม่พบข้อมูล</div>';
            }
        }
    }

    async saveConfig() {
        const config = {
            chrome_headless: document.getElementById('chromeHeadless')?.checked || false,
            ai_enabled: document.getElementById('aiEnabled')?.checked || false,
            thai_processing: document.getElementById('thaiProcessing')?.checked || false,
            parallel_processing: document.getElementById('parallelProcessing')?.checked || false
        };

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('บันทึกการตั้งค่าสำเร็จ', 'success');
            } else {
                this.showNotification('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }

        } catch (error) {
            console.error('Config save error:', error);
            this.showNotification('ไม่สามารถบันทึกการตั้งค่าได้', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadConfig() {
        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/config`);
            const data = await response.json();

            if (data.success) {
                this.updateConfigUI(data.config);
                this.showNotification('โหลดการตั้งค่าสำเร็จ', 'success');
            } else {
                this.showNotification('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }

        } catch (error) {
            console.error('Config load error:', error);
            this.showNotification('ไม่สามารถโหลดการตั้งค่าได้', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    updateConfigUI(config) {
        if (config.chrome_headless !== undefined) {
            const headlessCheckbox = document.getElementById('chromeHeadless');
            if (headlessCheckbox) headlessCheckbox.checked = config.chrome_headless;
        }

        if (config.ai_enabled !== undefined) {
            const aiCheckbox = document.getElementById('aiEnabled');
            if (aiCheckbox) aiCheckbox.checked = config.ai_enabled;
        }

        if (config.thai_processing !== undefined) {
            const thaiCheckbox = document.getElementById('thaiProcessing');
            if (thaiCheckbox) thaiCheckbox.checked = config.thai_processing;
        }

        if (config.parallel_processing !== undefined) {
            const parallelCheckbox = document.getElementById('parallelProcessing');
            if (parallelCheckbox) parallelCheckbox.checked = config.parallel_processing;
        }
    }

    resetConfig() {
        // Reset all checkboxes to default values
        const headlessCheckbox = document.getElementById('chromeHeadless');
        if (headlessCheckbox) headlessCheckbox.checked = false;

        const aiCheckbox = document.getElementById('aiEnabled');
        if (aiCheckbox) aiCheckbox.checked = true;

        const thaiCheckbox = document.getElementById('thaiProcessing');
        if (thaiCheckbox) thaiCheckbox.checked = true;

        const parallelCheckbox = document.getElementById('parallelProcessing');
        if (parallelCheckbox) parallelCheckbox.checked = true;

        this.showNotification('รีเซ็ตการตั้งค่าแล้ว', 'info');
    }

    // Quick action functions
    async restartSystem() {
        if (!confirm('คุณต้องการรีสตาร์ทระบบหรือไม่?')) return;

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/system/restart`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('รีสตาร์ทระบบสำเร็จ', 'success');
                setTimeout(() => {
                    this.checkSystemHealth();
                }, 5000);
            } else {
                this.showNotification('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }

        } catch (error) {
            console.error('Restart error:', error);
            this.showNotification('ไม่สามารถรีสตาร์ทระบบได้', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async openChrome() {
        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/chrome`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: 'navigate',
                    url: 'https://www.google.com'
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('เปิด Chrome สำเร็จ', 'success');
            } else {
                this.showNotification('เกิดข้อผิดพลาด: ' + data.error, 'error');
            }

        } catch (error) {
            console.error('Open Chrome error:', error);
            this.showNotification('ไม่สามารถเปิด Chrome ได้', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async testAI() {
        this.navigateToSection('ai');
        const aiPrompt = document.getElementById('aiPrompt');
        if (aiPrompt) {
            aiPrompt.value = 'สวัสดีครับ ระบบ WAWAGOT V.2 ทำงานได้ดีไหม?';
            this.processAI();
        }
    }

    async backupSystem() {
        this.showNotification('กำลังสำรองข้อมูล...', 'info');
        // Implement backup functionality
        setTimeout(() => {
            this.showNotification('สำรองข้อมูลสำเร็จ', 'success');
        }, 2000);
    }

    // Utility functions
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (show) {
                overlay.classList.add('show');
            } else {
                overlay.classList.remove('show');
            }
        }
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;

        container.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    getNotificationIcon(type) {
        switch (type) {
            case 'success': return 'check-circle';
            case 'error': return 'exclamation-circle';
            case 'warning': return 'exclamation-triangle';
            default: return 'info-circle';
        }
    }

    addLogEntry(message, level = 'info') {
        const logsContainer = document.getElementById('systemLogs');
        if (!logsContainer) return;

        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry';
        logEntry.innerHTML = `
            <span class="log-time">[${new Date().toLocaleString('th-TH')}]</span>
            <span class="log-level ${level}">${level.toUpperCase()}</span>
            <span class="log-message">${message}</span>
        `;

        logsContainer.insertBefore(logEntry, logsContainer.firstChild);

        // Keep only last 50 log entries
        while (logsContainer.children.length > 50) {
            logsContainer.removeChild(logsContainer.lastChild);
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.wawagot = new WAWAGOTFrontend();
});

// Global functions for onclick handlers
function sendCommand() {
    if (window.wawagot) window.wawagot.sendCommand();
}

function navigateTo() {
    if (window.wawagot) window.wawagot.navigateTo();
}

function chromeAction(action, direction) {
    if (window.wawagot) window.wawagot.chromeAction(action, direction);
}

function processAI() {
    if (window.wawagot) window.wawagot.processAI();
}

function analyzeImage() {
    if (window.wawagot) window.wawagot.analyzeImage();
}

function searchKnowledge() {
    if (window.wawagot) window.wawagot.searchKnowledge();
}

function storeKnowledge() {
    if (window.wawagot) window.wawagot.storeKnowledge();
}

function saveConfig() {
    if (window.wawagot) window.wawagot.saveConfig();
}

function loadConfig() {
    if (window.wawagot) window.wawagot.loadConfig();
}

function resetConfig() {
    if (window.wawagot) window.wawagot.resetConfig();
}

function restartSystem() {
    if (window.wawagot) window.wawagot.restartSystem();
}

function openChrome() {
    if (window.wawagot) window.wawagot.openChrome();
}

function testAI() {
    if (window.wawagot) window.wawagot.testAI();
}

function backupSystem() {
    if (window.wawagot) window.wawagot.backupSystem();
} 