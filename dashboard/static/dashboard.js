// WAWA AI System Dashboard JavaScript
// Real-time System Monitoring & Control

let socket = null;
let currentGodModeSession = null;
let updateInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 WAWA AI Dashboard initializing...');
    
    // Debug: Check if capability cards exist
    console.log('🔍 Checking capability cards in DOM...');
    const capabilityKeys = [
        'chrome_automation', 'ai_integration', 'thai_processor', 'visual_recognition',
        'backup_controller', 'supabase_integration', 'environment_cards', 'knowledge_manager',
        'godmode_knowledge', 'gpu_processing', 'smart_allocator'
    ];
    
    capabilityKeys.forEach(key => {
        const card = document.getElementById(`capability-${key}`);
        if (card) {
            console.log(`✅ Found card: capability-${key}`);
        } else {
            console.warn(`❌ Missing card: capability-${key}`);
        }
    });
    
    // Initialize Socket.IO connection
    initializeSocketIO();
    
    // Load initial data
    loadSystemStatus();
    loadGodModeData();
    loadLogs();
    
    // Start real-time updates
    startRealTimeUpdates();
    
    // Set up event listeners
    setupEventListeners();
    
    console.log('✅ Dashboard initialized successfully');
});

// Initialize Socket.IO connection
function initializeSocketIO() {
    try {
        // Check if socket already exists
        if (socket) {
            socket.disconnect();
        }
        
        socket = io();
        
        socket.on('connect', function() {
            console.log('🔗 Connected to dashboard server');
            addLogEntry({
                level: 'info',
                message: 'Connected to dashboard server',
                timestamp: new Date().toISOString()
            });
        });
        
        socket.on('disconnect', function() {
            console.log('🔌 Disconnected from dashboard server');
            addLogEntry({
                level: 'warning',
                message: 'Disconnected from dashboard server',
                timestamp: new Date().toISOString()
            });
        });
        
        socket.on('system_update', function(data) {
            updateSystemDisplay(data);
        });
        
        socket.on('new_log', function(logEntry) {
            addLogEntry(logEntry);
        });
        
        socket.on('status', function(data) {
            console.log('Status update:', data.message);
        });
        
    } catch (error) {
        console.error('❌ Socket.IO connection error:', error);
        addLogEntry({
            level: 'error',
            message: `Socket.IO connection error: ${error.message}`,
            timestamp: new Date().toISOString()
        });
    }
}

// Load system status
function loadSystemStatus() {
    console.log('🔄 Loading system status...');
    fetch('/api/status')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 System status data received:', data);
            console.log('📋 Capabilities data:', data.capabilities);
            updateSystemDisplay(data);
        })
        .catch(error => {
            console.error('❌ Error loading system status:', error);
            addLogEntry({
                level: 'error',
                message: `System status error: ${error.message}`,
                timestamp: new Date().toISOString()
            });
            
            // Show error state
            const statusPercent = document.getElementById('status-percent');
            const statusMessage = document.getElementById('status-message');
            const statusProgress = document.getElementById('status-progress');
            
            if (statusPercent) statusPercent.textContent = 'Error';
            if (statusMessage) statusMessage.textContent = 'ไม่สามารถโหลดข้อมูลได้';
            if (statusProgress) statusProgress.style.width = '0%';
        });
}

// Update system display
function updateSystemDisplay(data) {
    try {
        console.log('🔄 Updating system display with data:', data);
        
        // Update status percentage
        if (data.status_percent !== undefined) {
            const percent = Math.round(data.status_percent);
            const statusPercent = document.getElementById('status-percent');
            const statusProgress = document.getElementById('status-progress');
            const statusMessage = document.getElementById('status-message');
            
            if (statusPercent) statusPercent.textContent = `${percent}%`;
            if (statusProgress) statusProgress.style.width = `${percent}%`;
            if (statusMessage) statusMessage.textContent = data.status_message || 'กำลังตรวจสอบ...';
        }
        
        // Update capability cards
        if (data.capabilities) {
            console.log('🔄 Calling updateCapabilityCards with:', data.capabilities);
            updateCapabilityCards(data.capabilities);
        } else {
            console.warn('⚠️ No capabilities data in response');
        }
        
        // Update system resources
        if (data.system_resources) {
            updateSystemResources(data.system_resources);
        }
        
        // Update God Mode data
        if (data.godmode_data) {
            updateGodModeData(data.godmode_data);
        }
        
        // Update recommendations
        if (data.recommendations) {
            updateRecommendations(data.recommendations);
        }
        
        // Update last update time
        if (data.last_update) {
            const lastUpdate = document.getElementById('last-update');
            if (lastUpdate) lastUpdate.textContent = new Date(data.last_update).toLocaleString();
        }
        
        console.log('✅ System display updated successfully');
        
    } catch (error) {
        console.error('❌ Error updating system display:', error);
        addLogEntry({
            level: 'error',
            message: `Display update error: ${error.message}`,
            timestamp: new Date().toISOString()
        });
    }
}

