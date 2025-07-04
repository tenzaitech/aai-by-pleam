#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Learning Manager
ระบบเรียนรู้อัตโนมัติจากพฤติกรรมของผู้ใช้
"""

import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from collections import defaultdict, Counter
import sqlite3
import threading

class AutoLearningManager:
    """ระบบเรียนรู้อัตโนมัติ"""
    
    def __init__(self, base_path: str = "auto_learning_data"):
        self.base_path = base_path
        self.db_path = os.path.join(base_path, "auto_learning.db")
        self.patterns_file = os.path.join(base_path, "learning_patterns.json")
        self.behaviors_file = os.path.join(base_path, "user_behaviors.json")
        
        self.logger = logging.getLogger(__name__)
        
        # สร้างโฟลเดอร์
        os.makedirs(base_path, exist_ok=True)
        
        # ตั้งค่าฐานข้อมูล
        self._init_database()
        
        # โหลดข้อมูล
        self.patterns = self._load_patterns()
        self.behaviors = self._load_behaviors()
        
        # ตั้งค่าการเรียนรู้
        self.learning_enabled = True
        self.min_confidence = 0.7
        self.min_frequency = 3
        self.pattern_lifetime_days = 30
        
        # Thread lock สำหรับ thread safety
        self.lock = threading.Lock()
        
        # เริ่ม background learning thread
        self._start_background_learning()
        
        self.logger.info("🧠 Auto Learning Manager initialized")
    
    def _init_database(self):
        """สร้างฐานข้อมูล SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ตาราง patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT UNIQUE,
                pattern_type TEXT,
                pattern_data TEXT,
                frequency INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 0.0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence_score REAL DEFAULT 0.0,
                tags TEXT
            )
        ''')
        
        # ตาราง user behaviors
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_behaviors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                behavior_id TEXT UNIQUE,
                user_id TEXT,
                action_type TEXT,
                action_data TEXT,
                context TEXT,
                timestamp TIMESTAMP,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ตาราง learning sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                user_id TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                patterns_learned INTEGER DEFAULT 0,
                behaviors_recorded INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # สร้าง indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_type ON learning_patterns(pattern_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON learning_patterns(confidence_score)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_behaviors_user ON user_behaviors(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_behaviors_type ON user_behaviors(action_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_behaviors_timestamp ON user_behaviors(timestamp)')
        
        conn.commit()
        conn.close()
    
    def _load_patterns(self) -> Dict[str, Any]:
        """โหลด patterns จากไฟล์"""
        try:
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading patterns: {e}")
        return {}
    
    def _save_patterns(self):
        """บันทึก patterns ลงไฟล์"""
        try:
            with self.lock:
                with open(self.patterns_file, 'w', encoding='utf-8') as f:
                    json.dump(self.patterns, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving patterns: {e}")
    
    def _load_behaviors(self) -> List[Dict[str, Any]]:
        """โหลด behaviors จากไฟล์"""
        try:
            if os.path.exists(self.behaviors_file):
                with open(self.behaviors_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading behaviors: {e}")
        return []
    
    def _save_behaviors(self):
        """บันทึก behaviors ลงไฟล์"""
        try:
            with self.lock:
                with open(self.behaviors_file, 'w', encoding='utf-8') as f:
                    json.dump(self.behaviors, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving behaviors: {e}")
    
    def record_behavior(self, user_id: str, action_type: str, action_data: Dict[str, Any], 
                       context: Dict[str, Any] = None, session_id: str = None) -> str:
        """บันทึกพฤติกรรมของผู้ใช้"""
        if not self.learning_enabled:
            return ""
        
        try:
            behavior_id = hashlib.md5(
                f"{user_id}_{action_type}_{time.time()}".encode()
            ).hexdigest()[:12]
            
            behavior = {
                "behavior_id": behavior_id,
                "user_id": user_id,
                "action_type": action_type,
                "action_data": action_data,
                "context": context or {},
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id or "default"
            }
            
            with self.lock:
                self.behaviors.append(behavior)
                self._save_behaviors()
            
            # บันทึกลงฐานข้อมูล
            self._save_behavior_to_db(behavior)
            
            self.logger.info(f"📝 Recorded behavior: {action_type} for user {user_id}")
            return behavior_id
            
        except Exception as e:
            self.logger.error(f"Error recording behavior: {e}")
            return ""
    
    def _save_behavior_to_db(self, behavior: Dict[str, Any]):
        """บันทึก behavior ลงฐานข้อมูล"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_behaviors 
                (behavior_id, user_id, action_type, action_data, context, timestamp, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                behavior["behavior_id"],
                behavior["user_id"],
                behavior["action_type"],
                json.dumps(behavior["action_data"]),
                json.dumps(behavior["context"]),
                behavior["timestamp"],
                behavior["session_id"]
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving behavior to DB: {e}")
    
    def learn_from_behaviors(self, user_id: str = None, time_window_hours: int = 24) -> List[Dict[str, Any]]:
        """เรียนรู้จากพฤติกรรม"""
        if not self.learning_enabled:
            return []
        
        try:
            # กรอง behaviors ตาม user_id และ time window
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            relevant_behaviors = [
                b for b in self.behaviors
                if (user_id is None or b["user_id"] == user_id) and 
                datetime.fromisoformat(b["timestamp"]) >= cutoff_time
            ]
            
            if not relevant_behaviors:
                return []
            
            # วิเคราะห์ patterns
            patterns = []
            
            # 1. Command patterns
            command_patterns = self._analyze_command_patterns(relevant_behaviors)
            patterns.extend(command_patterns)
            
            # 2. Workflow patterns
            workflow_patterns = self._analyze_workflow_patterns(relevant_behaviors)
            patterns.extend(workflow_patterns)
            
            # 3. Error fix patterns
            error_patterns = self._analyze_error_patterns(relevant_behaviors)
            patterns.extend(error_patterns)
            
            # 4. Preference patterns
            preference_patterns = self._analyze_preference_patterns(relevant_behaviors)
            patterns.extend(preference_patterns)
            
            # บันทึก patterns ใหม่
            for pattern in patterns:
                self._save_pattern(pattern)
            
            self.logger.info(f"🧠 Learned {len(patterns)} new patterns")
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error learning from behaviors: {e}")
            return []
    
    def _analyze_command_patterns(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """วิเคราะห์ patterns ของคำสั่ง"""
        patterns = []
        
        # จัดกลุ่มตาม command type
        command_groups = defaultdict(list)
        for behavior in behaviors:
            if behavior["action_type"] == "command":
                command_type = behavior["action_data"].get("command_type", "unknown")
                command_groups[command_type].append(behavior)
        
        # วิเคราะห์แต่ละกลุ่ม
        for command_type, group_behaviors in command_groups.items():
            if len(group_behaviors) >= self.min_frequency:
                # คำนวณ success rate
                success_count = sum(1 for b in group_behaviors 
                                  if b["action_data"].get("success", False))
                success_rate = success_count / len(group_behaviors)
                
                # สร้าง pattern
                pattern_id = hashlib.md5(f"command_{command_type}".encode()).hexdigest()[:12]
                pattern = {
                    "pattern_id": pattern_id,
                    "pattern_type": "command",
                    "pattern_data": {
                        "command_type": command_type,
                        "common_parameters": self._extract_common_parameters(group_behaviors),
                        "average_execution_time": self._calculate_avg_execution_time(group_behaviors)
                    },
                    "frequency": len(group_behaviors),
                    "success_rate": success_rate,
                    "last_used": max(b["timestamp"] for b in group_behaviors),
                    "created_at": datetime.now().isoformat(),
                    "confidence_score": min(success_rate * (len(group_behaviors) / 10), 1.0),
                    "tags": ["command", command_type]
                }
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_workflow_patterns(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """วิเคราะห์ patterns ของ workflow"""
        patterns = []
        
        # หา sequences ของ actions
        session_sequences = defaultdict(list)
        for behavior in behaviors:
            session_sequences[behavior["session_id"]].append(behavior)
        
        # วิเคราะห์ sequences
        for session_id, session_behaviors in session_sequences.items():
            if len(session_behaviors) >= 3:  # ต้องมีอย่างน้อย 3 actions
                # หา subsequences ที่เกิดขึ้นบ่อย
                sequences = self._extract_sequences(session_behaviors)
                
                for sequence, count in sequences.items():
                    if count >= self.min_frequency:
                        pattern_id = hashlib.md5(f"workflow_{sequence}".encode()).hexdigest()[:12]
                        pattern = {
                            "pattern_id": pattern_id,
                            "pattern_type": "workflow",
                            "pattern_data": {
                                "sequence": sequence,
                                "actions": self._parse_sequence(sequence),
                                "average_duration": self._calculate_sequence_duration(session_behaviors, sequence)
                            },
                            "frequency": count,
                            "success_rate": 1.0,  # Workflow patterns มักจะสำเร็จ
                            "last_used": datetime.now().isoformat(),
                            "created_at": datetime.now().isoformat(),
                            "confidence_score": min(count / 10, 1.0),
                            "tags": ["workflow", "sequence"]
                        }
                        patterns.append(pattern)
        
        return patterns
    
    def _analyze_error_patterns(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """วิเคราะห์ patterns ของการแก้ไขข้อผิดพลาด"""
        patterns = []
        
        # หา error behaviors
        error_behaviors = [b for b in behaviors if b["action_type"] == "error"]
        
        if len(error_behaviors) >= self.min_frequency:
            # จัดกลุ่มตาม error type
            error_groups = defaultdict(list)
            for behavior in error_behaviors:
                error_type = behavior["action_data"].get("error_type", "unknown")
                error_groups[error_type].append(behavior)
            
            # วิเคราะห์การแก้ไข
            for error_type, group_behaviors in error_groups.items():
                if len(group_behaviors) >= 2:
                    # หา solution patterns
                    solutions = self._extract_solution_patterns(group_behaviors)
                    
                    for solution, count in solutions.items():
                        pattern_id = hashlib.md5(f"error_fix_{error_type}_{solution}".encode()).hexdigest()[:12]
                        pattern = {
                            "pattern_id": pattern_id,
                            "pattern_type": "error_fix",
                            "pattern_data": {
                                "error_type": error_type,
                                "solution": solution,
                                "fix_steps": self._parse_solution(solution)
                            },
                            "frequency": count,
                            "success_rate": 1.0,  # Error fix patterns มักจะสำเร็จ
                            "last_used": datetime.now().isoformat(),
                            "created_at": datetime.now().isoformat(),
                            "confidence_score": min(count / 5, 1.0),
                            "tags": ["error_fix", error_type]
                        }
                        patterns.append(pattern)
        
        return patterns
    
    def _analyze_preference_patterns(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """วิเคราะห์ patterns ของความชอบ"""
        patterns = []
        
        # วิเคราะห์ preferences จาก context
        preference_data = defaultdict(list)
        for behavior in behaviors:
            if behavior["context"]:
                for key, value in behavior["context"].items():
                    if key.startswith("pref_"):
                        preference_data[key].append(value)
        
        # สร้าง preference patterns
        for pref_key, values in preference_data.items():
            if len(values) >= self.min_frequency:
                # หาค่าที่ใช้บ่อยที่สุด
                most_common = Counter(values).most_common(1)[0]
                
                pattern_id = hashlib.md5(f"preference_{pref_key}".encode()).hexdigest()[:12]
                pattern = {
                    "pattern_id": pattern_id,
                    "pattern_type": "preference",
                    "pattern_data": {
                        "preference_key": pref_key,
                        "preferred_value": most_common[0],
                        "usage_count": most_common[1],
                        "all_values": list(set(values))
                    },
                    "frequency": len(values),
                    "success_rate": 1.0,
                    "last_used": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                    "confidence_score": min(most_common[1] / len(values), 1.0),
                    "tags": ["preference", pref_key]
                }
                patterns.append(pattern)
        
        return patterns
    
    def _extract_common_parameters(self, behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """สกัด parameters ที่ใช้บ่อย"""
        param_counts = defaultdict(Counter)
        
        for behavior in behaviors:
            params = behavior["action_data"].get("parameters", {})
            for key, value in params.items():
                param_counts[key][str(value)] += 1
        
        common_params = {}
        for param, counts in param_counts.items():
            most_common = counts.most_common(1)[0]
            if most_common[1] >= len(behaviors) * 0.5:  # ใช้บ่อยกว่า 50%
                common_params[param] = most_common[0]
        
        return common_params
    
    def _calculate_avg_execution_time(self, behaviors: List[Dict[str, Any]]) -> float:
        """คำนวณเวลาการทำงานเฉลี่ย"""
        times = []
        for behavior in behaviors:
            exec_time = behavior["action_data"].get("execution_time", 0)
            if exec_time > 0:
                times.append(exec_time)
        
        return sum(times) / len(times) if times else 0
    
    def _extract_sequences(self, behaviors: List[Dict[str, Any]]) -> Dict[str, int]:
        """สกัด sequences จาก behaviors"""
        sequences = Counter()
        
        # สร้าง sequences ขนาด 2-4 actions
        for seq_len in range(2, min(5, len(behaviors) + 1)):
            for i in range(len(behaviors) - seq_len + 1):
                seq = behaviors[i:i+seq_len]
                seq_str = "->".join(b["action_type"] for b in seq)
                sequences[seq_str] += 1
        
        return sequences
    
    def _parse_sequence(self, sequence: str) -> List[str]:
        """แปลง sequence string เป็น list"""
        return sequence.split("->")
    
    def _calculate_sequence_duration(self, behaviors: List[Dict[str, Any]], sequence: str) -> float:
        """คำนวณเวลาของ sequence"""
        actions = self._parse_sequence(sequence)
        total_duration = 0
        
        for i in range(len(behaviors) - len(actions) + 1):
            if [b["action_type"] for b in behaviors[i:i+len(actions)]] == actions:
                start_time = datetime.fromisoformat(behaviors[i]["timestamp"])
                end_time = datetime.fromisoformat(behaviors[i+len(actions)-1]["timestamp"])
                total_duration += (end_time - start_time).total_seconds()
        
        return total_duration
    
    def _extract_solution_patterns(self, error_behaviors: List[Dict[str, Any]]) -> Dict[str, int]:
        """สกัด patterns ของการแก้ไข"""
        solutions = Counter()
        
        for behavior in error_behaviors:
            solution = behavior["action_data"].get("solution", "")
            if solution:
                solutions[solution] += 1
        
        return solutions
    
    def _parse_solution(self, solution: str) -> List[str]:
        """แปลง solution string เป็น list"""
        return solution.split(";") if ";" in solution else [solution]
    
    def _save_pattern(self, pattern: Dict[str, Any]):
        """บันทึก pattern"""
        with self.lock:
            # อัปเดตหรือเพิ่ม pattern
            if pattern["pattern_id"] in self.patterns:
                existing = self.patterns[pattern["pattern_id"]]
                existing["frequency"] += pattern["frequency"]
                existing["success_rate"] = (existing["success_rate"] + pattern["success_rate"]) / 2
                existing["last_used"] = pattern["last_used"]
                existing["confidence_score"] = max(existing["confidence_score"], pattern["confidence_score"])
            else:
                self.patterns[pattern["pattern_id"]] = pattern
            
            self._save_patterns()
            
            # บันทึกลงฐานข้อมูล
            self._save_pattern_to_db(pattern)
    
    def _save_pattern_to_db(self, pattern: Dict[str, Any]):
        """บันทึก pattern ลงฐานข้อมูล"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO learning_patterns 
                (pattern_id, pattern_type, pattern_data, frequency, success_rate, 
                 last_used, confidence_score, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern["pattern_id"],
                pattern["pattern_type"],
                json.dumps(pattern["pattern_data"]),
                pattern["frequency"],
                pattern["success_rate"],
                pattern["last_used"],
                pattern["confidence_score"],
                json.dumps(pattern["tags"])
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving pattern to DB: {e}")
    
    def get_recommendations(self, user_id: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """ดึงคำแนะนำจาก patterns ที่เรียนรู้"""
        try:
            # กรอง patterns ที่มี confidence สูงพอ
            high_confidence_patterns = [
                p for p in self.patterns.values()
                if p["confidence_score"] >= self.min_confidence
            ]
            
            recommendations = []
            
            for pattern in high_confidence_patterns:
                recommendation = {
                    "pattern_id": pattern["pattern_id"],
                    "pattern_type": pattern["pattern_type"],
                    "confidence": pattern["confidence_score"],
                    "frequency": pattern["frequency"],
                    "success_rate": pattern["success_rate"],
                    "recommendation": self._generate_recommendation(pattern, context),
                    "tags": pattern["tags"]
                }
                recommendations.append(recommendation)
            
            # เรียงตาม confidence และ frequency
            recommendations.sort(key=lambda x: (x["confidence"], x["frequency"]), reverse=True)
            
            return recommendations[:10]  # ส่งคืน 10 อันดับแรก
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            return []
    
    def _generate_recommendation(self, pattern: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """สร้างคำแนะนำจาก pattern"""
        if pattern["pattern_type"] == "command":
            return f"แนะนำใช้คำสั่ง {pattern['pattern_data'].get('command_type', 'unknown')} (ความสำเร็จ {pattern['success_rate']:.1%})"
        elif pattern["pattern_type"] == "workflow":
            return f"แนะนำ workflow: {' -> '.join(pattern['pattern_data'].get('actions', []))}"
        elif pattern["pattern_type"] == "error_fix":
            return f"วิธีแก้ไข {pattern['pattern_data'].get('error_type', 'unknown')}: {pattern['pattern_data'].get('solution', '')}"
        elif pattern["pattern_type"] == "preference":
            return f"แนะนำค่า {pattern['pattern_data'].get('preferred_value', '')} สำหรับ {pattern['pattern_data'].get('preference_key', '')}"
        else:
            return f"คำแนะนำจาก pattern {pattern['pattern_type']}"
    
    def _start_background_learning(self):
        """เริ่ม background learning thread"""
        def background_learning():
            while self.learning_enabled:
                try:
                    # เรียนรู้ทุก 30 นาที
                    time.sleep(1800)
                    self.learn_from_behaviors()
                    
                    # ลบ patterns เก่า
                    self._cleanup_old_patterns()
                    
                except Exception as e:
                    self.logger.error(f"Background learning error: {e}")
        
        thread = threading.Thread(target=background_learning, daemon=True)
        thread.start()
    
    def _cleanup_old_patterns(self):
        """ลบ patterns เก่า"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.pattern_lifetime_days)
            
            with self.lock:
                old_patterns = [
                    pattern_id for pattern_id, pattern in self.patterns.items()
                    if datetime.fromisoformat(pattern["last_used"]) < cutoff_date and pattern["frequency"] < self.min_frequency
                ]
                
                for pattern_id in old_patterns:
                    del self.patterns[pattern_id]
                
                if old_patterns:
                    self._save_patterns()
                    self.logger.info(f"🧹 Cleaned up {len(old_patterns)} old patterns")
        
        except Exception as e:
            self.logger.error(f"Error cleaning up patterns: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """ดึงสถิติของระบบ"""
        try:
            with self.lock:
                total_patterns = len(self.patterns)
                total_behaviors = len(self.behaviors)
                
                pattern_types = Counter(p["pattern_type"] for p in self.patterns.values())
                behavior_types = Counter(b["action_type"] for b in self.behaviors)
                
                avg_confidence = sum(p["confidence_score"] for p in self.patterns.values()) / total_patterns if total_patterns > 0 else 0
                avg_success_rate = sum(p["success_rate"] for p in self.patterns.values()) / total_patterns if total_patterns > 0 else 0
                
                return {
                    "total_patterns": total_patterns,
                    "total_behaviors": total_behaviors,
                    "pattern_types": dict(pattern_types),
                    "behavior_types": dict(behavior_types),
                    "average_confidence": round(avg_confidence, 3),
                    "average_success_rate": round(avg_success_rate, 3),
                    "learning_enabled": self.learning_enabled,
                    "min_confidence": self.min_confidence,
                    "min_frequency": self.min_frequency
                }
        
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    def export_learning_data(self, export_path: str = None) -> str:
        """ส่งออกข้อมูลการเรียนรู้"""
        try:
            if export_path is None:
                export_path = os.path.join(self.base_path, f"learning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            export_data = {
                "metadata": {
                    "export_time": datetime.now().isoformat(),
                    "total_patterns": len(self.patterns),
                    "total_behaviors": len(self.behaviors)
                },
                "patterns": self.patterns,
                "behaviors": self.behaviors
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"📤 Exported learning data to: {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Error exporting learning data: {e}")
            return ""
    
    def import_learning_data(self, import_path: str) -> bool:
        """นำเข้าข้อมูลการเรียนรู้"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            with self.lock:
                # Import patterns
                self.patterns.update(import_data.get("patterns", {}))
                
                # Import behaviors
                self.behaviors.extend(import_data.get("behaviors", []))
                
                self._save_patterns()
                self._save_behaviors()
            
            self.logger.info(f"📥 Imported learning data from: {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing learning data: {e}")
            return False 