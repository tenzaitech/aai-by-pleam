#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Command Hub - ศูนย์กลางคำสั่งอัจฉริยะ
"""

import json
import sqlite3
import asyncio
import logging
import subprocess
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import hashlib
import re
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CommandDefinition:
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

class SmartCommandHub:
    def __init__(self, db_path: str = "database/smart_command_hub.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.init_database()
        self.load_default_commands()
        
        logger.info("Smart Command Hub initialized successfully")
    
    def init_database(self):
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
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            conn.commit()
    
    def load_default_commands(self):
        default_commands = [
            {
                "id": "system_status",
                "name": "ตรวจสอบสถานะระบบ",
                "description": "ตรวจสอบสถานะระบบทั้งหมด",
                "category": "system",
                "component": "system",
                "command": "get_system_status",
                "parameters": {},
                "examples": ["ตรวจสอบระบบ", "สถานะระบบ", "system status"],
                "tags": ["system", "status", "ตรวจสอบ", "สถานะ"]
            },
            {
                "id": "cmd_execute",
                "name": "รันคำสั่ง CMD",
                "description": "รันคำสั่งผ่าน Command Prompt",
                "category": "system",
                "component": "system",
                "command": "execute_cmd",
                "parameters": {"command": "string", "working_dir": "string"},
                "examples": ["รันคำสั่ง", "execute command", "cmd"],
                "tags": ["system", "cmd", "execute", "รัน", "คำสั่ง"]
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
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO commands 
                (id, name, description, category, component, command, parameters, 
                 examples, tags, usage_count, success_rate, last_used, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                command.id, command.name, command.description, command.category,
                command.component, command.command, json.dumps(command.parameters),
                json.dumps(command.examples), json.dumps(command.tags),
                command.usage_count, command.success_rate, command.last_used,
                command.created_at, command.updated_at, command.is_active
            ))
            conn.commit()
        logger.info(f"Added command: {command.name}")
    
    def search_commands(self, query: str) -> List[CommandDefinition]:
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
                    created_at=row[12], updated_at=row[13], is_active=bool(row[14])
                ))
        return commands
    
    async def execute_command(self, user_input: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            # Find matching command
            commands = self.search_commands(user_input)
            if not commands:
                return {
                    "status": "error",
                    "message": "ไม่พบคำสั่งที่เหมาะสม"
                }
            
            command = commands[0]
            
            # Execute command
            if command.command == "get_system_status":
                result = await self.get_system_status()
            elif command.command == "execute_cmd":
                result = await self.execute_cmd_command(user_input)
            else:
                result = {"status": "success", "message": f"Mock execution of {command.command}"}
            
            execution_time = time.time() - start_time
            
            return {
                "status": "success",
                "command": command.name,
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "status": "error",
                "message": str(e),
                "execution_time": execution_time
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
                "disk_total": disk.total,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    async def execute_cmd_command(self, user_input: str) -> Dict[str, Any]:
        try:
            # Extract command from user input
            cmd_keywords = ["รัน", "execute", "run", "cmd", "คำสั่ง"]
            command = ""
            
            for keyword in cmd_keywords:
                if keyword in user_input:
                    parts = user_input.split(keyword)
                    if len(parts) > 1:
                        command = parts[1].strip()
                        break
            
            if not command:
                # Try to extract command directly
                words = user_input.split()
                if len(words) >= 2:
                    command = " ".join(words[1:])
            
            if not command:
                return {"error": "No command specified", "status": "error"}
            
            # Execute command using subprocess
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=30)
            
            return {
                "status": "success" if process.returncode == 0 else "error",
                "return_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            process.kill()
            return {"error": "Command timeout", "status": "error"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def get_statistics(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            total_commands = conn.execute("SELECT COUNT(*) FROM commands WHERE is_active = 1").fetchone()[0]
            
            popular_commands = conn.execute("""
                SELECT name, usage_count, success_rate 
                FROM commands 
                WHERE is_active = 1 
                ORDER BY usage_count DESC 
                LIMIT 10
            """).fetchall()
            
            return {
                "total_commands": total_commands,
                "popular_commands": [
                    {"name": cmd[0], "usage_count": cmd[1], "success_rate": cmd[2]}
                    for cmd in popular_commands
                ]
            }

# Global instance
smart_command_hub = SmartCommandHub()

if __name__ == "__main__":
    async def test_system():
        print("Testing Smart Command Hub...")
        
        # Test system status
        result = await smart_command_hub.execute_command("ตรวจสอบสถานะระบบ")
        print(f"System Status: {result}")
        
        # Test command search
        commands = smart_command_hub.search_commands("cmd")
        print(f"Found {len(commands)} cmd commands")
        
        # Test statistics
        stats = smart_command_hub.get_statistics()
        print(f"Statistics: {stats}")
        
        print("Smart Command Hub test completed")
    
    asyncio.run(test_system()) 