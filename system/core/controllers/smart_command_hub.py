#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Command Hub - ศูนย์กลางคำสั่งอัจฉริยะ
จัดการคำสั่งทั้งหมดในระบบแบบอัตโนมัติและอัจฉริยะ
"""

import json
import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import re
from collections import defaultdict, Counter
import threading
import time

# Import existing components
try:
    from .knowledge_manager import KnowledgeManager
    from .ai_integration import AIIntegration
    from .chrome_controller import ChromeController
    from .thai_processor import ThaiProcessor
    from .visual_recognition import VisualRecognition
    from .backup_controller import BackupController
    from .restore_controller import RestoreController
    from .supabase_integration import SupabaseIntegration
    from .auto_learning_manager import AutoLearningManager
except ImportError:
    # Mock classes for development
    class MockComponent:
        def __init__(self, name):
            self.name = name
            self.is_available = True
        
        async def execute(self, command, params):
            return {"status": "success", "component": self.name, "result": f"Mock {command}"}
    
    KnowledgeManager = MockComponent("KnowledgeManager")
    AIIntegration = MockComponent("AIIntegration")
    ChromeController = MockComponent("ChromeController")
    ThaiProcessor = MockComponent("ThaiProcessor")
    VisualRecognition = MockComponent("VisualRecognition")
    BackupController = MockComponent("BackupController")
    RestoreController = MockComponent("RestoreController")
    SupabaseIntegration = MockComponent("SupabaseIntegration")
    AutoLearningManager = MockComponent("AutoLearningManager")

@dataclass
class CommandDefinition:
    """คำนิยามคำสั่ง"""
    id: str
    name: str
    description: str
    category: str
    component: str
    command: str
    parameters: Dict[str, Any]
    examples: List[str]
    tags: List[str]
    usage_count: int = 0
    success_rate: float = 0.0
    last_used: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    is_active: bool = True
    requires_auth: bool = False
    timeout: int = 30
    retry_count: int = 3

@dataclass
class CommandExecution:
    """การประมวลผลคำสั่ง"""
    id: str
    command_id: str
    user_input: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    execution_time: float
    status: str
    error_message: Optional[str] = None
    timestamp: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class CommandPattern:
    """รูปแบบคำสั่ง"""
    id: str
    pattern: str
    command_id: str
    confidence: float
    usage_count: int = 0
    last_used: Optional[str] = None

class SmartCommandHub:
    """Smart Command Hub - ศูนย์กลางคำสั่งอัจฉริยะ"""
    
    def __init__(self, db_path: str = "database/smart_command_hub.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.components = {
            'knowledge_manager': KnowledgeManager("KnowledgeManager"),
            'ai_integration': AIIntegration("AIIntegration"),
            'chrome_controller': ChromeController("ChromeController"),
            'thai_processor': ThaiProcessor("ThaiProcessor"),
            'visual_recognition': VisualRecognition("VisualRecognition"),
            'backup_controller': BackupController("BackupController"),
            'restore_controller': RestoreController("RestoreController"),
            'supabase_integration': SupabaseIntegration("SupabaseIntegration"),
            'auto_learning_manager': AutoLearningManager("AutoLearningManager")
        }
        
        # Initialize database
        self.init_database()
        
        # Load default commands
        self.load_default_commands()
        
        # Initialize AI for pattern recognition
        self.pattern_cache = {}
        self.command_cache = {}
        self.user_preferences = {}
        
        # Background tasks
        self.background_thread = None
        self.is_running = True
        self.start_background_tasks()
        
        logging.info("🚀 Smart Command Hub initialized successfully")
    
    def init_database(self):
        """สร้างฐานข้อมูล"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS commands (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    component TEXT,
                    command TEXT,
                    parameters TEXT,
                    examples TEXT,
                    tags TEXT,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    last_used TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    requires_auth BOOLEAN DEFAULT 0,
                    timeout INTEGER DEFAULT 30,
                    retry_count INTEGER DEFAULT 3
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id TEXT PRIMARY KEY,
                    command_id TEXT,
                    user_input TEXT,
                    parameters TEXT,
                    result TEXT,
                    execution_time REAL,
                    status TEXT,
                    error_message TEXT,
                    timestamp TEXT,
                    user_id TEXT,
                    session_id TEXT,
                    FOREIGN KEY (command_id) REFERENCES commands (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id TEXT PRIMARY KEY,
                    pattern TEXT,
                    command_id TEXT,
                    confidence REAL,
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT,
                    FOREIGN KEY (command_id) REFERENCES commands (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferences TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_commands_category ON commands(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_commands_component ON commands(component)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_timestamp ON executions(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_patterns_pattern ON patterns(pattern)")
            
            conn.commit()
    
    def load_default_commands(self):
        """โหลดคำสั่งเริ่มต้น"""
        default_commands = [
            {
                "id": "chrome_navigate",
                "name": "เปิดเว็บไซต์",
                "description": "เปิดเว็บไซต์ใน Chrome",
                "category": "chrome",
                "component": "chrome_controller",
                "command": "navigate_to",
                "parameters": {"url": "string"},
                "examples": ["เปิด Google", "ไปที่ Facebook", "เปิด YouTube"],
                "tags": ["chrome", "web", "navigate", "เปิด", "ไปที่"]
            },
            {
                "id": "chrome_click",
                "name": "คลิกองค์ประกอบ",
                "description": "คลิกองค์ประกอบในหน้าเว็บ",
                "category": "chrome",
                "component": "chrome_controller",
                "command": "click_element",
                "parameters": {"selector": "string"},
                "examples": ["คลิกปุ่ม", "กดลิงก์", "เลือกเมนู"],
                "tags": ["chrome", "click", "คลิก", "กด", "เลือก"]
            },
            {
                "id": "chrome_type",
                "name": "พิมพ์ข้อความ",
                "description": "พิมพ์ข้อความในช่องกรอก",
                "category": "chrome",
                "component": "chrome_controller",
                "command": "type_text",
                "parameters": {"selector": "string", "text": "string"},
                "examples": ["พิมพ์คำค้นหา", "กรอกข้อมูล", "ใส่รหัสผ่าน"],
                "tags": ["chrome", "type", "พิมพ์", "กรอก", "ใส่"]
            },
            {
                "id": "chrome_screenshot",
                "name": "ถ่ายภาพหน้าจอ",
                "description": "ถ่ายภาพหน้าจอของหน้าเว็บ",
                "category": "chrome",
                "component": "chrome_controller",
                "command": "take_screenshot",
                "parameters": {},
                "examples": ["ถ่ายภาพหน้าจอ", "บันทึกภาพ", "แคปหน้าจอ"],
                "tags": ["chrome", "screenshot", "ถ่ายภาพ", "บันทึก", "แคป"]
            },
            {
                "id": "ai_process",
                "name": "ประมวลผล AI",
                "description": "ประมวลผลคำสั่งด้วย AI",
                "category": "ai",
                "component": "ai_integration",
                "command": "process_command",
                "parameters": {"command": "string", "parameters": "object"},
                "examples": ["วิเคราะห์ข้อมูล", "สรุปข้อความ", "แปลภาษา"],
                "tags": ["ai", "process", "วิเคราะห์", "สรุป", "แปล"]
            },
            {
                "id": "thai_process",
                "name": "ประมวลผลภาษาไทย",
                "description": "ประมวลผลคำสั่งภาษาไทย",
                "category": "thai",
                "component": "thai_processor",
                "command": "process_command",
                "parameters": {"command": "string", "parameters": "object"},
                "examples": ["ประมวลผลภาษาไทย", "วิเคราะห์ข้อความไทย", "แปลภาษาไทย"],
                "tags": ["thai", "process", "ภาษาไทย", "วิเคราะห์", "แปล"]
            },
            {
                "id": "visual_analyze",
                "name": "วิเคราะห์ภาพ",
                "description": "วิเคราะห์และจดจำภาพ",
                "category": "visual",
                "component": "visual_recognition",
                "command": "analyze_image",
                "parameters": {"image_data": "string"},
                "examples": ["วิเคราะห์ภาพ", "จดจำภาพ", "อ่านข้อความในภาพ"],
                "tags": ["visual", "analyze", "วิเคราะห์", "จดจำ", "อ่าน"]
            },
            {
                "id": "backup_create",
                "name": "สร้างการสำรองข้อมูล",
                "description": "สร้างการสำรองข้อมูลระบบ",
                "category": "backup",
                "component": "backup_controller",
                "command": "create_backup",
                "parameters": {"source": "string", "destination": "string"},
                "examples": ["สำรองข้อมูล", "สร้าง backup", "เก็บข้อมูล"],
                "tags": ["backup", "create", "สำรอง", "เก็บ", "backup"]
            },
            {
                "id": "restore_data",
                "name": "กู้คืนข้อมูล",
                "description": "กู้คืนข้อมูลจากการสำรอง",
                "category": "restore",
                "component": "restore_controller",
                "command": "restore_backup",
                "parameters": {"backup_id": "string", "destination": "string"},
                "examples": ["กู้คืนข้อมูล", "restore", "เรียกข้อมูลกลับ"],
                "tags": ["restore", "กู้คืน", "เรียกกลับ", "restore"]
            },
            {
                "id": "knowledge_store",
                "name": "เก็บความรู้",
                "description": "เก็บความรู้ในระบบ",
                "category": "knowledge",
                "component": "knowledge_manager",
                "command": "store_knowledge",
                "parameters": {"data": "object"},
                "examples": ["เก็บความรู้", "บันทึกข้อมูล", "เพิ่มความรู้"],
                "tags": ["knowledge", "store", "เก็บ", "บันทึก", "เพิ่ม"]
            },
            {
                "id": "knowledge_retrieve",
                "name": "ค้นหาความรู้",
                "description": "ค้นหาและดึงความรู้",
                "category": "knowledge",
                "component": "knowledge_manager",
                "command": "retrieve_knowledge",
                "parameters": {"query": "string"},
                "examples": ["ค้นหาความรู้", "หาข้อมูล", "ดึงความรู้"],
                "tags": ["knowledge", "retrieve", "ค้นหา", "หา", "ดึง"]
            },
            {
                "id": "supabase_query",
                "name": "ค้นหาข้อมูลในฐานข้อมูล",
                "description": "ค้นหาข้อมูลใน Supabase",
                "category": "database",
                "component": "supabase_integration",
                "command": "query_data",
                "parameters": {"table": "string", "query": "string"},
                "examples": ["ค้นหาข้อมูล", "ดึงข้อมูล", "query database"],
                "tags": ["database", "query", "ค้นหา", "ดึง", "supabase"]
            },
            {
                "id": "auto_learn",
                "name": "เรียนรู้อัตโนมัติ",
                "description": "เรียนรู้รูปแบบการใช้งานอัตโนมัติ",
                "category": "learning",
                "component": "auto_learning_manager",
                "command": "learn_pattern",
                "parameters": {"pattern": "string", "context": "object"},
                "examples": ["เรียนรู้รูปแบบ", "auto learn", "บันทึกพฤติกรรม"],
                "tags": ["learning", "auto", "เรียนรู้", "รูปแบบ", "พฤติกรรม"]
            }
        ]
        
        for cmd_data in default_commands:
            self.add_command(CommandDefinition(
                id=cmd_data["id"],
                name=cmd_data["name"],
                description=cmd_data["description"],
                category=cmd_data["category"],
                component=cmd_data["component"],
                command=cmd_data["command"],
                parameters=cmd_data["parameters"],
                examples=cmd_data["examples"],
                tags=cmd_data["tags"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ))
    
    def add_command(self, command: CommandDefinition):
        """เพิ่มคำสั่งใหม่"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO commands 
                (id, name, description, category, component, command, parameters, 
                 examples, tags, usage_count, success_rate, last_used, created_at, updated_at, 
                 is_active, requires_auth, timeout, retry_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                command.id, command.name, command.description, command.category,
                command.component, command.command, json.dumps(command.parameters),
                json.dumps(command.examples), json.dumps(command.tags),
                command.usage_count, command.success_rate, command.last_used,
                command.created_at, command.updated_at, command.is_active,
                command.requires_auth, command.timeout, command.retry_count
            ))
            conn.commit()
        
        # Clear cache
        self.command_cache.clear()
        logging.info(f"✅ Added command: {command.name}")
    
    def get_command(self, command_id: str) -> Optional[CommandDefinition]:
        """ดึงคำสั่งตาม ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM commands WHERE id = ?
            """, (command_id,))
            row = cursor.fetchone()
            
            if row:
                return CommandDefinition(
                    id=row[0], name=row[1], description=row[2], category=row[3],
                    component=row[4], command=row[5], parameters=json.loads(row[6]),
                    examples=json.loads(row[7]), tags=json.loads(row[8]),
                    usage_count=row[9], success_rate=row[10], last_used=row[11],
                    created_at=row[12], updated_at=row[13], is_active=bool(row[14]),
                    requires_auth=bool(row[15]), timeout=row[16], retry_count=row[17]
                )
        return None
    
    def get_commands_by_category(self, category: str) -> List[CommandDefinition]:
        """ดึงคำสั่งตามหมวดหมู่"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM commands WHERE category = ? AND is_active = 1
                ORDER BY usage_count DESC, name ASC
            """, (category,))
            
            commands = []
            for row in cursor.fetchall():
                commands.append(CommandDefinition(
                    id=row[0], name=row[1], description=row[2], category=row[3],
                    component=row[4], command=row[5], parameters=json.loads(row[6]),
                    examples=json.loads(row[7]), tags=json.loads(row[8]),
                    usage_count=row[9], success_rate=row[10], last_used=row[11],
                    created_at=row[12], updated_at=row[13], is_active=bool(row[14]),
                    requires_auth=bool(row[15]), timeout=row[16], retry_count=row[17]
                ))
        return commands
    
    def search_commands(self, query: str) -> List[CommandDefinition]:
        """ค้นหาคำสั่ง"""
        query = query.lower()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM commands WHERE is_active = 1 AND 
                (LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR 
                 LOWER(tags) LIKE ? OR LOWER(examples) LIKE ?)
                ORDER BY usage_count DESC, name ASC
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
            
            commands = []
            for row in cursor.fetchall():
                commands.append(CommandDefinition(
                    id=row[0], name=row[1], description=row[2], category=row[3],
                    component=row[4], command=row[5], parameters=json.loads(row[6]),
                    examples=json.loads(row[7]), tags=json.loads(row[8]),
                    usage_count=row[9], success_rate=row[10], last_used=row[11],
                    created_at=row[12], updated_at=row[13], is_active=bool(row[14]),
                    requires_auth=bool(row[15]), timeout=row[16], retry_count=row[17]
                ))
        return commands
    
    async def execute_command(self, user_input: str, user_id: Optional[str] = None, 
                            session_id: Optional[str] = None) -> Dict[str, Any]:
        """ประมวลผลคำสั่ง"""
        start_time = time.time()
        execution_id = hashlib.md5(f"{user_input}{time.time()}".encode()).hexdigest()
        
        try:
            # Find matching command
            command = await self.find_best_command(user_input)
            if not command:
                return {
                    "status": "error",
                    "message": "ไม่พบคำสั่งที่เหมาะสม",
                    "suggestions": await self.get_suggestions(user_input)
                }
            
            # Execute command
            component = self.components.get(command.component)
            if not component:
                return {
                    "status": "error",
                    "message": f"ไม่พบ component: {command.component}"
                }
            
            # Prepare parameters
            parameters = await self.extract_parameters(user_input, command)
            
            # Execute with retry
            result = None
            for attempt in range(command.retry_count):
                try:
                    result = await component.execute(command.command, parameters)
                    break
                except Exception as e:
                    if attempt == command.retry_count - 1:
                        raise e
                    await asyncio.sleep(1)
            
            execution_time = time.time() - start_time
            
            # Record execution
            execution = CommandExecution(
                id=execution_id,
                command_id=command.id,
                user_input=user_input,
                parameters=parameters,
                result=result,
                execution_time=execution_time,
                status="success",
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                session_id=session_id
            )
            
            await self.record_execution(execution)
            await self.update_command_stats(command.id, True)
            
            return {
                "status": "success",
                "command": command.name,
                "result": result,
                "execution_time": execution_time,
                "suggestions": await self.get_suggestions(user_input)
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record failed execution
            execution = CommandExecution(
                id=execution_id,
                command_id=command.id if command else "",
                user_input=user_input,
                parameters={},
                result={},
                execution_time=execution_time,
                status="error",
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                session_id=session_id
            )
            
            await self.record_execution(execution)
            if command:
                await self.update_command_stats(command.id, False)
            
            return {
                "status": "error",
                "message": str(e),
                "execution_time": execution_time,
                "suggestions": await self.get_suggestions(user_input)
            }
    
    async def find_best_command(self, user_input: str) -> Optional[CommandDefinition]:
        """หาคำสั่งที่เหมาะสมที่สุด"""
        # Check cache first
        if user_input in self.command_cache:
            return self.command_cache[user_input]
        
        # Search by patterns
        patterns = await self.get_patterns()
        best_match = None
        best_score = 0
        
        for pattern in patterns:
            score = self.calculate_pattern_score(user_input, pattern.pattern)
            if score > best_score and score > 0.7:  # Minimum confidence
                best_score = score
                best_match = self.get_command(pattern.command_id)
        
        # If no pattern match, search by keywords
        if not best_match:
            commands = self.search_commands(user_input)
            if commands:
                best_match = commands[0]
        
        # Cache result
        self.command_cache[user_input] = best_match
        return best_match
    
    def calculate_pattern_score(self, user_input: str, pattern: str) -> float:
        """คำนวณคะแนนความเหมาะสมของ pattern"""
        # Simple pattern matching for now
        user_words = set(user_input.lower().split())
        pattern_words = set(pattern.lower().split())
        
        if not pattern_words:
            return 0
        
        intersection = user_words.intersection(pattern_words)
        return len(intersection) / len(pattern_words)
    
    async def extract_parameters(self, user_input: str, command: CommandDefinition) -> Dict[str, Any]:
        """สกัดพารามิเตอร์จาก user input"""
        parameters = {}
        
        # Extract URL for chrome commands
        if command.category == "chrome" and "url" in command.parameters:
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, user_input)
            if urls:
                parameters["url"] = urls[0]
        
        # Extract selectors
        if "selector" in command.parameters:
            # Simple selector extraction
            if "ปุ่ม" in user_input or "button" in user_input.lower():
                parameters["selector"] = "button"
            elif "ลิงก์" in user_input or "link" in user_input.lower():
                parameters["selector"] = "a"
            elif "ช่อง" in user_input or "input" in user_input.lower():
                parameters["selector"] = "input"
        
        # Extract text
        if "text" in command.parameters:
            # Extract text after certain keywords
            text_keywords = ["พิมพ์", "กรอก", "ใส่", "type", "enter"]
            for keyword in text_keywords:
                if keyword in user_input:
                    parts = user_input.split(keyword)
                    if len(parts) > 1:
                        parameters["text"] = parts[1].strip()
                        break
        
        return parameters
    
    async def get_suggestions(self, user_input: str) -> List[Dict[str, Any]]:
        """ให้คำแนะนำคำสั่ง"""
        suggestions = []
        
        # Get popular commands
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, name, description, usage_count 
                FROM commands 
                WHERE is_active = 1 
                ORDER BY usage_count DESC 
                LIMIT 5
            """)
            
            for row in cursor.fetchall():
                suggestions.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "usage_count": row[3]
                })
        
        return suggestions
    
    async def record_execution(self, execution: CommandExecution):
        """บันทึกการประมวลผล"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO executions 
                (id, command_id, user_input, parameters, result, execution_time, 
                 status, error_message, timestamp, user_id, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution.id, execution.command_id, execution.user_input,
                json.dumps(execution.parameters), json.dumps(execution.result),
                execution.execution_time, execution.status, execution.error_message,
                execution.timestamp, execution.user_id, execution.session_id
            ))
            conn.commit()
    
    async def update_command_stats(self, command_id: str, success: bool):
        """อัปเดตสถิติคำสั่ง"""
        with sqlite3.connect(self.db_path) as conn:
            # Get current stats
            cursor = conn.execute("""
                SELECT usage_count, success_rate FROM commands WHERE id = ?
            """, (command_id,))
            row = cursor.fetchone()
            
            if row:
                usage_count = row[0] + 1
                current_success_rate = row[1]
                
                # Calculate new success rate
                if usage_count == 1:
                    new_success_rate = 1.0 if success else 0.0
                else:
                    total_success = current_success_rate * (usage_count - 1)
                    new_success_rate = (total_success + (1 if success else 0)) / usage_count
                
                # Update command
                conn.execute("""
                    UPDATE commands 
                    SET usage_count = ?, success_rate = ?, last_used = ?
                    WHERE id = ?
                """, (usage_count, new_success_rate, datetime.now().isoformat(), command_id))
                conn.commit()
    
    async def get_patterns(self) -> List[CommandPattern]:
        """ดึง patterns ทั้งหมด"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, pattern, command_id, confidence, usage_count, last_used
                FROM patterns ORDER BY confidence DESC, usage_count DESC
            """)
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append(CommandPattern(
                    id=row[0], pattern=row[1], command_id=row[2],
                    confidence=row[3], usage_count=row[4], last_used=row[5]
                ))
        return patterns
    
    def add_pattern(self, pattern: str, command_id: str, confidence: float = 0.8):
        """เพิ่ม pattern ใหม่"""
        pattern_id = hashlib.md5(f"{pattern}{command_id}".encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO patterns 
                (id, pattern, command_id, confidence, usage_count, last_used)
                VALUES (?, ?, ?, ?, 0, ?)
            """, (pattern_id, pattern, command_id, confidence, datetime.now().isoformat()))
            conn.commit()
    
    def start_background_tasks(self):
        """เริ่มงานในพื้นหลัง"""
        self.background_thread = threading.Thread(target=self._background_worker, daemon=True)
        self.background_thread.start()
    
    def _background_worker(self):
        """งานในพื้นหลัง"""
        while self.is_running:
            try:
                # Clean old executions (older than 30 days)
                with sqlite3.connect(self.db_path) as conn:
                    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
                    conn.execute("DELETE FROM executions WHERE timestamp < ?", (thirty_days_ago,))
                    conn.commit()
                
                # Update pattern usage
                self._update_pattern_usage()
                
                time.sleep(3600)  # Run every hour
                
            except Exception as e:
                logging.error(f"Background task error: {e}")
                time.sleep(60)
    
    def _update_pattern_usage(self):
        """อัปเดตการใช้งาน patterns"""
        with sqlite3.connect(self.db_path) as conn:
            # Get recent executions
            cursor = conn.execute("""
                SELECT user_input, command_id FROM executions 
                WHERE timestamp > ? ORDER BY timestamp DESC
            """, ((datetime.now() - timedelta(hours=1)).isoformat(),))
            
            for row in cursor.fetchall():
                user_input, command_id = row
                
                # Find matching patterns
                patterns = conn.execute("""
                    SELECT id, pattern FROM patterns WHERE command_id = ?
                """, (command_id,)).fetchall()
                
                for pattern_id, pattern in patterns:
                    if self.calculate_pattern_score(user_input, pattern) > 0.8:
                        conn.execute("""
                            UPDATE patterns 
                            SET usage_count = usage_count + 1, last_used = ?
                            WHERE id = ?
                        """, (datetime.now().isoformat(), pattern_id))
            
            conn.commit()
    
    def get_statistics(self) -> Dict[str, Any]:
        """ดึงสถิติระบบ"""
        with sqlite3.connect(self.db_path) as conn:
            # Total commands
            total_commands = conn.execute("SELECT COUNT(*) FROM commands WHERE is_active = 1").fetchone()[0]
            
            # Total executions
            total_executions = conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0]
            
            # Success rate
            success_executions = conn.execute("SELECT COUNT(*) FROM executions WHERE status = 'success'").fetchone()[0]
            overall_success_rate = (success_executions / total_executions * 100) if total_executions > 0 else 0
            
            # Popular commands
            popular_commands = conn.execute("""
                SELECT name, usage_count, success_rate 
                FROM commands 
                WHERE is_active = 1 
                ORDER BY usage_count DESC 
                LIMIT 10
            """).fetchall()
            
            # Recent executions
            recent_executions = conn.execute("""
                SELECT command_id, status, execution_time, timestamp
                FROM executions 
                ORDER BY timestamp DESC 
                LIMIT 20
            """).fetchall()
            
            return {
                "total_commands": total_commands,
                "total_executions": total_executions,
                "overall_success_rate": overall_success_rate,
                "popular_commands": [
                    {"name": cmd[0], "usage_count": cmd[1], "success_rate": cmd[2]}
                    for cmd in popular_commands
                ],
                "recent_executions": [
                    {"command_id": exe[0], "status": exe[1], "execution_time": exe[2], "timestamp": exe[3]}
                    for exe in recent_executions
                ]
            }
    
    def shutdown(self):
        """ปิดระบบ"""
        self.is_running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
        logging.info("🔄 Smart Command Hub shutdown complete")

# Global instance
smart_command_hub = SmartCommandHub() 