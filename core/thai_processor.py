
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
        
    def normalize_thai_text(self, text):
        """ทำให้ข้อความภาษาไทยเป็นมาตรฐาน"""
        return normalize(text)
        
    def tokenize_thai(self, text):
        """แยกคำภาษาไทย"""
        return word_tokenize(text)
        
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

    def process_thai_text(self, text: str) -> Dict[str, any]:
        """ประมวลผลข้อความภาษาไทย (Method ที่ระบบเรียกใช้)"""
        try:
            normalized = self.normalize_thai_text(text)
            tokens = self.tokenize_thai(normalized)
            result = {
                'original_text': text,
                'normalized_text': normalized,
                'tokens': tokens,
                'word_count': len(tokens),
                'sentences': sent_tokenize(text),
                'has_thai': any('\u0e00' <= char <= '\u0e7f' for char in text),
                'confidence': 0.9
            }
            # ตรวจสอบคำสั่ง
            command_info = self.process_natural_command(text)
            if command_info['action']:
                result['detected_command'] = command_info
            return result
        except Exception as e:
            return {
                'error': f'การประมวลผลข้อความผิดพลาด: {e}',
                'original_text': text,
                'confidence': 0.0
            }

    def analyze_thai_sentiment(self, text: str) -> Dict[str, any]:
        """วิเคราะห์ความรู้สึกของข้อความภาษาไทย"""
        try:
            positive_words = ['ดี', 'เยี่ยม', 'ยอดเยี่ยม', 'ชอบ', 'ดีใจ', 'สุข']
            negative_words = ['แย่', 'ไม่ดี', 'เสียใจ', 'โกรธ', 'หงุดหงิด']
            tokens = self.tokenize_thai(text)
            positive_count = sum(1 for token in tokens if token in positive_words)
            negative_count = sum(1 for token in tokens if token in negative_words)
            if positive_count > negative_count:
                sentiment = 'positive'
                score = positive_count / len(tokens) if tokens else 0
            elif negative_count > positive_count:
                sentiment = 'negative'
                score = negative_count / len(tokens) if tokens else 0
            else:
                sentiment = 'neutral'
                score = 0.0
            return {
                'text': text,
                'sentiment': sentiment,
                'score': score,
                'positive_words': positive_count,
                'negative_words': negative_count,
                'confidence': 0.8
            }
        except Exception as e:
            return {
                'error': f'การวิเคราะห์ความรู้สึกผิดพลาด: {e}',
                'text': text,
                'sentiment': 'unknown',
                'confidence': 0.0
            }

    def extract_thai_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """สกัดคำสำคัญจากข้อความภาษาไทย"""
        try:
            tokens = self.tokenize_thai(text)
            keywords = [
                token for token in tokens 
                if token not in self.stopwords 
                and len(token) > 1
                and not token.isdigit()
            ]
            from collections import Counter
            keyword_freq = Counter(keywords)
            return [word for word, freq in keyword_freq.most_common(max_keywords)]
        except Exception as e:
            print(f"❌ การสกัดคำสำคัญผิดพลาด: {e}")
            return []
