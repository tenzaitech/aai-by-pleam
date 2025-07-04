#!/usr/bin/env python3
"""
🇹🇭 WAWAGOD Thai Language Processor - ประมวลผลภาษาไทยแบบสมบูรณ์
รวม PyThaiNLP, EasyOCR, และ Thai Command Recognition
"""

import asyncio
import logging
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class WAWAGODThaiProcessor:
    """
    🇹🇭 WAWAGOD Thai Language Processor
    ประมวลผลภาษาไทยด้วย PyThaiNLP และ EasyOCR
    """
    
    def __init__(self):
        """เริ่มต้น Thai Language Processor"""
        self.logger = logging.getLogger('WAWAGOD.ThaiProcessor')
        self.initialized = False
        
        # Thai NLP Components
        self.pythainlp = None
        self.easyocr = None
        self.thai_tokenizer = None
        
        # Thai Command Mappings
        self.command_mappings = {
            'เปิด': 'open',
            'ปิด': 'close',
            'คลิก': 'click',
            'กรอก': 'fill',
            'ค้นหา': 'search',
            'รอ': 'wait',
            'ถ่าย': 'screenshot',
            'วิเคราะห์': 'analyze',
            'นำทาง': 'navigate',
            'เว็บไซต์': 'website',
            'ปุ่ม': 'button',
            'ฟอร์ม': 'form',
            'ข้อความ': 'text',
            'รูปภาพ': 'image',
            'หน้าจอ': 'screen'
        }
        
        # Thai Element Descriptions
        self.element_descriptions = {
            'ปุ่มค้นหา': 'search button',
            'ช่องค้นหา': 'search box',
            'ปุ่มเข้าสู่ระบบ': 'login button',
            'ช่องรหัสผ่าน': 'password field',
            'ช่องชื่อผู้ใช้': 'username field',
            'ปุ่มส่ง': 'submit button',
            'ลิงก์': 'link',
            'เมนู': 'menu',
            'แท็บ': 'tab'
        }
        
        self.logger.info("✅ WAWAGOD Thai Language Processor พร้อมใช้งาน")

    async def initialize(self):
        """เริ่มต้น Thai Language Processor"""
        try:
            self.logger.info("🔧 เริ่มต้น Thai Language Processor...")
            
            # โหลด PyThaiNLP แบบ Parallel
            await self._load_pythainlp()
            
            # โหลด EasyOCR แบบ Parallel
            await self._load_easyocr()
            
            # โหลด Thai Tokenizer แบบ Parallel
            await self._load_thai_tokenizer()
            
            self.initialized = True
            self.logger.info("✅ Thai Language Processor เริ่มต้นสำเร็จ")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการเริ่มต้น Thai Processor: {e}")
            return False

    async def _load_pythainlp(self):
        """โหลด PyThaiNLP"""
        try:
            import pythainlp
            self.pythainlp = pythainlp
            self.logger.info("✅ PyThaiNLP โหลดสำเร็จ")
        except ImportError:
            self.logger.warning("⚠️ PyThaiNLP ไม่ได้ติดตั้ง")
            self.pythainlp = None

    async def _load_easyocr(self):
        """โหลด EasyOCR"""
        try:
            import easyocr
            self.easyocr = easyocr.Reader(['th', 'en'])
            self.logger.info("✅ EasyOCR โหลดสำเร็จ")
        except ImportError:
            self.logger.warning("⚠️ EasyOCR ไม่ได้ติดตั้ง")
            self.easyocr = None

    async def _load_thai_tokenizer(self):
        """โหลด Thai Tokenizer"""
        try:
            if self.pythainlp:
                from pythainlp.tokenize import word_tokenize
                self.thai_tokenizer = word_tokenize
                self.logger.info("✅ Thai Tokenizer โหลดสำเร็จ")
            else:
                self.thai_tokenizer = None
        except Exception as e:
            self.logger.warning(f"⚠️ Thai Tokenizer: {e}")
            self.thai_tokenizer = None

    async def translate_command(self, thai_command: str) -> str:
        """แปลคำสั่งไทยเป็นอังกฤษ"""
        try:
            self.logger.info(f"🇹🇭 แปลคำสั่งไทย: {thai_command}")
            
            english_command = thai_command
            
            # แทนที่คำไทยด้วยคำอังกฤษ
            for thai_word, english_word in self.command_mappings.items():
                english_command = english_command.replace(thai_word, english_word)
            
            # แทนที่คำอธิบาย element
            for thai_desc, english_desc in self.element_descriptions.items():
                english_command = english_command.replace(thai_desc, english_desc)
            
            self.logger.info(f"✅ แปลคำสั่งสำเร็จ: {english_command}")
            return english_command
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการแปลคำสั่ง: {e}")
            return thai_command

    async def analyze_text(self, texts: List[str]) -> Dict[str, Any]:
        """วิเคราะห์ข้อความไทย"""
        try:
            self.logger.info(f"🔍 วิเคราะห์ข้อความไทย: {len(texts)} texts")
            
            analysis_result = {
                'total_texts': len(texts),
                'thai_texts': [],
                'english_texts': [],
                'mixed_texts': [],
                'keywords': [],
                'sentiment': 'neutral',
                'timestamp': datetime.now().isoformat()
            }
            
            for text in texts:
                # ตรวจสอบภาษา
                if self._is_thai_text(text):
                    analysis_result['thai_texts'].append(text)
                elif self._is_english_text(text):
                    analysis_result['english_texts'].append(text)
                else:
                    analysis_result['mixed_texts'].append(text)
                
                # สกัดคำสำคัญ
                keywords = await self._extract_keywords(text)
                analysis_result['keywords'].extend(keywords)
            
            # วิเคราะห์ sentiment
            analysis_result['sentiment'] = await self._analyze_sentiment(texts)
            
            self.logger.info("✅ วิเคราะห์ข้อความไทยเสร็จสิ้น")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการวิเคราะห์ข้อความ: {e}")
            return {}

    def _is_thai_text(self, text: str) -> bool:
        """ตรวจสอบว่าเป็นข้อความไทยหรือไม่"""
        thai_chars = re.findall(r'[\u0E00-\u0E7F]', text)
        return len(thai_chars) > len(text) * 0.3

    def _is_english_text(self, text: str) -> bool:
        """ตรวจสอบว่าเป็นข้อความอังกฤษหรือไม่"""
        english_chars = re.findall(r'[a-zA-Z]', text)
        return len(english_chars) > len(text) * 0.5

    async def _extract_keywords(self, text: str) -> List[str]:
        """สกัดคำสำคัญจากข้อความ"""
        try:
            keywords = []
            
            if self.thai_tokenizer and self._is_thai_text(text):
                # ใช้ Thai tokenizer
                tokens = self.thai_tokenizer(text)
                keywords = [token for token in tokens if len(token) > 1]
            else:
                # ใช้ regex สำหรับภาษาอังกฤษ
                words = re.findall(r'\b\w+\b', text.lower())
                keywords = [word for word in words if len(word) > 2]
            
            return keywords[:10]  # จำกัด 10 คำสำคัญ
            
        except Exception as e:
            self.logger.warning(f"⚠️ สกัดคำสำคัญ: {e}")
            return []

    async def _analyze_sentiment(self, texts: List[str]) -> str:
        """วิเคราะห์ sentiment ของข้อความ"""
        try:
            positive_words = ['ดี', 'ดีใจ', 'ยินดี', 'ขอบคุณ', 'ชอบ', 'ดีมาก', 'เยี่ยม']
            negative_words = ['ไม่ดี', 'แย่', 'เสียใจ', 'โกรธ', 'ไม่ชอบ', 'แย่มาก', 'น่าเบื่อ']
            
            positive_count = 0
            negative_count = 0
            
            for text in texts:
                for word in positive_words:
                    if word in text:
                        positive_count += 1
                
                for word in negative_words:
                    if word in text:
                        negative_count += 1
            
            if positive_count > negative_count:
                return 'positive'
            elif negative_count > positive_count:
                return 'negative'
            else:
                return 'neutral'
                
        except Exception as e:
            self.logger.warning(f"⚠️ วิเคราะห์ sentiment: {e}")
            return 'neutral'

    async def extract_thai_text(self, image_path: str) -> List[str]:
        """สกัดข้อความไทยจากรูปภาพ"""
        try:
            self.logger.info(f"🇹🇭 สกัดข้อความไทยจาก: {image_path}")
            
            if not self.easyocr:
                self.logger.warning("⚠️ EasyOCR ไม่พร้อมใช้งาน")
                return []
            
            # ใช้ EasyOCR สกัดข้อความ
            results = self.easyocr.readtext(image_path)
            
            thai_texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # ความเชื่อมั่น > 50%
                    thai_texts.append(text)
            
            self.logger.info(f"✅ สกัดข้อความไทยสำเร็จ: {len(thai_texts)} texts")
            return thai_texts
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการสกัดข้อความไทย: {e}")
            return []

    async def analyze_screenshot_content(self, texts: List[str]) -> Dict[str, Any]:
        """วิเคราะห์เนื้อหาของ screenshot"""
        try:
            self.logger.info(f"🔍 วิเคราะห์เนื้อหา screenshot: {len(texts)} texts")
            
            analysis = {
                'total_texts': len(texts),
                'thai_texts': [],
                'english_texts': [],
                'buttons': [],
                'links': [],
                'forms': [],
                'headings': [],
                'content': [],
                'timestamp': datetime.now().isoformat()
            }
            
            for text in texts:
                # จำแนกประเภทข้อความ
                if self._is_button_text(text):
                    analysis['buttons'].append(text)
                elif self._is_link_text(text):
                    analysis['links'].append(text)
                elif self._is_form_text(text):
                    analysis['forms'].append(text)
                elif self._is_heading_text(text):
                    analysis['headings'].append(text)
                else:
                    analysis['content'].append(text)
                
                # จำแนกภาษา
                if self._is_thai_text(text):
                    analysis['thai_texts'].append(text)
                elif self._is_english_text(text):
                    analysis['english_texts'].append(text)
            
            self.logger.info("✅ วิเคราะห์เนื้อหา screenshot เสร็จสิ้น")
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการวิเคราะห์เนื้อหา: {e}")
            return {}

    def _is_button_text(self, text: str) -> bool:
        """ตรวจสอบว่าเป็นข้อความปุ่มหรือไม่"""
        button_keywords = ['ปุ่ม', 'button', 'คลิก', 'click', 'ส่ง', 'submit', 'ตกลง', 'ok', 'ยกเลิก', 'cancel']
        return any(keyword in text.lower() for keyword in button_keywords)

    def _is_link_text(self, text: str) -> bool:
        """ตรวจสอบว่าเป็นข้อความลิงก์หรือไม่"""
        link_keywords = ['ลิงก์', 'link', 'http', 'www', '.com', '.th']
        return any(keyword in text.lower() for keyword in link_keywords)

    def _is_form_text(self, text: str) -> bool:
        """ตรวจสอบว่าเป็นข้อความฟอร์มหรือไม่"""
        form_keywords = ['ฟอร์ม', 'form', 'กรอก', 'fill', 'ชื่อ', 'name', 'รหัสผ่าน', 'password', 'อีเมล', 'email']
        return any(keyword in text.lower() for keyword in form_keywords)

    def _is_heading_text(self, text: str) -> bool:
        """ตรวจสอบว่าเป็นข้อความหัวข้อหรือไม่"""
        # ตรวจสอบความยาวและรูปแบบ
        return len(text) < 50 and (text.isupper() or text[0].isupper())

    async def process_natural_command(self, command: str) -> Dict[str, Any]:
        """ประมวลผลคำสั่งธรรมชาติภาษาไทย"""
        try:
            self.logger.info(f"🇹🇭 ประมวลผลคำสั่งธรรมชาติ: {command}")
            
            # แยกคำสั่ง
            tokens = await self._tokenize_command(command)
            
            # วิเคราะห์โครงสร้างคำสั่ง
            command_structure = await self._analyze_command_structure(tokens)
            
            # แปลเป็นคำสั่งที่ระบบเข้าใจ
            system_command = await self._convert_to_system_command(command_structure)
            
            result = {
                'original_command': command,
                'tokens': tokens,
                'structure': command_structure,
                'system_command': system_command,
                'confidence': 0.8,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info("✅ ประมวลผลคำสั่งธรรมชาติเสร็จสิ้น")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาดในการประมวลผลคำสั่ง: {e}")
            return {}

    async def _tokenize_command(self, command: str) -> List[str]:
        """แยกคำสั่งเป็น tokens"""
        try:
            if self.thai_tokenizer:
                return self.thai_tokenizer(command)
            else:
                return command.split()
        except Exception as e:
            self.logger.warning(f"⚠️ Tokenize command: {e}")
            return command.split()

    async def _analyze_command_structure(self, tokens: List[str]) -> Dict[str, Any]:
        """วิเคราะห์โครงสร้างคำสั่ง"""
        try:
            structure = {
                'action': None,
                'target': None,
                'parameters': {},
                'modifiers': []
            }
            
            for i, token in enumerate(tokens):
                # หา action
                if token in ['เปิด', 'ปิด', 'คลิก', 'กรอก', 'ค้นหา', 'รอ', 'ถ่าย', 'วิเคราะห์']:
                    structure['action'] = token
                
                # หา target
                elif token in ['เว็บไซต์', 'ปุ่ม', 'ฟอร์ม', 'ข้อความ', 'รูปภาพ', 'หน้าจอ']:
                    structure['target'] = token
                
                # หา parameters
                elif '=' in token:
                    key, value = token.split('=', 1)
                    structure['parameters'][key] = value
                
                # หา modifiers
                else:
                    structure['modifiers'].append(token)
            
            return structure
            
        except Exception as e:
            self.logger.warning(f"⚠️ Analyze command structure: {e}")
            return {}

    async def _convert_to_system_command(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """แปลงเป็นคำสั่งระบบ"""
        try:
            system_command = {
                'method': None,
                'args': {},
                'kwargs': {}
            }
            
            # แปลง action เป็น method
            action_mapping = {
                'เปิด': 'navigate_to',
                'ปิด': 'close_browser',
                'คลิก': 'click_element',
                'กรอก': 'fill_field',
                'ค้นหา': 'search',
                'รอ': 'wait_for',
                'ถ่าย': 'take_screenshot',
                'วิเคราะห์': 'analyze_page'
            }
            
            if structure.get('action') in action_mapping:
                system_command['method'] = action_mapping[structure['action']]
            
            # แปลง parameters
            system_command['args'] = structure.get('parameters', {})
            
            return system_command
            
        except Exception as e:
            self.logger.warning(f"⚠️ Convert to system command: {e}")
            return {}

    def get_status(self):
        """รับสถานะ"""
        return {
            'initialized': self.initialized,
            'pythainlp_loaded': self.pythainlp is not None,
            'easyocr_loaded': self.easyocr is not None,
            'tokenizer_loaded': self.thai_tokenizer is not None,
            'command_mappings': len(self.command_mappings),
            'element_descriptions': len(self.element_descriptions),
            'timestamp': datetime.now().isoformat()
        }

# Test Function
async def test_thai_processor():
    """ทดสอบ Thai Language Processor"""
    print("🧪 ทดสอบ WAWAGOD Thai Language Processor...")
    
    processor = WAWAGODThaiProcessor()
    
    # เริ่มต้น
    success = await processor.initialize()
    if not success:
        print("❌ เริ่มต้นล้มเหลว")
        return
    
    # ทดสอบการแปลคำสั่ง
    thai_command = "เปิดเว็บไซต์ Google แล้วคลิกที่ปุ่มค้นหา"
    english_command = await processor.translate_command(thai_command)
    print(f"🇹🇭 คำสั่งไทย: {thai_command}")
    print(f"🇺🇸 คำสั่งอังกฤษ: {english_command}")
    
    # ทดสอบการวิเคราะห์ข้อความ
    texts = ["สวัสดีครับ", "Hello world", "ปุ่มค้นหา", "กรอกข้อมูล"]
    analysis = await processor.analyze_text(texts)
    print(f"📊 การวิเคราะห์: {analysis}")
    
    # ทดสอบการประมวลผลคำสั่งธรรมชาติ
    natural_command = "เปิดเว็บไซต์ Google แล้วคลิกปุ่มค้นหา"
    result = await processor.process_natural_command(natural_command)
    print(f"🎯 ผลลัพธ์: {result}")
    
    print("✅ ทดสอบเสร็จสิ้น")

if __name__ == "__main__":
    asyncio.run(test_thai_processor()) 