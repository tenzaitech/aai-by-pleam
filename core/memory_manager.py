"""
WAWAGOT.AI - Advanced Memory Management System
==============================================

This module provides comprehensive memory management for the AI system,
integrating Supabase database with local file storage for optimal performance.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import asyncio
from pathlib import Path

# Supabase integration
try:
    from supabase import create_client, Client
    from supabase.lib.client_options import ClientOptions
except ImportError:
    print("Warning: Supabase not available. Install with: pip install supabase")
    Client = None

# Local imports
from core.logger import get_logger
from core.config_manager import ConfigManager

logger = get_logger(__name__)

@dataclass
class MemoryItem:
    """Represents a single memory item"""
    id: Optional[str] = None
    category: str = ""
    title: str = ""
    content: str = ""
    tags: List[str] = None
    priority: int = 1
    created_at: datetime = None
    updated_at: datetime = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class MemoryManager:
    """
    Advanced memory management system with cloud-first approach
    """
    
    def __init__(self, config_path: str = "config/supabase_config.json"):
        self.config = ConfigManager()
        self.supabase: Optional[Client] = None
        self.local_cache: Dict[str, Any] = {}
        self.memory_dir = Path("pleamthinking")
        self.backup_dir = Path("data/memory_backups")
        
        # Ensure directories exist
        self.memory_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Supabase connection
        self._init_supabase(config_path)
        
        # Load local cache
        self._load_local_cache()
        
        logger.info("Memory Manager initialized successfully")
    
    def _init_supabase(self, config_path: str):
        """Initialize Supabase connection"""
        try:
            if Client is None:
                logger.warning("Supabase client not available")
                return
                
            # Load Supabase configuration
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                url = config.get('supabase_url')
                key = config.get('supabase_key')
                
                if url and key:
                    self.supabase = create_client(url, key)
                    logger.info("Supabase connection established")
                    
                    # Test connection
                    self._test_supabase_connection()
                else:
                    logger.warning("Supabase credentials not found in config")
            else:
                logger.warning(f"Supabase config file not found: {config_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
    
    def _test_supabase_connection(self):
        """Test Supabase connection"""
        try:
            if self.supabase:
                # Simple query to test connection
                result = self.supabase.table('memory').select('id').limit(1).execute()
                logger.info("Supabase connection test successful")
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
    
    def _load_local_cache(self):
        """Load local memory cache from files"""
        try:
            cache_file = self.memory_dir / "memory_cache.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.local_cache = json.load(f)
                logger.info(f"Loaded local cache with {len(self.local_cache)} items")
        except Exception as e:
            logger.error(f"Failed to load local cache: {e}")
            self.local_cache = {}
    
    def _save_local_cache(self):
        """Save local memory cache to files"""
        try:
            cache_file = self.memory_dir / "memory_cache.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.local_cache, f, ensure_ascii=False, indent=2, default=str)
            logger.info("Local cache saved successfully")
        except Exception as e:
            logger.error(f"Failed to save local cache: {e}")
    
    async def store_memory(self, memory: MemoryItem) -> bool:
        """
        Store a memory item (cloud-first approach)
        """
        try:
            # Prepare memory data
            memory_data = asdict(memory)
            memory_data['created_at'] = memory.created_at.isoformat()
            memory_data['updated_at'] = datetime.now().isoformat()
            if memory.expires_at:
                memory_data['expires_at'] = memory.expires_at.isoformat()
            
            # Store in Supabase (primary storage)
            if self.supabase:
                result = self.supabase.table('memory').insert(memory_data).execute()
                if result.data:
                    memory.id = result.data[0]['id']
                    logger.info(f"Memory stored in Supabase with ID: {memory.id}")
            
            # Store in local cache (backup)
            if memory.id:
                self.local_cache[memory.id] = memory_data
                self._save_local_cache()
            
            # Store in category-specific file
            await self._store_in_category_file(memory)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False
    
    async def _store_in_category_file(self, memory: MemoryItem):
        """Store memory in category-specific file"""
        try:
            category_file = self.memory_dir / f"{memory.category}.txt"
            
            # Read existing content
            existing_content = ""
            if category_file.exists():
                with open(category_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Add new memory
            new_entry = f"""
