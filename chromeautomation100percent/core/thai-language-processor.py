"""
Thai Language Processor for Chrome Automation
ประมวลผลภาษาไทยสำหรับการควบคุม Chrome
"""

import re
from typing import Dict, List, Tuple, Optional
from pythainlp import word_tokenize, sent_tokenize
from pythainlp.corpus import thai_stopwords
from pythainlp.util import normalize
import easyocr
import logging

class ThaiLanguageProcessor:
    """
    ประมวลผลภาษาไทยสำหรับ Chrome Automation
    """
    
    def __init__(self):
        """เริ่มต้น Thai Language Processor"""
        self.stopwords = set(thai_stopwords())
        self.ocr_reader = easyocr.Reader(['th', 'en'])
        
        # คำสั่งภาษาไทยที่รู้จัก
        self.thai_commands = {
            # Browser Commands
            'เปิด': 'open',
            'ปิด': 'close',
            'ไปที่': 'navigate',
            'กลับ': 'back',
            'ไปข้างหน้า': 'forward',
            'รีเฟรช': 'refresh',
            'หยุด': 'stop',
            
            # Click Commands
            'คลิก': 'click',
            'ดับเบิลคลิก': 'double_click',
            'คลิกขวา': 'right_click',
            'กด': 'press',
            
            # Input Commands
            'พิมพ์': 'type',
            'กรอก': 'fill',
            'ลบ': 'clear',
            'เลือก': 'select',
            
            # Form Commands
            'กรอกฟอร์ม': 'fill_form',
            'ส่งฟอร์ม': 'submit_form',
            'ตรวจสอบ': 'verify',
            
            # Screenshot Commands
            'ถ่ายภาพ': 'screenshot',
            'บันทึกภาพ': 'save_screenshot',
            'ถ่ายหน้าจอ': 'capture_screen',
            
            # Wait Commands
            'รอ': 'wait',
            'รอให้': 'wait_for',
            'รอจนกว่า': 'wait_until',
            
            # Scroll Commands
            'เลื่อน': 'scroll',
            'เลื่อนขึ้น': 'scroll_up',
            'เลื่อนลง': 'scroll_down',
            'เลื่อนซ้าย': 'scroll_left',
            'เลื่อนขวา': 'scroll_right',
            
            # Tab Commands
            'แท็บใหม่': 'new_tab',
            'ปิดแท็บ': 'close_tab',
            'เปลี่ยนแท็บ': 'switch_tab',
            
            # Window Commands
            'หน้าต่างใหม่': 'new_window',
            'ปิดหน้าต่าง': 'close_window',
            'ย่อ': 'minimize',
            'ขยาย': 'maximize',
            
            # Element Commands
            'หา': 'find',
            'ค้นหา': 'search',
            'เลือก': 'select',
            'ลบ': 'delete',
            
            # AI Commands
            'วิเคราะห์': 'analyze',
            'เข้าใจ': 'understand',
            'แปล': 'translate',
            'สรุป': 'summarize'
        }
        
        # Elements ที่รู้จัก
        self.thai_elements = {
            'ปุ่ม': 'button',
            'ลิงก์': 'link',
            'ช่องกรอก': 'input',
            'ช่องค้นหา': 'search_box',
            'ฟอร์ม': 'form',
            'ตาราง': 'table',
            'รูปภาพ': 'image',
            'ข้อความ': 'text',
            'หัวข้อ': 'heading',
            'เมนู': 'menu',
            'รายการ': 'list',
            'กล่อง': 'box',
            'แท็บ': 'tab',
            'หน้าต่าง': 'window',
            'แถบ': 'bar',
            'ไอคอน': 'icon',
            'สัญลักษณ์': 'symbol',
            'เครื่องหมาย': 'mark'
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def normalize_thai_text(self, text: str) -> str:
        """ทำให้ข้อความภาษาไทยเป็นมาตรฐาน"""
        return normalize(text)
    
    def tokenize_thai(self, text: str) -> List[str]:
        """แยกคำภาษาไทย"""
        normalized_text = self.normalize_thai_text(text)
        tokens = word_tokenize(normalized_text)
        return [token for token in tokens if token not in self.stopwords]
    
    def extract_command(self, text: str) -> Dict[str, any]:
        """แยกคำสั่งจากข้อความภาษาไทย"""
        tokens = self.tokenize_thai(text.lower())
        
        command_info = {
            'action': None,
            'target': None,
            'parameters': {},
            'original_text': text,
            'confidence': 0.0
        }
        
        # หาคำสั่งหลัก
        for token in tokens:
            if token in self.thai_commands:
                command_info['action'] = self.thai_commands[token]
                command_info['confidence'] += 0.3
                break
        
        # หา target element
        for token in tokens:
            if token in self.thai_elements:
                command_info['target'] = self.thai_elements[token]
                command_info['confidence'] += 0.2
                break
        
        # หา URL หรือ path
        url_pattern = r'https?://[^\s]+|www\.[^\s]+'
        urls = re.findall(url_pattern, text)
        if urls:
            command_info['parameters']['url'] = urls[0]
            command_info['confidence'] += 0.2
        
        # หาข้อความที่ต้องพิมพ์
        if 'พิมพ์' in text or 'กรอก' in text:
            # หาข้อความที่อยู่ในเครื่องหมายคำพูด
            quoted_text = re.findall(r'["""]([^"""]+)["""]', text)
            if quoted_text:
                command_info['parameters']['text'] = quoted_text[0]
                command_info['confidence'] += 0.2
        
        return command_info
    
    def ocr_thai_text(self, image_path: str) -> List[str]:
        """อ่านข้อความภาษาไทยจากรูปภาพ"""
        try:
            results = self.ocr_reader.readtext(image_path)
            thai_texts = []
            
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # ความเชื่อมั่นมากกว่า 50%
                    thai_texts.append(text)
            
            return thai_texts
        except Exception as e:
            self.logger.error(f"OCR Error: {e}")
            return []
    
    def analyze_thai_screenshot(self, image_path: str) -> Dict[str, any]:
        """วิเคราะห์รูปภาพหน้าจอภาษาไทย"""
        thai_texts = self.ocr_thai_text(image_path)
        
        analysis = {
            'texts': thai_texts,
            'elements_found': [],
            'suggested_actions': [],
            'confidence': 0.0
        }
        
        # หา elements จากข้อความที่อ่านได้
        for text in thai_texts:
            for thai_element, english_element in self.thai_elements.items():
                if thai_element in text:
                    analysis['elements_found'].append({
                        'element': english_element,
                        'text': text,
                        'thai_name': thai_element
                    })
        
        # สร้างคำแนะนำ
        if analysis['elements_found']:
            analysis['suggested_actions'] = [
                f"คลิกที่ {element['thai_name']}" 
                for element in analysis['elements_found']
            ]
            analysis['confidence'] = 0.7
        
        return analysis
    
    def translate_command_to_english(self, thai_command: str) -> str:
        """แปลคำสั่งภาษาไทยเป็นภาษาอังกฤษ"""
        command_info = self.extract_command(thai_command)
        
        if command_info['action'] and command_info['target']:
            return f"{command_info['action']} {command_info['target']}"
        elif command_info['action']:
            return command_info['action']
        else:
            return "unknown_command"
    
    def understand_natural_language(self, text: str) -> Dict[str, any]:
        """เข้าใจคำสั่งธรรมชาติภาษาไทย"""
        # ทำให้ข้อความเป็นมาตรฐาน
        normalized_text = self.normalize_thai_text(text)
        
        # แยกคำสั่ง
        command_info = self.extract_command(normalized_text)
        
        # เพิ่มการวิเคราะห์บริบท
        context = self.analyze_context(normalized_text)
        
        return {
            'command': command_info,
            'context': context,
            'confidence': command_info['confidence'],
            'suggestions': self.generate_suggestions(command_info, context)
        }
    
    def analyze_context(self, text: str) -> Dict[str, any]:
        """วิเคราะห์บริบทของข้อความ"""
        context = {
            'urgency': 'normal',
            'precision': 'general',
            'scope': 'current_page'
        }
        
        # ตรวจสอบความเร่งด่วน
        urgent_words = ['ด่วน', 'เร็ว', 'ทันที', 'ตอนนี้']
        if any(word in text for word in urgent_words):
            context['urgency'] = 'high'
        
        # ตรวจสอบความแม่นยำ
        precise_words = ['ตรง', 'เฉพาะ', 'แน่นอน', 'ชัดเจน']
        if any(word in text for word in precise_words):
            context['precision'] = 'high'
        
        # ตรวจสอบขอบเขต
        if 'ทั้งหมด' in text or 'ทุก' in text:
            context['scope'] = 'all'
        
        return context
    
    def generate_suggestions(self, command_info: Dict, context: Dict) -> List[str]:
        """สร้างคำแนะนำจากคำสั่งและบริบท"""
        suggestions = []
        
        if command_info['action'] == 'click':
            suggestions.append("ตรวจสอบว่า element พร้อมสำหรับการคลิก")
            suggestions.append("รอให้ element โหลดเสร็จก่อนคลิก")
        
        elif command_info['action'] == 'fill_form':
            suggestions.append("ตรวจสอบข้อมูลก่อนกรอกฟอร์ม")
            suggestions.append("ตรวจสอบการ validate ของฟอร์ม")
        
        elif command_info['action'] == 'screenshot':
            suggestions.append("บันทึกภาพในโฟลเดอร์ที่เหมาะสม")
            suggestions.append("ตั้งชื่อไฟล์ที่มีความหมาย")
        
        if context['urgency'] == 'high':
            suggestions.append("ดำเนินการทันทีตามความเร่งด่วน")
        
        return suggestions
    
    def validate_thai_command(self, command: str) -> Tuple[bool, str]:
        """ตรวจสอบความถูกต้องของคำสั่งภาษาไทย"""
        command_info = self.extract_command(command)
        
        if command_info['confidence'] < 0.3:
            return False, "ไม่เข้าใจคำสั่ง กรุณาพูดใหม่"
        
        if not command_info['action']:
            return False, "ไม่พบคำสั่งที่ชัดเจน"
        
        return True, "คำสั่งถูกต้อง"
    
    def get_available_commands(self) -> Dict[str, List[str]]:
        """ส่งคืนคำสั่งที่ใช้ได้"""
        return {
            'browser_commands': list(self.thai_commands.keys())[:10],
            'element_types': list(self.thai_elements.keys()),
            'examples': [
                "เปิดเว็บไซต์ Google",
                "คลิกที่ปุ่มค้นหา",
                "กรอกข้อมูลในช่อง username",
                "ถ่ายภาพหน้าจอ",
                "เลื่อนลงไปดูเนื้อหา"
            ]
        }

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    processor = ThaiLanguageProcessor()
    
    # ทดสอบการแยกคำสั่ง
    test_commands = [
        "เปิดเว็บไซต์ Google",
        "คลิกที่ปุ่มค้นหา",
        "กรอกข้อมูลในช่อง username",
        "ถ่ายภาพหน้าจอ",
        "เลื่อนลงไปดูเนื้อหา"
    ]
    
    print("=== ทดสอบ Thai Language Processor ===")
    for command in test_commands:
        result = processor.extract_command(command)
        print(f"\nคำสั่ง: {command}")
        print(f"ผลลัพธ์: {result}")
    
    # ทดสอบคำสั่งที่ใช้ได้
    available = processor.get_available_commands()
    print(f"\n=== คำสั่งที่ใช้ได้ ===")
    print(f"Browser Commands: {available['browser_commands']}")
    print(f"Element Types: {available['element_types']}")
    print(f"Examples: {available['examples']}") 