"""
WAWAGOT.AI - Automated Backup & Restore System
==============================================

This module provides comprehensive backup and restore functionality
for the entire system including memory, configurations, and data.
"""

import os
import json
import shutil
import zipfile
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import asyncio
import schedule
import time
import threading

# Local imports
from core.logger import get_logger
from core.memory_manager import get_memory_manager, MemoryItem
from core.config_manager import ConfigManager

logger = get_logger(__name__)

class BackupManager:
    """
    Comprehensive backup and restore system
    """
    
    def __init__(self, config_path: str = "config/backup_config.json"):
        self.config = ConfigManager()
        self.backup_dir = Path("data/backups")
        self.temp_dir = Path("data/temp")
        self.memory_manager = get_memory_manager()
        
        # Ensure directories exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Load backup configuration
        self.backup_config = self._load_backup_config(config_path)
        
        # Initialize backup scheduler
        self.scheduler_thread = None
        self.scheduler_running = False
        
        logger.info("Backup Manager initialized successfully")
    
    def _load_backup_config(self, config_path: str) -> Dict[str, Any]:
        """Load backup configuration"""
        default_config = {
            "enabled": True,
            "schedule": "0 2 * * *",  # Daily at 2 AM
            "retention_days": 30,
            "compression": True,
            "encryption": False,
            "backup_memory": True,
            "backup_configs": True,
            "backup_logs": True,
            "backup_data": True,
            "backup_pleamthinking": True,
            "max_backup_size": "1GB",
            "verify_backups": True,
            "notify_on_failure": True
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                default_config.update(config)
                logger.info("Backup configuration loaded")
            else:
                # Create default config file
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info("Default backup configuration created")
        except Exception as e:
            logger.error(f"Failed to load backup config: {e}")
        
        return default_config
    
    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """
        Create a comprehensive backup of the entire system
        """
        try:
            # Generate backup name
            if not backup_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"wawagot_backup_{timestamp}"
            
            backup_path = self.backup_dir / f"{backup_name}.zip"
            temp_backup_dir = self.temp_dir / backup_name
            
            # Create temporary directory
            temp_backup_dir.mkdir(exist_ok=True)
            
            logger.info(f"Starting backup: {backup_name}")
            
            # Backup different components
            backup_tasks = []
            
            if self.backup_config.get("backup_memory", True):
                backup_tasks.append(self._backup_memory(temp_backup_dir))
            
            if self.backup_config.get("backup_configs", True):
                backup_tasks.append(self._backup_configs(temp_backup_dir))
            
            if self.backup_config.get("backup_logs", True):
                backup_tasks.append(self._backup_logs(temp_backup_dir))
            
            if self.backup_config.get("backup_data", True):
                backup_tasks.append(self._backup_data(temp_backup_dir))
            
            if self.backup_config.get("backup_pleamthinking", True):
                backup_tasks.append(self._backup_pleamthinking(temp_backup_dir))
            
            # Execute all backup tasks
            await asyncio.gather(*backup_tasks)
            
            # Create metadata
            metadata = await self._create_backup_metadata(backup_name, temp_backup_dir)
            
            # Create compressed backup
            await self._create_compressed_backup(temp_backup_dir, backup_path, metadata)
            
            # Verify backup
            if self.backup_config.get("verify_backups", True):
                await self._verify_backup(backup_path, metadata)
            
            # Cleanup temporary files
            shutil.rmtree(temp_backup_dir)
            
            # Cleanup old backups
            await self._cleanup_old_backups()
            
            logger.info(f"Backup completed successfully: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            if self.backup_config.get("notify_on_failure", True):
                await self._notify_backup_failure(str(e))
            raise
    
    async def _backup_memory(self, backup_dir: Path):
        """Backup memory data"""
        try:
            memory_dir = backup_dir / "memory"
            memory_dir.mkdir(exist_ok=True)
            
            # Backup Supabase memory
            if self.memory_manager.supabase:
                memories = await self.memory_manager.retrieve_memory(limit=10000)
                memory_data = []
                for memory in memories:
                    memory_dict = {
                        'id': memory.id,
                        'category': memory.category,
                        'title': memory.title,
                        'content': memory.content,
                        'tags': memory.tags,
                        'priority': memory.priority,
                        'created_at': memory.created_at.isoformat(),
                        'updated_at': memory.updated_at.isoformat(),
                        'metadata': memory.metadata
                    }
                    if memory.expires_at:
                        memory_dict['expires_at'] = memory.expires_at.isoformat()
                    memory_data.append(memory_dict)
                
                with open(memory_dir / "supabase_memory.json", 'w', encoding='utf-8') as f:
                    json.dump(memory_data, f, ensure_ascii=False, indent=2, default=str)
            
            # Backup local cache
            with open(memory_dir / "local_cache.json", 'w', encoding='utf-8') as f:
                json.dump(self.memory_manager.local_cache, f, ensure_ascii=False, indent=2, default=str)
            
            # Backup category files
            pleamthinking_dir = Path("pleamthinking")
            if pleamthinking_dir.exists():
                for file_path in pleamthinking_dir.glob("*.txt"):
                    shutil.copy2(file_path, memory_dir / file_path.name)
            
            logger.info("Memory backup completed")
            
        except Exception as e:
            logger.error(f"Memory backup failed: {e}")
    
    async def _backup_configs(self, backup_dir: Path):
        """Backup configuration files"""
        try:
            config_dir = backup_dir / "configs"
            config_dir.mkdir(exist_ok=True)
            
            # Backup config directory
            if Path("config").exists():
                shutil.copytree("config", config_dir / "config", dirs_exist_ok=True)
            
            # Backup important config files
            important_files = [
                ".cursorrules",
                ".cursor/mcp.json",
                "requirements.txt",
                "requirements_*.txt"
            ]
            
            for pattern in important_files:
                for file_path in Path(".").glob(pattern):
                    if file_path.is_file():
                        shutil.copy2(file_path, config_dir / file_path.name)
            
            logger.info("Configuration backup completed")
            
        except Exception as e:
            logger.error(f"Configuration backup failed: {e}")
    
    async def _backup_logs(self, backup_dir: Path):
        """Backup log files"""
        try:
            logs_dir = backup_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Backup logs directory
            if Path("logs").exists():
                shutil.copytree("logs", logs_dir / "logs", dirs_exist_ok=True)
            
            logger.info("Logs backup completed")
            
        except Exception as e:
            logger.error(f"Logs backup failed: {e}")
    
    async def _backup_data(self, backup_dir: Path):
        """Backup data files"""
        try:
            data_dir = backup_dir / "data"
            data_dir.mkdir(exist_ok=True)
            
            # Backup data directory (excluding backups)
            if Path("data").exists():
                for item in Path("data").iterdir():
                    if item.name != "backups" and item.name != "temp":
                        if item.is_file():
                            shutil.copy2(item, data_dir / item.name)
                        elif item.is_dir():
                            shutil.copytree(item, data_dir / item.name, dirs_exist_ok=True)
            
            logger.info("Data backup completed")
            
        except Exception as e:
            logger.error(f"Data backup failed: {e}")
    
    async def _backup_pleamthinking(self, backup_dir: Path):
        """Backup pleamthinking directory"""
        try:
            pleamthinking_dir = Path("pleamthinking")
            if pleamthinking_dir.exists():
                shutil.copytree(pleamthinking_dir, backup_dir / "pleamthinking", dirs_exist_ok=True)
                logger.info("Pleamthinking backup completed")
            
        except Exception as e:
            logger.error(f"Pleamthinking backup failed: {e}")
    
    async def _create_backup_metadata(self, backup_name: str, backup_dir: Path) -> Dict[str, Any]:
        """Create backup metadata"""
        try:
            metadata = {
                "backup_name": backup_name,
                "created_at": datetime.now().isoformat(),
                "version": "2.0.0",
                "components": [],
                "file_sizes": {},
                "checksums": {}
            }
            
            # Calculate file sizes and checksums
            for item in backup_dir.rglob("*"):
                if item.is_file():
                    relative_path = str(item.relative_to(backup_dir))
                    metadata["file_sizes"][relative_path] = item.stat().st_size
                    
                    # Calculate checksum
                    with open(item, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        metadata["checksums"][relative_path] = file_hash
            
            # Save metadata
            with open(backup_dir / "backup_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to create backup metadata: {e}")
            return {}
    
    async def _create_compressed_backup(self, source_dir: Path, backup_path: Path, metadata: Dict[str, Any]):
        """Create compressed backup archive"""
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for item in source_dir.rglob("*"):
                    if item.is_file():
                        arcname = str(item.relative_to(source_dir))
                        zipf.write(item, arcname)
            
            logger.info(f"Compressed backup created: {backup_path}")
            
        except Exception as e:
            logger.error(f"Failed to create compressed backup: {e}")
            raise
    
    async def _verify_backup(self, backup_path: Path, metadata: Dict[str, Any]):
        """Verify backup integrity"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Check if all files are present
                file_list = zipf.namelist()
                
                for expected_file in metadata.get("checksums", {}).keys():
                    if expected_file not in file_list:
                        raise ValueError(f"Missing file in backup: {expected_file}")
                
                # Verify checksums
                for file_path, expected_checksum in metadata.get("checksums", {}).items():
                    if file_path in file_list:
                        with zipf.open(file_path) as f:
                            file_hash = hashlib.sha256(f.read()).hexdigest()
                            if file_hash != expected_checksum:
                                raise ValueError(f"Checksum mismatch for {file_path}")
            
            logger.info("Backup verification completed successfully")
            
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            raise
    
    async def restore_backup(self, backup_path: str, restore_to: Optional[str] = None) -> bool:
        """
        Restore system from backup
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Create restore directory
            if not restore_to:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                restore_to = f"restore_{timestamp}"
            
            restore_dir = self.temp_dir / restore_to
            restore_dir.mkdir(exist_ok=True)
            
            logger.info(f"Starting restore from: {backup_path}")
            
            # Extract backup
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(restore_dir)
            
            # Load metadata
            metadata_file = restore_dir / "backup_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                logger.info(f"Restoring backup: {metadata.get('backup_name', 'Unknown')}")
            
            # Restore components
            restore_tasks = []
            
            # Restore memory
            memory_dir = restore_dir / "memory"
            if memory_dir.exists():
                restore_tasks.append(self._restore_memory(memory_dir))
            
            # Restore configs
            configs_dir = restore_dir / "configs"
            if configs_dir.exists():
                restore_tasks.append(self._restore_configs(configs_dir))
            
            # Restore data
            data_dir = restore_dir / "data"
            if data_dir.exists():
                restore_tasks.append(self._restore_data(data_dir))
            
            # Restore pleamthinking
            pleamthinking_dir = restore_dir / "pleamthinking"
            if pleamthinking_dir.exists():
                restore_tasks.append(self._restore_pleamthinking(pleamthinking_dir))
            
            # Execute restore tasks
            await asyncio.gather(*restore_tasks)
            
            logger.info(f"Restore completed successfully to: {restore_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    async def _restore_memory(self, memory_dir: Path):
        """Restore memory data"""
        try:
            # Restore Supabase memory
            supabase_file = memory_dir / "supabase_memory.json"
            if supabase_file.exists():
                with open(supabase_file, 'r', encoding='utf-8') as f:
                    memories = json.load(f)
                
                # Clear existing memory
                if self.memory_manager.supabase:
                    self.memory_manager.supabase.table('memory').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                
                # Restore memories
                for memory_data in memories:
                    # Convert string dates back to datetime
                    if 'created_at' in memory_data:
                        memory_data['created_at'] = datetime.fromisoformat(memory_data['created_at'])
                    if 'updated_at' in memory_data:
                        memory_data['updated_at'] = datetime.fromisoformat(memory_data['updated_at'])
                    if 'expires_at' in memory_data and memory_data['expires_at']:
                        memory_data['expires_at'] = datetime.fromisoformat(memory_data['expires_at'])
                    
                    memory = MemoryItem(**memory_data)
                    await self.memory_manager.store_memory(memory)
            
            # Restore local cache
            cache_file = memory_dir / "local_cache.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.memory_manager.local_cache = json.load(f)
                self.memory_manager._save_local_cache()
            
            logger.info("Memory restore completed")
            
        except Exception as e:
            logger.error(f"Memory restore failed: {e}")
    
    async def _restore_configs(self, configs_dir: Path):
        """Restore configuration files"""
        try:
            # Restore config directory
            config_backup = configs_dir / "config"
            if config_backup.exists():
                if Path("config").exists():
                    shutil.rmtree("config")
                shutil.copytree(config_backup, "config")
            
            # Restore individual config files
            for file_path in configs_dir.iterdir():
                if file_path.is_file() and file_path.name != "config":
                    shutil.copy2(file_path, Path(".") / file_path.name)
            
            logger.info("Configuration restore completed")
            
        except Exception as e:
            logger.error(f"Configuration restore failed: {e}")
    
    async def _restore_data(self, data_dir: Path):
        """Restore data files"""
        try:
            # Restore data files
            for item in data_dir.iterdir():
                target_path = Path("data") / item.name
                if item.is_file():
                    shutil.copy2(item, target_path)
                elif item.is_dir():
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(item, target_path)
            
            logger.info("Data restore completed")
            
        except Exception as e:
            logger.error(f"Data restore failed: {e}")
    
    async def _restore_pleamthinking(self, pleamthinking_dir: Path):
        """Restore pleamthinking directory"""
        try:
            if Path("pleamthinking").exists():
                shutil.rmtree("pleamthinking")
            shutil.copytree(pleamthinking_dir, "pleamthinking")
            
            logger.info("Pleamthinking restore completed")
            
        except Exception as e:
            logger.error(f"Pleamthinking restore failed: {e}")
    
    async def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        try:
            retention_days = self.backup_config.get("retention_days", 30)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            deleted_count = 0
            for backup_file in self.backup_dir.glob("*.zip"):
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old backups")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    async def _notify_backup_failure(self, error_message: str):
        """Notify about backup failure"""
        try:
            # This can be extended to send notifications via email, Slack, etc.
            logger.error(f"BACKUP FAILURE NOTIFICATION: {error_message}")
            
            # Store failure in memory for tracking
            await self.memory_manager.store_memory(
                MemoryItem(
                    category="system",
                    title="Backup Failure",
                    content=f"Backup failed at {datetime.now()}: {error_message}",
                    tags=["backup", "failure", "system"],
                    priority=3
                )
            )
            
        except Exception as e:
            logger.error(f"Failed to send backup failure notification: {e}")
    
    def start_scheduled_backups(self):
        """Start scheduled backup service"""
        try:
            if not self.backup_config.get("enabled", True):
                logger.info("Scheduled backups are disabled")
                return
            
            schedule_str = self.backup_config.get("schedule", "0 2 * * *")
            
            # Schedule daily backup
            schedule.every().day.at("02:00").do(self._run_scheduled_backup)
            
            self.scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            
            logger.info(f"Scheduled backups started with schedule: {schedule_str}")
            
        except Exception as e:
            logger.error(f"Failed to start scheduled backups: {e}")
    
    def stop_scheduled_backups(self):
        """Stop scheduled backup service"""
        try:
            self.scheduler_running = False
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5)
            
            logger.info("Scheduled backups stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop scheduled backups: {e}")
    
    def _run_scheduler(self):
        """Run the backup scheduler"""
        while self.scheduler_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _run_scheduled_backup(self):
        """Run scheduled backup (wrapper for async function)"""
        try:
            asyncio.run(self.create_backup())
        except Exception as e:
            logger.error(f"Scheduled backup failed: {e}")
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup system statistics"""
        try:
            backup_files = list(self.backup_dir.glob("*.zip"))
            
            stats = {
                "total_backups": len(backup_files),
                "total_size": sum(f.stat().st_size for f in backup_files),
                "oldest_backup": None,
                "newest_backup": None,
                "scheduled_backups_enabled": self.backup_config.get("enabled", True),
                "retention_days": self.backup_config.get("retention_days", 30),
                "scheduler_running": self.scheduler_running
            }
            
            if backup_files:
                backup_times = [datetime.fromtimestamp(f.stat().st_mtime) for f in backup_files]
                stats["oldest_backup"] = min(backup_times).isoformat()
                stats["newest_backup"] = max(backup_times).isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get backup stats: {e}")
            return {}

# Global backup manager instance
backup_manager = None

def get_backup_manager() -> BackupManager:
    """Get global backup manager instance"""
    global backup_manager
    if backup_manager is None:
        backup_manager = BackupManager()
    return backup_manager

# Convenience functions
async def create_backup(backup_name: str = None) -> str:
    """Create a backup"""
    return await get_backup_manager().create_backup(backup_name)

async def restore_backup(backup_path: str, restore_to: str = None) -> bool:
    """Restore from backup"""
    return await get_backup_manager().restore_backup(backup_path, restore_to)

def start_scheduled_backups():
    """Start scheduled backups"""
    get_backup_manager().start_scheduled_backups()

def stop_scheduled_backups():
    """Stop scheduled backups"""
    get_backup_manager().stop_scheduled_backups() 