===============================================================================
{memory.title}
===============================================================================
📅 Created: {memory.created_at.strftime('%Y-%m-%d %H:%M:%S')}
🏷️ Tags: {', '.join(memory.tags)}
⭐ Priority: {memory.priority}
📝 Content:
{memory.content}

"""
            
            # Write back to file
            with open(category_file, 'w', encoding='utf-8') as f:
                f.write(existing_content + new_entry)
                
        except Exception as e:
            logger.error(f"Failed to store in category file: {e}")
    
    async def retrieve_memory(self, 
                            category: Optional[str] = None,
                            tags: Optional[List[str]] = None,
                            limit: int = 50) -> List[MemoryItem]:
        """
        Retrieve memory items with filtering
        """
        try:
            memories = []
            
            # Try Supabase first
            if self.supabase:
                query = self.supabase.table('memory').select('*')
                
                if category:
                    query = query.eq('category', category)
                
                if tags:
                    for tag in tags:
                        query = query.contains('tags', [tag])
                
                query = query.order('created_at', desc=True).limit(limit)
                result = query.execute()
                
                for item in result.data:
                    memory = self._dict_to_memory(item)
                    memories.append(memory)
            
            # Fallback to local cache
            if not memories and self.local_cache:
                for item_id, item_data in self.local_cache.items():
                    if category and item_data.get('category') != category:
                        continue
                    if tags and not any(tag in item_data.get('tags', []) for tag in tags):
                        continue
                    
                    memory = self._dict_to_memory(item_data)
                    memories.append(memory)
                    
                    if len(memories) >= limit:
                        break
            
            # Sort by creation date
            memories.sort(key=lambda x: x.created_at, reverse=True)
            
            logger.info(f"Retrieved {len(memories)} memory items")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []
    
    def _dict_to_memory(self, data: Dict[str, Any]) -> MemoryItem:
        """Convert dictionary to MemoryItem"""
        try:
            # Parse datetime fields
            created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
            updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
            expires_at = datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
            
            return MemoryItem(
                id=data.get('id'),
                category=data.get('category', ''),
                title=data.get('title', ''),
                content=data.get('content', ''),
                tags=data.get('tags', []),
                priority=data.get('priority', 1),
                created_at=created_at,
                updated_at=updated_at,
                expires_at=expires_at,
                metadata=data.get('metadata', {})
            )
        except Exception as e:
            logger.error(f"Failed to convert dict to memory: {e}")
            return MemoryItem()
    
    async def search_memory(self, query: str, category: Optional[str] = None) -> List[MemoryItem]:
        """
        Search memory items by content
        """
        try:
            memories = []
            
            # Search in Supabase
            if self.supabase:
                search_query = self.supabase.table('memory').select('*')
                
                if category:
                    search_query = search_query.eq('category', category)
                
                # Full-text search (if available)
                search_query = search_query.text_search('content', query)
                result = search_query.execute()
                
                for item in result.data:
                    memory = self._dict_to_memory(item)
                    memories.append(memory)
            
            # Fallback to local search
            if not memories:
                for item_id, item_data in self.local_cache.items():
                    if category and item_data.get('category') != category:
                        continue
                    
                    content = item_data.get('content', '').lower()
                    title = item_data.get('title', '').lower()
                    query_lower = query.lower()
                    
                    if query_lower in content or query_lower in title:
                        memory = self._dict_to_memory(item_data)
                        memories.append(memory)
            
            logger.info(f"Search found {len(memories)} items for query: {query}")
            return memories
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing memory item
        """
        try:
            updates['updated_at'] = datetime.now().isoformat()
            
            # Update in Supabase
            if self.supabase:
                result = self.supabase.table('memory').update(updates).eq('id', memory_id).execute()
                if result.data:
                    logger.info(f"Memory updated in Supabase: {memory_id}")
            
            # Update local cache
            if memory_id in self.local_cache:
                self.local_cache[memory_id].update(updates)
                self._save_local_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update memory: {e}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory item
        """
        try:
            # Delete from Supabase
            if self.supabase:
                result = self.supabase.table('memory').delete().eq('id', memory_id).execute()
                logger.info(f"Memory deleted from Supabase: {memory_id}")
            
            # Delete from local cache
            if memory_id in self.local_cache:
                del self.local_cache[memory_id]
                self._save_local_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return False
    
    async def backup_memory(self) -> bool:
        """
        Create backup of all memory data
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f"memory_backup_{timestamp}.json"
            
            # Collect all memory data
            all_memories = []
            
            # From Supabase
            if self.supabase:
                result = self.supabase.table('memory').select('*').execute()
                all_memories.extend(result.data)
            
            # From local cache
            all_memories.extend(self.local_cache.values())
            
            # Save backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(all_memories, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Memory backup created: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    async def restore_memory(self, backup_file: str) -> bool:
        """
        Restore memory from backup
        """
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            # Restore to Supabase
            if self.supabase and memories:
                # Clear existing data
                self.supabase.table('memory').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                
                # Insert backup data
                for memory in memories:
                    self.supabase.table('memory').insert(memory).execute()
            
            # Restore local cache
            self.local_cache = {item.get('id', str(i)): item for i, item in enumerate(memories)}
            self._save_local_cache()
            
            logger.info(f"Memory restored from backup: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore memory: {e}")
            return False
    
    async def cleanup_expired_memory(self) -> int:
        """
        Clean up expired memory items
        """
        try:
            count = 0
            now = datetime.now()
            
            # Clean up from Supabase
            if self.supabase:
                result = self.supabase.table('memory').select('id, expires_at').execute()
                for item in result.data:
                    if item.get('expires_at'):
                        expires_at = datetime.fromisoformat(item['expires_at'])
                        if expires_at < now:
                            self.supabase.table('memory').delete().eq('id', item['id']).execute()
                            count += 1
            
            # Clean up local cache
            expired_ids = []
            for item_id, item_data in self.local_cache.items():
                if item_data.get('expires_at'):
                    expires_at = datetime.fromisoformat(item_data['expires_at'])
                    if expires_at < now:
                        expired_ids.append(item_id)
            
            for item_id in expired_ids:
                del self.local_cache[item_id]
                count += 1
            
            if count > 0:
                self._save_local_cache()
                logger.info(f"Cleaned up {count} expired memory items")
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired memory: {e}")
            return 0
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory system statistics
        """
        try:
            stats = {
                'total_items': 0,
                'categories': {},
                'supabase_connected': self.supabase is not None,
                'local_cache_size': len(self.local_cache),
                'backup_files': len(list(self.backup_dir.glob('*.json')))
            }
            
            # Count by category
            if self.supabase:
                result = self.supabase.table('memory').select('category').execute()
                for item in result.data:
                    category = item.get('category', 'uncategorized')
                    stats['categories'][category] = stats['categories'].get(category, 0) + 1
                    stats['total_items'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}

# Global memory manager instance
memory_manager = None

def get_memory_manager() -> MemoryManager:
    """Get global memory manager instance"""
    global memory_manager
    if memory_manager is None:
        memory_manager = MemoryManager()
    return memory_manager

# Convenience functions
async def store_memory(category: str, title: str, content: str, 
                      tags: List[str] = None, priority: int = 1) -> bool:
    """Store a memory item"""
    memory = MemoryItem(
        category=category,
        title=title,
        content=content,
        tags=tags or [],
        priority=priority
    )
    return await get_memory_manager().store_memory(memory)

async def retrieve_memories(category: str = None, tags: List[str] = None) -> List[MemoryItem]:
    """Retrieve memory items"""
    return await get_memory_manager().retrieve_memory(category=category, tags=tags)

async def search_memories(query: str, category: str = None) -> List[MemoryItem]:
    """Search memory items"""
    return await get_memory_manager().search_memory(query, category) 