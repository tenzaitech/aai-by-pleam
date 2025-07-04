
"""
Full-Featured Thai Processor
ประมวลผลภาษาไทยแบบเต็มรูปแบบ
"""

from pythainlp import word_tokenize, sent_tokenize
from pythainlp.corpus import thai_stopwords
from pythainlp.util import normalize
import easyocr
import re
from typing import Dict, List, Tuple

class FullThaiProcessor:
    def __init__(self):
        self.ocr_reader = easyocr.Reader(['th', 'en'])
        self.stopwords = set(thai_stopwords())
        self.commands = self.load_thai_commands()
        self.elements = self.load_thai_elements()
        
    def load_thai_commands(self):
        """โหลดคำสั่งภาษาไทย"""
        return {
            'เปิด': 'open',
            'ปิด': 'close',
            'คลิก': 'click',
            'พิมพ์': 'type',
            'ไปที่': 'navigate',
            'ถ่ายภาพ': 'screenshot',
            'เลื่อน': 'scroll'
        }
        
    def load_thai_elements(self):
        """โหลด elements ภาษาไทย"""
        return {
            'ปุ่ม': 'button',
            'ลิงก์': 'link',
            'ช่องกรอก': 'input',
            'ฟอร์ม': 'form'
        }
        
    def process_natural_command(self, command):
        """ประมวลผลคำสั่งธรรมชาติ"""
        normalized = self.normalize_thai_text(command)
        tokens = self.tokenize_thai(normalized)
        return self.extract_full_command(tokens)
        
    def extract_full_command(self, tokens):
        """แยกคำสั่งแบบเต็มรูปแบบ"""
        command_info = {
            'action': None,
            'target': None,
            'parameters': {},
            'confidence': 0.0
        }
        
        # หาคำสั่งหลัก
        for token in tokens:
            if token in self.commands:
                command_info['action'] = self.commands[token]
                command_info['confidence'] += 0.3
                break
                
        # หา target
        for token in tokens:
            if token in self.elements:
                command_info['target'] = self.elements[token]
                command_info['confidence'] += 0.2
                break
                
        return command_info
        
    def ocr_advanced(self, image_path):
        """OCR แบบขั้นสูง"""
        results = self.ocr_reader.readtext(image_path)
        return self.process_ocr_results(results)
        
    def process_ocr_results(self, results):
        """ประมวลผลผลลัพธ์ OCR"""
        processed = []
        for bbox, text, confidence in results:
            if confidence > 0.5:
                processed.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox
                })
        return processed