// Update capability cards
function updateCapabilityCards(capabilities) {
    try {
        console.log('🔄 Updating capability cards:', capabilities);
        let readyCount = 0;
        let errorCount = 0;
        
        Object.keys(capabilities).forEach(key => {
            const capability = capabilities[key];
            const cardId = `capability-${key}`;
            const card = document.getElementById(cardId);
            
            console.log(`🔍 Looking for card: ${cardId}`);
            
            if (card) {
                console.log(`✅ Found card: ${cardId}`);
                
                // Update status
                const oldClass = card.className;
                card.className = `capability-card status-${capability.status}`;
                console.log(`🔄 Updated class: ${oldClass} -> ${card.className}`);
                
                // Update status indicator
                const indicator = card.querySelector('.status-indicator');
                if (indicator) {
                    const oldIndicatorClass = indicator.className;
                    indicator.className = `status-indicator ${capability.status}`;
                    console.log(`🔄 Updated indicator: ${oldIndicatorClass} -> ${indicator.className}`);
                } else {
                    console.warn(`⚠️ No status indicator found in card: ${cardId}`);
                }
                
                // Update title (h6 element)
                const title = card.querySelector('h6');
                if (title) {
                    const oldTitle = title.innerHTML;
                    title.innerHTML = `${capability.icon || '🔧'} ${capability.name || key}`;
                    console.log(`🔄 Updated title: ${oldTitle} -> ${title.innerHTML}`);
                } else {
                    console.warn(`⚠️ No title (h6) found in card: ${cardId}`);
                }
                
                // Update description
                const description = card.querySelector('.capability-description');
                if (description) {
                    const oldDesc = description.textContent;
                    description.textContent = capability.description || 'No description available';
                    console.log(`🔄 Updated description: ${oldDesc} -> ${description.textContent}`);
                } else {
                    console.warn(`⚠️ No description found in card: ${cardId}`);
                }
                
                // Count statuses
                if (capability.status === 'ready') readyCount++;
                if (capability.status === 'error') errorCount++;
                
                console.log(`✅ Updated card ${key}: ${capability.name} - ${capability.status}`);
            } else {
                console.warn(`❌ Card not found for capability: ${cardId}`);
            }
        });
        
        // Update counters
        const readyCountElement = document.getElementById('ready-count');
        const errorCountElement = document.getElementById('error-count');
        
        if (readyCountElement) {
            readyCountElement.textContent = readyCount;
            console.log(`🔄 Updated ready count: ${readyCount}`);
        }
        if (errorCountElement) {
            errorCountElement.textContent = errorCount;
            console.log(`🔄 Updated error count: ${errorCount}`);
        }
        
        console.log(`✅ Capability cards updated: ${readyCount} ready, ${errorCount} errors`);
        
    } catch (error) {
        console.error('❌ Error updating capability cards:', error);
    }
}

