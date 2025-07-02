#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Manager for AI-Powered Learning System
จัดการฐานความรู้สำหรับการเรียนรู้และควบคุมระบบ
"""

import json
import os
import requests
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any
import hashlib
from urllib.parse import urlparse
import re

class KnowledgeManager:
    def __init__(self, base_path: str = "Learning-doc-datafiles"):
        """
        Initialize Knowledge Manager
        
        Args:
            base_path: Path to store knowledge files
        """
        self.base_path = base_path
        self.knowledge_file = os.path.join(base_path, "knowledge-base.json")
        self.categories_file = os.path.join(base_path, "categories.json")
        self.logger = logging.getLogger(__name__)
        
        # Create directory if not exists
        os.makedirs(base_path, exist_ok=True)
        
        # Initialize knowledge base
        self.knowledge_base = self._load_knowledge_base()
        self.categories = self._load_categories()
        
        self.logger.info(f"🧠 Knowledge Manager initialized at {base_path}")
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base from file"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logger.info(f"📚 Loaded {len(data.get('knowledge', []))} knowledge items")
                    return data
            else:
                # Create new knowledge base
                default_kb = {
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "version": "1.0",
                        "total_items": 0
                    },
                    "knowledge": [],
                    "categories": []
                }
                self._save_knowledge_base(default_kb)
                return default_kb
        except Exception as e:
            self.logger.error(f"❌ Error loading knowledge base: {e}")
            return {"metadata": {}, "knowledge": [], "categories": []}
    
    def _save_knowledge_base(self, data: Dict[str, Any]) -> bool:
        """Save knowledge base to file"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"❌ Error saving knowledge base: {e}")
            return False
    
    def _load_categories(self) -> Dict[str, Any]:
        """Load categories configuration"""
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Default categories
                default_categories = {
                    "categories": [
                        {"id": "n8n", "name": "n8n", "description": "n8n Workflow Automation", "icon": "🔧"},
                        {"id": "zapier", "name": "Zapier", "description": "Zapier Automation", "icon": "⚡"},
                        {"id": "make", "name": "Make", "description": "Make (Integromat) Automation", "icon": "🔄"},
                        {"id": "general", "name": "General", "description": "General Automation Knowledge", "icon": "📚"},
                        {"id": "chrome", "name": "Chrome", "description": "Chrome Automation", "icon": "🌐"},
                        {"id": "ai", "name": "AI", "description": "AI Integration", "icon": "🧠"}
                    ],
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "version": "1.0"
                    }
                }
                self._save_categories(default_categories)
                return default_categories
        except Exception as e:
            self.logger.error(f"❌ Error loading categories: {e}")
            return {"categories": [], "metadata": {}}
    
    def _save_categories(self, data: Dict[str, Any]) -> bool:
        """Save categories configuration"""
        try:
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"❌ Error saving categories: {e}")
            return False
    
    def add_knowledge_from_url(self, url: str, category: str, title: str = None, description: str = None) -> Dict[str, Any]:
        """
        Add knowledge from URL
        
        Args:
            url: URL to learn from
            category: Knowledge category
            title: Custom title (optional)
            description: Custom description (optional)
            
        Returns:
            Dict with result status and knowledge ID
        """
        try:
            self.logger.info(f"🔍 Learning from URL: {url}")
            
            # Validate URL
            if not self._is_valid_url(url):
                return {"success": False, "error": "Invalid URL format"}
            
            # Fetch content from URL
            content = self._fetch_url_content(url)
            if not content:
                return {"success": False, "error": "Could not fetch content from URL"}
            
            # Generate knowledge item
            knowledge_item = {
                "id": self._generate_knowledge_id(url),
                "title": title or self._extract_title_from_url(url),
                "description": description or self._extract_description(content),
                "url": url,
                "category": category,
                "content": content,
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "source": "url",
                    "content_length": len(content),
                    "domain": urlparse(url).netloc
                },
                "tags": self._extract_tags(content),
                "summary": self._generate_summary(content)
            }
            
            # Add to knowledge base
            self.knowledge_base["knowledge"].append(knowledge_item)
            self.knowledge_base["metadata"]["total_items"] = len(self.knowledge_base["knowledge"])
            self.knowledge_base["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save to file
            if self._save_knowledge_base(self.knowledge_base):
                self.logger.info(f"✅ Knowledge added successfully: {knowledge_item['id']}")
                return {
                    "success": True,
                    "knowledge_id": knowledge_item["id"],
                    "message": "Knowledge added successfully"
                }
            else:
                return {"success": False, "error": "Failed to save knowledge base"}
                
        except Exception as e:
            self.logger.error(f"❌ Error adding knowledge from URL: {e}")
            return {"success": False, "error": str(e)}
    
    def add_knowledge_from_text(self, title: str, content: str, category: str, description: str = None) -> Dict[str, Any]:
        """
        Add knowledge from text
        
        Args:
            title: Knowledge title
            content: Knowledge content
            category: Knowledge category
            description: Knowledge description (optional)
            
        Returns:
            Dict with result status and knowledge ID
        """
        try:
            self.logger.info(f"📝 Adding knowledge from text: {title}")
            
            knowledge_item = {
                "id": self._generate_knowledge_id(title + content),
                "title": title,
                "description": description or self._extract_description(content),
                "url": None,
                "category": category,
                "content": content,
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "source": "text",
                    "content_length": len(content)
                },
                "tags": self._extract_tags(content),
                "summary": self._generate_summary(content)
            }
            
            # Add to knowledge base
            self.knowledge_base["knowledge"].append(knowledge_item)
            self.knowledge_base["metadata"]["total_items"] = len(self.knowledge_base["knowledge"])
            self.knowledge_base["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save to file
            if self._save_knowledge_base(self.knowledge_base):
                self.logger.info(f"✅ Knowledge added successfully: {knowledge_item['id']}")
                return {
                    "success": True,
                    "knowledge_id": knowledge_item["id"],
                    "message": "Knowledge added successfully"
                }
            else:
                return {"success": False, "error": "Failed to save knowledge base"}
                
        except Exception as e:
            self.logger.error(f"❌ Error adding knowledge from text: {e}")
            return {"success": False, "error": str(e)}
    
    def update_knowledge(self, knowledge_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing knowledge
        
        Args:
            knowledge_id: ID of knowledge to update
            updates: Dictionary of fields to update
            
        Returns:
            Dict with result status
        """
        try:
            # Find knowledge item
            for item in self.knowledge_base["knowledge"]:
                if item["id"] == knowledge_id:
                    # Update fields
                    for key, value in updates.items():
                        if key in ["title", "description", "category", "content"]:
                            item[key] = value
                    
                    # Update metadata
                    item["metadata"]["last_updated"] = datetime.now().isoformat()
                    
                    # Regenerate summary and tags if content changed
                    if "content" in updates:
                        item["summary"] = self._generate_summary(item["content"])
                        item["tags"] = self._extract_tags(item["content"])
                    
                    # Save to file
                    if self._save_knowledge_base(self.knowledge_base):
                        self.logger.info(f"✅ Knowledge updated successfully: {knowledge_id}")
                        return {"success": True, "message": "Knowledge updated successfully"}
                    else:
                        return {"success": False, "error": "Failed to save knowledge base"}
            
            return {"success": False, "error": "Knowledge not found"}
            
        except Exception as e:
            self.logger.error(f"❌ Error updating knowledge: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_knowledge(self, knowledge_id: str) -> Dict[str, Any]:
        """
        Delete knowledge item
        
        Args:
            knowledge_id: ID of knowledge to delete
            
        Returns:
            Dict with result status
        """
        try:
            # Find and remove knowledge item
            for i, item in enumerate(self.knowledge_base["knowledge"]):
                if item["id"] == knowledge_id:
                    deleted_item = self.knowledge_base["knowledge"].pop(i)
                    self.knowledge_base["metadata"]["total_items"] = len(self.knowledge_base["knowledge"])
                    self.knowledge_base["metadata"]["last_updated"] = datetime.now().isoformat()
                    
                    # Save to file
                    if self._save_knowledge_base(self.knowledge_base):
                        self.logger.info(f"✅ Knowledge deleted successfully: {knowledge_id}")
                        return {"success": True, "message": "Knowledge deleted successfully"}
                    else:
                        return {"success": False, "error": "Failed to save knowledge base"}
            
            return {"success": False, "error": "Knowledge not found"}
            
        except Exception as e:
            self.logger.error(f"❌ Error deleting knowledge: {e}")
            return {"success": False, "error": str(e)}
    
    def search_knowledge(self, query: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search knowledge base
        
        Args:
            query: Search query
            category: Filter by category (optional)
            limit: Maximum number of results
            
        Returns:
            List of matching knowledge items
        """
        try:
            query_lower = query.lower()
            results = []
            
            for item in self.knowledge_base["knowledge"]:
                # Filter by category if specified
                if category and item["category"] != category:
                    continue
                
                # Search in title, description, content, and tags
                searchable_text = f"{item['title']} {item['description']} {item['content']} {' '.join(item.get('tags', []))}"
                
                if query_lower in searchable_text.lower():
                    # Calculate relevance score (simple implementation)
                    relevance = 0
                    if query_lower in item['title'].lower():
                        relevance += 10
                    if query_lower in item['description'].lower():
                        relevance += 5
                    if query_lower in item['content'].lower():
                        relevance += 1
                    
                    results.append({
                        **item,
                        "relevance_score": relevance
                    })
            
            # Sort by relevance and limit results
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            self.logger.error(f"❌ Error searching knowledge: {e}")
            return []
    
    def get_knowledge_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all knowledge items in a category"""
        try:
            return [item for item in self.knowledge_base["knowledge"] if item["category"] == category]
        except Exception as e:
            self.logger.error(f"❌ Error getting knowledge by category: {e}")
            return []
    
    def get_knowledge_by_id(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """Get knowledge item by ID"""
        try:
            for item in self.knowledge_base["knowledge"]:
                if item["id"] == knowledge_id:
                    return item
            return None
        except Exception as e:
            self.logger.error(f"❌ Error getting knowledge by ID: {e}")
            return None
    
    def get_all_knowledge(self) -> List[Dict[str, Any]]:
        """Get all knowledge items"""
        return self.knowledge_base.get("knowledge", [])
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        return self.categories.get("categories", [])
    
    def add_category(self, category_id: str, name: str, description: str, icon: str = "📁") -> Dict[str, Any]:
        """Add new category"""
        try:
            # Check if category already exists
            for cat in self.categories["categories"]:
                if cat["id"] == category_id:
                    return {"success": False, "error": "Category already exists"}
            
            new_category = {
                "id": category_id,
                "name": name,
                "description": description,
                "icon": icon
            }
            
            self.categories["categories"].append(new_category)
            self.categories["metadata"]["last_updated"] = datetime.now().isoformat()
            
            if self._save_categories(self.categories):
                self.logger.info(f"✅ Category added successfully: {category_id}")
                return {"success": True, "message": "Category added successfully"}
            else:
                return {"success": False, "error": "Failed to save categories"}
                
        except Exception as e:
            self.logger.error(f"❌ Error adding category: {e}")
            return {"success": False, "error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            total_items = len(self.knowledge_base["knowledge"])
            categories = {}
            
            for item in self.knowledge_base["knowledge"]:
                cat = item["category"]
                categories[cat] = categories.get(cat, 0) + 1
            
            return {
                "total_items": total_items,
                "categories": categories,
                "last_updated": self.knowledge_base["metadata"].get("last_updated"),
                "created": self.knowledge_base["metadata"].get("created")
            }
        except Exception as e:
            self.logger.error(f"❌ Error getting statistics: {e}")
            return {}
    
    # Helper methods
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _fetch_url_content(self, url: str) -> Optional[str]:
        """Fetch content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"❌ Error fetching URL content: {e}")
            return None
    
    def _generate_knowledge_id(self, content: str) -> str:
        """Generate unique knowledge ID"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract title from URL"""
        try:
            domain = urlparse(url).netloc
            path = urlparse(url).path
            if path:
                return path.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
            return domain
        except:
            return "Untitled"
    
    def _extract_description(self, content: str) -> str:
        """Extract description from content"""
        # Simple implementation - take first 200 characters
        return content[:200].strip() + "..." if len(content) > 200 else content.strip()
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content"""
        # Simple implementation - extract common words
        words = re.findall(r'\b\w+\b', content.lower())
        common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        tags = [word for word in words if word not in common_words and len(word) > 3]
        return list(set(tags[:10]))  # Return unique tags, max 10
    
    def _generate_summary(self, content: str) -> str:
        """Generate summary from content"""
        # Simple implementation - take first 500 characters
        return content[:500].strip() + "..." if len(content) > 500 else content.strip()

# Global instance
knowledge_manager = KnowledgeManager() 