#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase Integration for Backup-byGod
เชื่อมต่อกับ Supabase Pro Plan สำหรับ Database และ Real-time Features
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase library not installed. Run: pip install supabase")

class SupabaseIntegration:
    """Supabase Integration Controller"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.is_connected = False
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, str]:
        """โหลด Supabase configuration"""
        config_path = "config/supabase_config.json"
        
        # Default config template
        default_config = {
            "supabase_url": "YOUR_SUPABASE_URL",
            "supabase_key": "YOUR_SUPABASE_ANON_KEY",
            "supabase_service_key": "YOUR_SUPABASE_SERVICE_KEY"
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            else:
                # สร้าง config file ใหม่
                os.makedirs("config", exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                return default_config
        except Exception as e:
            logging.error(f"Error loading Supabase config: {e}")
            return default_config
    
    def connect(self) -> bool:
        """เชื่อมต่อกับ Supabase"""
        if not SUPABASE_AVAILABLE:
            logging.error("Supabase library not available")
            return False
            
        try:
            if (self.config["supabase_url"] == "YOUR_SUPABASE_URL" or 
                self.config["supabase_key"] == "YOUR_SUPABASE_ANON_KEY"):
                logging.warning("Supabase credentials not configured")
                return False
                
            self.client = create_client(
                self.config["supabase_url"],
                self.config["supabase_key"]
            )
            
            # ทดสอบการเชื่อมต่อ
            response = self.client.table('system_status').select('*').limit(1).execute()
            self.is_connected = True
            logging.info("✅ Supabase connected successfully")
            return True
            
        except Exception as e:
            logging.error(f"❌ Supabase connection failed: {e}")
            self.is_connected = False
            return False
    
    def save_backup_log(self, backup_data: Dict[str, Any]) -> bool:
        """บันทึก backup log ลง Supabase"""
        if not self.is_connected:
            return False
            
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "backup_type": backup_data.get("type", "unknown"),
                "status": backup_data.get("status", "unknown"),
                "file_count": backup_data.get("file_count", 0),
                "total_size": backup_data.get("total_size", 0),
                "duration": backup_data.get("duration", 0),
                "details": json.dumps(backup_data.get("details", {}))
            }
            
            result = self.client.table('backup_logs').insert(log_entry).execute()
            logging.info(f"✅ Backup log saved: {backup_data.get('type')}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to save backup log: {e}")
            return False
    
    def get_backup_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """ดึงประวัติ backup จาก Supabase"""
        if not self.is_connected:
            return []
            
        try:
            result = self.client.table('backup_logs')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logging.error(f"❌ Failed to get backup history: {e}")
            return []
    
    def save_system_status(self, status_data: Dict[str, Any]) -> bool:
        """บันทึกสถานะระบบลง Supabase"""
        if not self.is_connected:
            return False
            
        try:
            status_entry = {
                "timestamp": datetime.now().isoformat(),
                "cpu_usage": status_data.get("cpu_percent", 0),
                "memory_usage": status_data.get("memory_percent", 0),
                "disk_usage": status_data.get("disk_percent", 0),
                "components_ready": status_data.get("ready_components", 0),
                "total_components": status_data.get("total_components", 0),
                "system_status": status_data.get("status_message", "unknown")
            }
            
            result = self.client.table('system_status').insert(status_entry).execute()
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to save system status: {e}")
            return False
    
    def get_system_analytics(self, days: int = 7) -> Dict[str, Any]:
        """ดึงข้อมูล analytics จาก Supabase"""
        if not self.is_connected:
            return {}
            
        try:
            # ดึงข้อมูล backup success rate
            backup_result = self.client.table('backup_logs')\
                .select('status')\
                .execute()
            
            total_backups = len(backup_result.data)
            successful_backups = len([b for b in backup_result.data if b.get('status') == 'success'])
            success_rate = (successful_backups / total_backups * 100) if total_backups > 0 else 0
            
            # ดึงข้อมูล system performance
            system_result = self.client.table('system_status')\
                .select('cpu_usage,memory_usage,disk_usage')\
                .order('timestamp', desc=True)\
                .limit(100)\
                .execute()
            
            avg_cpu = sum(s.get('cpu_usage', 0) for s in system_result.data) / len(system_result.data) if system_result.data else 0
            avg_memory = sum(s.get('memory_usage', 0) for s in system_result.data) / len(system_result.data) if system_result.data else 0
            
            return {
                "backup_success_rate": round(success_rate, 2),
                "total_backups": total_backups,
                "avg_cpu_usage": round(avg_cpu, 2),
                "avg_memory_usage": round(avg_memory, 2),
                "data_points": len(system_result.data)
            }
            
        except Exception as e:
            logging.error(f"❌ Failed to get analytics: {e}")
            return {}
    
    def disconnect(self):
        """ปิดการเชื่อมต่อ Supabase"""
        self.client = None
        self.is_connected = False
        logging.info("🔌 Supabase disconnected")

# Global instance
supabase_integration = SupabaseIntegration() 