// Update system resources
function updateSystemResources(resources) {
    try {
        const container = document.getElementById('system-resources');
        if (!container) {
            console.warn('⚠️ System resources container not found');
            return;
        }
        
        if (resources.error) {
            console.warn('⚠️ System resources error:', resources.error);
            container.innerHTML = `<p class="text-danger">Error: ${resources.error}</p>`;
            return;
        }
        
        let resourcesHtml = '';
        
        // CPU
        if (resources.cpu) {
            resourcesHtml += `
                <div class="resource-item">
                    <h6><i class="fas fa-microchip"></i> CPU Usage</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar" style="width: ${resources.cpu.percent}%"></div>
                    </div>
                    <small>${resources.cpu.percent}% (${resources.cpu.count || 'Unknown'} cores)</small>
                </div>
            `;
        }
        
        // Memory
        if (resources.memory) {
            resourcesHtml += `
                <div class="resource-item">
                    <h6><i class="fas fa-memory"></i> Memory Usage</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar" style="width: ${resources.memory.percent}%"></div>
                    </div>
                    <small>${resources.memory.percent}% (${resources.memory.available_gb || 'Unknown'} GB available)</small>
                </div>
            `;
        }
        
        // Disk
        if (resources.disk) {
            resourcesHtml += `
                <div class="resource-item">
                    <h6><i class="fas fa-hdd"></i> Disk Usage</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar" style="width: ${resources.disk.percent}%"></div>
                    </div>
                    <small>${resources.disk.percent}% (${resources.disk.free_gb || 'Unknown'} GB free)</small>
                </div>
            `;
        }
        
        // GPU
        if (resources.gpu) {
            if (resources.gpu.available) {
                const gpuPercent = (resources.gpu.used_memory_mb / (resources.gpu.total_memory_gb * 1024)) * 100;
                resourcesHtml += `
                    <div class="resource-item">
                        <h6><i class="fas fa-gamepad"></i> GPU Status</h6>
                        <div class="progress mb-2">
                            <div class="progress-bar" style="width: ${gpuPercent}%"></div>
                        </div>
                        <small>${resources.gpu.name} - ${resources.gpu.used_memory_mb} MB / ${resources.gpu.total_memory_gb} GB</small>
                    </div>
                `;
            } else {
                resourcesHtml += `
                    <div class="resource-item">
                        <h6><i class="fas fa-gamepad"></i> GPU Status</h6>
                        <small class="text-muted">Not Available</small>
                    </div>
                `;
            }
        }
        
        // Network
        if (resources.network) {
            resourcesHtml += `
                <div class="resource-item">
                    <h6><i class="fas fa-network-wired"></i> Network</h6>
                    <small>${resources.network.status || 'Unknown'}</small>
                </div>
            `;
        }
        
        if (resourcesHtml === '') {
            resourcesHtml = '<p class="text-muted">No resource data available</p>';
        }
        
        container.innerHTML = resourcesHtml;
        
    } catch (error) {
        console.error('❌ Error updating system resources:', error);
        const container = document.getElementById('system-resources');
        if (container) {
            container.innerHTML = `<p class="text-danger">Error updating resources: ${error.message}</p>`;
        }
    }
}

// Load God Mode data
function loadGodModeData() {
    try {
        // Load statistics
        fetch('/api/godmode/statistics')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.warn('⚠️ God Mode statistics error:', data.error);
                } else {
                    updateGodModeStatistics(data);
                }
            })
            .catch(error => {
                console.error('❌ Error loading God Mode statistics:', error);
            });
        
        // Load recent sessions
        fetch('/api/godmode/sessions?limit=5')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    const container = document.getElementById('godmode-sessions');
                    if (container) container.innerHTML = `<p class="text-danger">${data.error}</p>`;
                } else {
                    updateGodModeSessions(data);
                }
            })
            .catch(error => {
                const container = document.getElementById('godmode-sessions');
                if (container) container.innerHTML = `<p class="text-danger">Error: ${error.message}</p>`;
            });
        
        // Load recent commands
        fetch('/api/godmode/commands?limit=5')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    const container = document.getElementById('godmode-commands');
                    if (container) container.innerHTML = `<p class="text-danger">${data.error}</p>`;
                } else {
                    updateGodModeCommands(data);
                }
            })
            .catch(error => {
                const container = document.getElementById('godmode-commands');
                if (container) container.innerHTML = `<p class="text-danger">Error: ${error.message}</p>`;
            });
        
    } catch (error) {
        console.error('❌ Error loading God Mode data:', error);
    }
}

