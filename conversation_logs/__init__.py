# -*- coding: utf-8 -*-
"""
WAWAGOT.AI Conversation Logs System
ระบบบันทึกการสนทนาอัตโนมัติแบบยืดหยุ่น
"""

# Import ระบบย่อยหลัก
from .security_manager import SecurityManager
from .monitoring_alert_system import MonitoringAlertSystem
from .data_retention_manager import DataRetentionManager

# Import ระบบย่อยเดิม
from .auto_logger.auto_logger import AutoLogger
from .ai_filter.ai_filter import AIFilter
from .conversation_manager.conversation_manager import ConversationManager
from .auto_backup.auto_backup import AutoBackup
from .integration.integration_manager import IntegrationManager

__version__ = "1.0.0"
__author__ = "WAWAGOT.AI Team"

# Export ระบบย่อยทั้งหมด
__all__ = [
    'SecurityManager',
    'MonitoringAlertSystem', 
    'DataRetentionManager',
    'AutoLogger',
    'AIFilter',
    'ConversationManager',
    'AutoBackup',
    'IntegrationManager'
] 