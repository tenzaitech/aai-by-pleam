#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI AI Filter System
ระบบกรองและจัดหมวดหมู่ข้อมูลแบบยืดหยุ่น
"""

import os
import json
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import sqlite3
from pathlib import Path
import hashlib

class AIFilter:
    """ระบบกรองและจัดหมวดหมู่ข้อมูล"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.db_path = self.config.get('filter_database_path', 'ai_filter.db')
        self.init_database()
        self.categories = self._load_categories()
        self.keywords = self._load_keywords()
        
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """โหลดการตั้งค่า"""
        default_config = {
            'log_level': 'INFO',
            'filter_database_path': 'ai_filter.db',
            'auto_categorize': True,
            'keyword_matching': True,
            'sentiment_analysis': True,
            'priority_levels': ['high', 'medium', 'low'],
            'max_keywords_per_category': 50,
            'confidence_threshold': 0.7
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logging.error(f"ไม่สามารถโหลด config: {e}")
                
        return default_config
    
    def setup_logging(self):
        """ตั้งค่าระบบ logging"""
        log_dir = Path('conversation_logs/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.config['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'ai_filter.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AIFilter')
        
    def init_database(self):
        """สร้างฐานข้อมูลสำหรับ AI Filter"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ตารางหมวดหมู่
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'medium',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ตารางคำสำคัญ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                    keyword TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            
            # ตารางผลการกรอง
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS filter_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    category_id INTEGER,
                    confidence REAL,
                    keywords_found TEXT,
                    sentiment_score REAL,
                    priority TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("สร้างฐานข้อมูล AI Filter สำเร็จ")
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถสร้างฐานข้อมูล: {e}")
    
    def _load_categories(self) -> Dict[str, Dict[str, Any]]:
        """โหลดหมวดหมู่จากฐานข้อมูล"""
        categories = {}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM categories')
            rows = cursor.fetchall()
            
            for row in rows:
                categories[row[1]] = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'priority': row[3],
                    'created_at': row[4]
                }
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถโหลดหมวดหมู่: {e}")
            
        return categories
    
    def _load_keywords(self) -> Dict[int, List[Dict[str, Any]]]:
        """โหลดคำสำคัญจากฐานข้อมูล"""
        keywords = {}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM keywords')
            rows = cursor.fetchall()
            
            for row in rows:
                category_id = row[1]
                if category_id not in keywords:
                    keywords[category_id] = []
                    
                keywords[category_id].append({
                    'id': row[0],
                    'category_id': row[1],
                    'keyword': row[2],
                    'weight': row[3],
                    'created_at': row[4]
                })
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถโหลดคำสำคัญ: {e}")
            
        return keywords
    
    def add_category(self, name: str, description: str = None, 
                    priority: str = 'medium') -> bool:
        """เพิ่มหมวดหมู่ใหม่"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO categories (name, description, priority)
                VALUES (?, ?, ?)
            ''', (name, description, priority))
            
            category_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # อัปเดต cache
            self.categories[name] = {
                'id': category_id,
                'name': name,
                'description': description,
                'priority': priority,
                'created_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"เพิ่มหมวดหมู่สำเร็จ: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถเพิ่มหมวดหมู่: {e}")
            return False
    
    def add_keyword(self, category_name: str, keyword: str, 
                   weight: float = 1.0) -> bool:
        """เพิ่มคำสำคัญ"""
        try:
            if category_name not in self.categories:
                self.logger.error(f"ไม่พบหมวดหมู่: {category_name}")
                return False
            
            category_id = self.categories[category_name]['id']
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO keywords (category_id, keyword, weight)
                VALUES (?, ?, ?)
            ''', (category_id, keyword, weight))
            
            conn.commit()
            conn.close()
            
            # อัปเดต cache
            if category_id not in self.keywords:
                self.keywords[category_id] = []
                
            self.keywords[category_id].append({
                'id': cursor.lastrowid,
                'category_id': category_id,
                'keyword': keyword,
                'weight': weight,
                'created_at': datetime.now().isoformat()
            })
            
            self.logger.info(f"เพิ่มคำสำคัญสำเร็จ: {keyword} -> {category_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถเพิ่มคำสำคัญ: {e}")
            return False
    
    def filter_conversation(self, conversation_text: str, 
                          conversation_id: int = None) -> Dict[str, Any]:
        """กรองการสนทนา"""
        try:
            results = {
                'categories': [],
                'confidence_scores': {},
                'keywords_found': {},
                'sentiment_score': 0.0,
                'priority': 'low',
                'overall_confidence': 0.0
            }
            
            # วิเคราะห์หมวดหมู่
            for category_name, category_info in self.categories.items():
                category_id = category_info['id']
                confidence, keywords = self._analyze_category(
                    conversation_text, category_id
                )
                
                if confidence > 0:
                    results['categories'].append(category_name)
                    results['confidence_scores'][category_name] = confidence
                    results['keywords_found'][category_name] = keywords
            
            # คำนวณความมั่นใจรวม
            if results['confidence_scores']:
                results['overall_confidence'] = max(results['confidence_scores'].values())
            
            # วิเคราะห์ sentiment
            if self.config['sentiment_analysis']:
                results['sentiment_score'] = self._analyze_sentiment(conversation_text)
            
            # กำหนดความสำคัญ
            results['priority'] = self._determine_priority(results)
            
            # บันทึกผลลัพธ์
            if conversation_id:
                self._save_filter_result(conversation_id, results)
            
            self.logger.info(f"กรองการสนทนาสำเร็จ: {len(results['categories'])} หมวดหมู่")
            return results
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถกรองการสนทนา: {e}")
            return {}
    
    def _analyze_category(self, text: str, category_id: int) -> Tuple[float, List[str]]:
        """วิเคราะห์หมวดหมู่"""
        if category_id not in self.keywords:
            return 0.0, []
        
        found_keywords = []
        total_weight = 0.0
        matched_weight = 0.0
        
        for keyword_info in self.keywords[category_id]:
            keyword = keyword_info['keyword']
            weight = keyword_info['weight']
            total_weight += weight
            
            # ค้นหาคำสำคัญ (case-insensitive)
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            if pattern.search(text):
                found_keywords.append(keyword)
                matched_weight += weight
        
        confidence = matched_weight / total_weight if total_weight > 0 else 0.0
        return confidence, found_keywords
    
    def _analyze_sentiment(self, text: str) -> float:
        """วิเคราะห์ sentiment (แบบง่าย)"""
        positive_words = ['ดี', 'ดีใจ', 'ยินดี', 'ขอบคุณ', 'ชอบ', 'ดีมาก', 'เยี่ยม']
        negative_words = ['ไม่ดี', 'แย่', 'เสียใจ', 'โกรธ', 'ไม่ชอบ', 'แย่มาก', 'ห่วย']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        sentiment_score = (positive_count - negative_count) / total_words
        return max(-1.0, min(1.0, sentiment_score))  # จำกัดระหว่าง -1 ถึง 1
    
    def _determine_priority(self, results: Dict[str, Any]) -> str:
        """กำหนดความสำคัญ"""
        confidence = results.get('overall_confidence', 0.0)
        sentiment = abs(results.get('sentiment_score', 0.0))
        
        if confidence > 0.8 or sentiment > 0.7:
            return 'high'
        elif confidence > 0.5 or sentiment > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _save_filter_result(self, conversation_id: int, results: Dict[str, Any]):
        """บันทึกผลการกรอง"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for category_name in results['categories']:
                category_id = self.categories[category_name]['id']
                confidence = results['confidence_scores'][category_name]
                keywords = results['keywords_found'][category_name]
                
                cursor.execute('''
                    INSERT INTO filter_results 
                    (conversation_id, category_id, confidence, keywords_found, 
                     sentiment_score, priority)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (conversation_id, category_id, confidence, 
                     json.dumps(keywords), results['sentiment_score'], 
                     results['priority']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถบันทึกผลการกรอง: {e}")
    
    def get_filter_statistics(self, days: int = 7) -> Dict[str, Any]:
        """ดึงสถิติการกรอง"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.name, COUNT(fr.id), AVG(fr.confidence)
                FROM categories c
                LEFT JOIN filter_results fr ON c.id = fr.category_id
                WHERE fr.created_at >= datetime('now', '-{} days')
                GROUP BY c.id, c.name
                ORDER BY COUNT(fr.id) DESC
            '''.format(days))
            
            rows = cursor.fetchall()
            stats = {
                'category_stats': [],
                'total_filtered': 0,
                'avg_confidence': 0.0
            }
            
            total_count = 0
            total_confidence = 0.0
            
            for row in rows:
                category_name, count, avg_conf = row
                stats['category_stats'].append({
                    'category': category_name,
                    'count': count,
                    'avg_confidence': avg_conf or 0.0
                })
                total_count += count
                total_confidence += (avg_conf or 0.0) * count
            
            stats['total_filtered'] = total_count
            stats['avg_confidence'] = total_confidence / total_count if total_count > 0 else 0.0
            
            conn.close()
            return stats
            
        except Exception as e:
            self.logger.error(f"ไม่สามารถดึงสถิติการกรอง: {e}")
            return {}
    
    def setup_default_categories(self):
        """ตั้งค่าหมวดหมู่เริ่มต้น"""
        default_categories = [
            ('การพัฒนา', 'เกี่ยวกับการเขียนโค้ดและพัฒนาโปรแกรม', 'high'),
            ('การแก้ไขปัญหา', 'เกี่ยวกับการแก้ไขปัญหาและ troubleshooting', 'high'),
            ('การตั้งค่า', 'เกี่ยวกับการตั้งค่าระบบและ configuration', 'medium'),
            ('การทดสอบ', 'เกี่ยวกับการทดสอบและ debugging', 'medium'),
            ('การจัดการข้อมูล', 'เกี่ยวกับการจัดการและวิเคราะห์ข้อมูล', 'medium'),
            ('การเชื่อมต่อ', 'เกี่ยวกับการเชื่อมต่อ API และ services', 'low'),
            ('การสำรองข้อมูล', 'เกี่ยวกับการ backup และ restore', 'low'),
            ('การติดตั้ง', 'เกี่ยวกับการติดตั้งและ deployment', 'low')
        ]
        
        for name, description, priority in default_categories:
            if name not in self.categories:
                self.add_category(name, description, priority)
        
        # เพิ่มคำสำคัญเริ่มต้น
        self._add_default_keywords()
    
    def _add_default_keywords(self):
        """เพิ่มคำสำคัญเริ่มต้น"""
        keyword_mappings = {
            'การพัฒนา': ['code', 'programming', 'develop', 'เขียนโค้ด', 'พัฒนา', 'function', 'class'],
            'การแก้ไขปัญหา': ['error', 'bug', 'fix', 'แก้ไข', 'ปัญหา', 'troubleshoot', 'debug'],
            'การตั้งค่า': ['config', 'setting', 'ตั้งค่า', 'configuration', 'setup'],
            'การทดสอบ': ['test', 'debug', 'ทดสอบ', 'ตรวจสอบ', 'verify'],
            'การจัดการข้อมูล': ['data', 'database', 'ข้อมูล', 'จัดการ', 'analyze'],
            'การเชื่อมต่อ': ['connect', 'api', 'เชื่อมต่อ', 'integration', 'service'],
            'การสำรองข้อมูล': ['backup', 'restore', 'สำรอง', 'กู้คืน', 'save'],
            'การติดตั้ง': ['install', 'deploy', 'ติดตั้ง', 'deployment', 'setup']
        }
        
        for category, keywords in keyword_mappings.items():
            for keyword in keywords:
                self.add_keyword(category, keyword)

if __name__ == "__main__":
    # ทดสอบระบบ
    filter_system = AIFilter()
    filter_system.setup_default_categories()
    
    # ทดสอบกรองข้อความ
    test_text = "ช่วยแก้ไขปัญหา error ในโค้ด Python ให้หน่อยครับ"
    result = filter_system.filter_conversation(test_text)
    
    print("ผลการกรอง:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # แสดงสถิติ
    stats = filter_system.get_filter_statistics()
    print("\nสถิติการกรอง:")
    print(json.dumps(stats, indent=2, ensure_ascii=False)) 