// Update God Mode statistics
function updateGodModeStatistics(stats) {
    try {
        const container = document.getElementById('godmode-statistics');
        if (container) {
            container.innerHTML = `
                <div class="row">
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4>${stats.total_sessions || 0}</h4>
                            <small>Sessions</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4>${stats.total_commands || 0}</h4>
                            <small>Commands</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4>${stats.total_patterns || 0}</h4>
                            <small>Patterns</small>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="text-center">
                            <h4>${stats.success_rate ? stats.success_rate.toFixed(1) : 0}%</h4>
                            <small>Success Rate</small>
                        </div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('❌ Error updating God Mode statistics:', error);
    }
}

// Update God Mode sessions
function updateGodModeSessions(sessions) {
    try {
        const container = document.getElementById('godmode-sessions');
        if (container) {
            if (sessions.length === 0) {
                container.innerHTML = '<p class="text-muted">No sessions found</p>';
                return;
            }
            
            let sessionsHtml = '';
            sessions.forEach(session => {
                sessionsHtml += `
                    <div class="session-item">
                        <strong>${session.session_id}</strong><br>
                        <small>Status: ${session.status} | Commands: ${session.commands_count || 0}</small><br>
                        <small>Started: ${new Date(session.start_time).toLocaleString()}</small>
                    </div>
                `;
            });
            container.innerHTML = sessionsHtml;
        }
    } catch (error) {
        console.error('❌ Error updating God Mode sessions:', error);
    }
}

// Update God Mode commands
function updateGodModeCommands(commands) {
    try {
        const container = document.getElementById('godmode-commands');
        if (container) {
            if (commands.length === 0) {
                container.innerHTML = '<p class="text-muted">No commands found</p>';
                return;
            }
            
            let commandsHtml = '';
            commands.forEach(command => {
                const commandText = command.command_text || 'Unknown command';
                const truncatedText = commandText.length > 50 ? commandText.substring(0, 50) + '...' : commandText;
                
                commandsHtml += `
                    <div class="command-item">
                        <strong>${truncatedText}</strong><br>
                        <small>Type: ${command.command_type || 'Unknown'} | Success: ${command.success ? 'Yes' : 'No'}</small><br>
                        <small>Time: ${new Date(command.execution_time).toLocaleString()}</small>
                    </div>
                `;
            });
            container.innerHTML = commandsHtml;
        }
    } catch (error) {
        console.error('❌ Error updating God Mode commands:', error);
    }
}

// Update recommendations
function updateRecommendations(recommendations) {
    try {
        console.log('🔄 Updating recommendations:', recommendations);
        const container = document.getElementById('recommendations-container');
        if (container && recommendations.length > 0) {
            let recommendationsHtml = '';
            recommendations.forEach(rec => {
                recommendationsHtml += `
                    <div class="alert alert-${getRecommendationType(rec.type)} alert-custom">
                        <i class="fas fa-${getRecommendationIcon(rec.type)}"></i>
                        ${rec.message}
                    </div>
                `;
            });
            container.innerHTML = recommendationsHtml;
            console.log('✅ Recommendations updated successfully');
        } else {
            console.log('⚠️ No recommendations to display');
        }
    } catch (error) {
        console.error('❌ Error updating recommendations:', error);
    }
}

// Get recommendation type
function getRecommendationType(type) {
    const types = {
        'success': 'success',
        'warning': 'warning',
        'error': 'danger',
        'info': 'info'
    };
    return types[type] || 'info';
}

// Get recommendation icon
function getRecommendationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'error': 'times-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Start real-time updates
function startRealTimeUpdates() {
    // Update every 10 seconds
    updateInterval = setInterval(() => {
        loadSystemStatus();
    }, 10000);
}

// Set up event listeners
function setupEventListeners() {
    try {
        // Start God Mode button
        const startGodModeBtn = document.getElementById('start-godmode');
        if (startGodModeBtn) {
            startGodModeBtn.addEventListener('click', startGodModeSession);
        }
        
        // End God Mode button
        const endGodModeBtn = document.getElementById('end-godmode');
        if (endGodModeBtn) {
            endGodModeBtn.addEventListener('click', endGodModeSession);
        }
        
        // Cleanup Chrome button
        const cleanupChromeBtn = document.getElementById('cleanup-chrome');
        if (cleanupChromeBtn) {
            cleanupChromeBtn.addEventListener('click', cleanupChrome);
        }
        
        // Restart Dashboard button
        const restartDashboardBtn = document.getElementById('restart-dashboard');
        if (restartDashboardBtn) {
            restartDashboardBtn.addEventListener('click', restartDashboard);
        }
        
        console.log('✅ Event listeners set up successfully');
        
    } catch (error) {
        console.error('❌ Error setting up event listeners:', error);
    }
}

// God Mode session functions
function startGodModeSession() {
    fetch('/api/godmode/start-session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert('Error starting session: ' + data.error, 'danger');
        } else {
            currentGodModeSession = data.session_id;
            showAlert('God Mode session started: ' + data.session_id, 'success');
            loadGodModeData();
        }
    })
    .catch(error => {
        showAlert('Error: ' + error.message, 'danger');
    });
}

function endGodModeSession() {
    if (!currentGodModeSession) {
        showAlert('No active session to end', 'warning');
        return;
    }
    
    fetch('/api/godmode/end-session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({session_id: currentGodModeSession})
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert('Error ending session: ' + data.error, 'danger');
        } else {
            showAlert('God Mode session ended: ' + currentGodModeSession, 'success');
            currentGodModeSession = null;
            loadGodModeData();
        }
    })
    .catch(error => {
        showAlert('Error: ' + error.message, 'danger');
    });
}

// System control functions
function cleanupChrome() {
    if (confirm('Are you sure you want to cleanup Chrome processes?')) {
        fetch('/api/system/cleanup-chrome', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            showAlert(data.message || 'Chrome cleanup completed', 'info');
        })
        .catch(error => {
            showAlert('Error: ' + error.message, 'danger');
        });
    }
}

function restartDashboard() {
    if (confirm('Are you sure you want to restart the dashboard?')) {
        fetch('/api/system/restart-dashboard', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            showAlert(data.message || 'Dashboard restart requested', 'info');
        })
        .catch(error => {
            showAlert('Error: ' + error.message, 'danger');
        });
    }
}

// Load logs
function loadLogs() {
    fetch('/api/logs')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('logs-container');
            if (container) {
                container.innerHTML = '';
                data.forEach(log => {
                    addLogEntry(log);
                });
            }
        })
        .catch(error => {
            console.error('❌ Error loading logs:', error);
        });
}

// Add log entry
function addLogEntry(logEntry) {
    try {
        const container = document.getElementById('logs-container');
        if (!container) return;
        
        const logDiv = document.createElement('div');
        logDiv.className = `log-entry log-${logEntry.level}`;
        
        logDiv.innerHTML = `
            <small class="text-muted">${new Date(logEntry.timestamp).toLocaleString()}</small>
            <span class="badge bg-${getLogLevelColor(logEntry.level)}">${logEntry.level.toUpperCase()}</span>
            ${logEntry.message}
        `;
        
        container.appendChild(logDiv);
        container.scrollTop = container.scrollHeight;
        
        // Keep only last 100 logs
        const logs = container.querySelectorAll('.log-entry');
        if (logs.length > 100) {
            logs[0].remove();
        }
        
    } catch (error) {
        console.error('❌ Error adding log entry:', error);
    }
}

// Get log level color
function getLogLevelColor(level) {
    const colors = {
        'error': 'danger',
        'warning': 'warning',
        'success': 'success',
        'info': 'info'
    };
    return colors[level] || 'secondary';
}

// Show alert
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    if (socket) {
        socket.disconnect();
    }
});

// Export functions for global access
window.dashboard = {
    loadSystemStatus,
    loadGodModeData,
    loadLogs,
    startGodModeSession,
    endGodModeSession,
    cleanupChrome,
    restartDashboard,
    refreshGodModeData: loadGodModeData
};

// Update God Mode data - เพิ่มฟังก์ชันที่หายไป
function updateGodModeData(godmodeData) {
    try {
        // Update statistics
        if (godmodeData.statistics) {
            updateGodModeStatistics(godmodeData.statistics);
        }
        
        // Update sessions
        if (godmodeData.sessions) {
            updateGodModeSessions(godmodeData.sessions);
        }
        
        // Update commands
        if (godmodeData.commands) {
            updateGodModeCommands(godmodeData.commands);
        }
        
    } catch (error) {
        console.error('❌ Error updating God Mode data:', error);
    }
}
