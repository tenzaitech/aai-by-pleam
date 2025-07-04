"""
Multimodal AI Integration
เชื่อมต่อกับ AI แบบ Multimodal (Local Processing)
"""

import base64
from typing import Dict, Any, List
import cv2
import numpy as np
import json
import re
from pathlib import Path

class MultimodalAIIntegration:
    def __init__(self, api_key=None):
        """เริ่มต้น AI Integration (ไม่ต้องใช้ OpenAI API)"""
        self.api_key = api_key
        self.use_openai = api_key is not None and api_key.strip() != ""
        
        if self.use_openai:
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key)
                print("🤖 ใช้ OpenAI API สำหรับ AI Integration")
            except Exception as e:
                print(f"⚠️ ไม่สามารถใช้ OpenAI API: {e}")
                self.use_openai = False
        
        if not self.use_openai:
            print("🧠 ใช้ Local AI Processing แทน OpenAI API")
        
    async def analyze_multimodal(self, images: List[str], text: str, prompt: str):
        """วิเคราะห์แบบ Multimodal"""
        if self.use_openai:
            return await self._analyze_with_openai(images, text, prompt)
        else:
            return await self._analyze_local(images, text, prompt)
    
    async def _analyze_with_openai(self, images: List[str], text: str, prompt: str):
        """วิเคราะห์ด้วย OpenAI API"""
        try:
            content = [{"type": "text", "text": prompt + "\n\n" + text}]
            
            for image_path in images:
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                    })
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[{"role": "user", "content": content}],
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ OpenAI API Error: {e}")
            return await self._analyze_local(images, text, prompt)
    
    async def _analyze_local(self, images: List[str], text: str, prompt: str):
        """วิเคราะห์แบบ Local Processing"""
        analysis = {
            "prompt": prompt,
            "text_input": text,
            "images_analyzed": len(images),
            "analysis": "Local AI Processing - Basic Analysis",
            "confidence": 0.7
        }
        
        # วิเคราะห์รูปภาพแบบพื้นฐาน
        for i, image_path in enumerate(images):
            img_analysis = await self._analyze_image_local(image_path)
            analysis[f"image_{i+1}"] = img_analysis
        
        return json.dumps(analysis, indent=2, ensure_ascii=False)
    
    async def _analyze_image_local(self, image_path: str):
        """วิเคราะห์รูปภาพแบบ Local"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "ไม่สามารถอ่านรูปภาพได้"}
            
            height, width = img.shape[:2]
            
            # วิเคราะห์พื้นฐาน
            analysis = {
                "dimensions": f"{width}x{height}",
                "file_size": Path(image_path).stat().st_size,
                "file_type": Path(image_path).suffix,
                "analysis": "Local Image Analysis"
            }
            
            # ตรวจจับสีหลัก
            if len(img.shape) == 3:  # Color image
                avg_color = np.mean(img, axis=(0, 1))
                analysis["dominant_colors"] = {
                    "blue": int(avg_color[0]),
                    "green": int(avg_color[1]), 
                    "red": int(avg_color[2])
                }
            
            return analysis
            
        except Exception as e:
            return {"error": f"การวิเคราะห์รูปภาพผิดพลาด: {e}"}
        
    async def element_detection(self, screenshot_path, element_description):
        """ตรวจจับ element ด้วย AI"""
        if self.use_openai:
            result = await self._vision_analysis_openai(screenshot_path, element_description)
        else:
            result = await self._element_detection_local(screenshot_path, element_description)
        
        return self.parse_coordinates(result)
    
    async def _vision_analysis_openai(self, screenshot_path, prompt):
        """วิเคราะห์ภาพด้วย OpenAI"""
        try:
            with open(screenshot_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[{
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ OpenAI Vision Error: {e}")
            return await self._element_detection_local(screenshot_path, prompt)
    
    async def _element_detection_local(self, screenshot_path, element_description):
        """ตรวจจับ element แบบ Local"""
        try:
            img = cv2.imread(screenshot_path)
            if img is None:
                return json.dumps({"error": "ไม่สามารถอ่านรูปภาพได้"})
            
            height, width = img.shape[:2]
            
            # ตรวจจับ element แบบพื้นฐาน (ตัวอย่าง)
            elements = []
            
            # ตรวจจับปุ่ม (สีขาว/เทา)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours[:5]:  # 5 elements แรก
                x, y, w, h = cv2.boundingRect(contour)
                if w > 50 and h > 20:  # ขนาดขั้นต่ำ
                    elements.append({
                        "type": "button",
                        "coordinates": [x + w//2, y + h//2],
                        "size": [w, h],
                        "confidence": 0.6
                    })
            
            return json.dumps({
                "description": element_description,
                "image_size": [width, height],
                "elements_found": elements,
                "method": "Local Detection"
            })
            
        except Exception as e:
            return json.dumps({"error": f"การตรวจจับ element ผิดพลาด: {e}"})
        
    def parse_coordinates(self, ai_response):
        """แยกพิกัดจาก AI response"""
        try:
            if isinstance(ai_response, str):
                # ลอง parse JSON
                data = json.loads(ai_response)
                
                # หา coordinates
                if "elements_found" in data and data["elements_found"]:
                    return data["elements_found"][0]["coordinates"]
                elif "coordinates" in data:
                    return data["coordinates"]
                    
            # Fallback: หา coordinates จาก text
            coords_match = re.search(r'\[(\d+),\s*(\d+)\]', str(ai_response))
            if coords_match:
                return [int(coords_match.group(1)), int(coords_match.group(2))]
                
        except Exception as e:
            print(f"❌ ไม่สามารถแยกพิกัดได้: {e}")
        
        return None

    # เพิ่ม Missing Methods ที่ระบบเรียกใช้
    def process_text(self, text: str, task: str = "general") -> Dict[str, any]:
        """ประมวลผลข้อความ (Method ที่ระบบเรียกใช้)"""
        try:
            result = {
                'input_text': text,
                'task': task,
                'processed_at': str(Path(__file__).parent / 'logs' / 'ai_processing.log'),
                'confidence': 0.8
            }
            
            if task == "sentiment":
                # วิเคราะห์ความรู้สึก
                positive_words = ['ดี', 'เยี่ยม', 'ชอบ', 'ดีใจ', 'สุข', 'good', 'great', 'love', 'happy']
                negative_words = ['แย่', 'ไม่ดี', 'เสียใจ', 'โกรธ', 'bad', 'terrible', 'hate', 'angry']
                
                text_lower = text.lower()
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                if positive_count > negative_count:
                    result['sentiment'] = 'positive'
                    result['score'] = positive_count / len(text.split())
                elif negative_count > positive_count:
                    result['sentiment'] = 'negative'
                    result['score'] = negative_count / len(text.split())
                else:
                    result['sentiment'] = 'neutral'
                    result['score'] = 0.0
                    
            elif task == "keywords":
                # สกัดคำสำคัญ
                words = text.lower().split()
                from collections import Counter
                word_freq = Counter(words)
                result['keywords'] = [word for word, freq in word_freq.most_common(5)]
                
            elif task == "summary":
                # สรุปข้อความ
                sentences = text.split('.')
                if len(sentences) > 1:
                    result['summary'] = sentences[0] + '.'
                else:
                    result['summary'] = text[:100] + '...'
                    
            else:
                # การประมวลผลทั่วไป
                result['word_count'] = len(text.split())
                result['char_count'] = len(text)
                result['language'] = 'thai' if any('\u0e00' <= char <= '\u0e7f' for char in text) else 'english'
            
            return result
            
        except Exception as e:
            return {
                'error': f'การประมวลผลข้อความผิดพลาด: {e}',
                'input_text': text,
                'task': task,
                'confidence': 0.0
            }
    
    def process_image(self, image_path: str, task: str = "analysis") -> Dict[str, any]:
        """ประมวลผลรูปภาพ (Method ที่ระบบเรียกใช้)"""
        try:
            result = {
                'image_path': image_path,
                'task': task,
                'processed_at': str(Path(__file__).parent / 'logs' / 'image_processing.log'),
                'confidence': 0.7
            }
            
            img = cv2.imread(image_path)
            if img is None:
                return {'error': 'ไม่สามารถอ่านรูปภาพได้', 'image_path': image_path}
            
            height, width = img.shape[:2]
            result['dimensions'] = {'width': width, 'height': height}
            result['file_size'] = Path(image_path).stat().st_size
            
            if task == "ocr":
                # OCR การอ่านข้อความ
                import easyocr
                reader = easyocr.Reader(['th', 'en'])
                ocr_results = reader.readtext(image_path)
                result['text_detected'] = [text for _, text, conf in ocr_results if conf > 0.5]
                result['ocr_confidence'] = sum(conf for _, _, conf in ocr_results) / len(ocr_results) if ocr_results else 0
                
            elif task == "objects":
                # ตรวจจับวัตถุ
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                result['objects_detected'] = len(contours)
                
            elif task == "colors":
                # วิเคราะห์สี
                if len(img.shape) == 3:
                    avg_color = np.mean(img, axis=(0, 1))
                    result['dominant_colors'] = {
                        'blue': int(avg_color[0]),
                        'green': int(avg_color[1]),
                        'red': int(avg_color[2])
                    }
                    
            else:
                # การวิเคราะห์ทั่วไป
                result['channels'] = img.shape[2] if len(img.shape) == 3 else 1
                result['aspect_ratio'] = width / height if height > 0 else 0
            
            return result
            
        except Exception as e:
            return {
                'error': f'การประมวลผลรูปภาพผิดพลาด: {e}',
                'image_path': image_path,
                'task': task,
                'confidence': 0.0
            }
    
    def smart_analysis(self, data: Dict[str, any]) -> Dict[str, any]:
        """การวิเคราะห์อัจฉริยะ (Method ที่ระบบเรียกใช้)"""
        try:
            result = {
                'analysis_type': 'smart_analysis',
                'input_data': data,
                'processed_at': str(Path(__file__).parent / 'logs' / 'smart_analysis.log'),
                'confidence': 0.8
            }
            
            # วิเคราะห์ตามประเภทข้อมูล
            if 'text' in data:
                text_result = self.process_text(data['text'], 'general')
                result['text_analysis'] = text_result
                
            if 'image_path' in data:
                image_result = self.process_image(data['image_path'], 'analysis')
                result['image_analysis'] = image_result
                
            # สรุปผลการวิเคราะห์
            result['summary'] = {
                'total_analyses': len([k for k in result.keys() if k.endswith('_analysis')]),
                'overall_confidence': result.get('confidence', 0.0),
                'recommendations': self._generate_recommendations(result)
            }
            
            return result
            
        except Exception as e:
            return {
                'error': f'การวิเคราะห์อัจฉริยะผิดพลาด: {e}',
                'input_data': data,
                'confidence': 0.0
            }
    
    def _generate_recommendations(self, analysis_result: Dict[str, any]) -> List[str]:
        """สร้างคำแนะนำจากการวิเคราะห์"""
        recommendations = []
        
        # ตรวจสอบความเชื่อมั่น
        if analysis_result.get('confidence', 0) < 0.5:
            recommendations.append("ควรตรวจสอบข้อมูลเพิ่มเติมเพื่อเพิ่มความแม่นยำ")
            
        # ตรวจสอบการวิเคราะห์ข้อความ
        if 'text_analysis' in analysis_result:
            text_analysis = analysis_result['text_analysis']
            if text_analysis.get('word_count', 0) < 5:
                recommendations.append("ข้อความสั้นเกินไป ควรเพิ่มข้อมูลให้มากขึ้น")
                
        # ตรวจสอบการวิเคราะห์รูปภาพ
        if 'image_analysis' in analysis_result:
            image_analysis = analysis_result['image_analysis']
            if image_analysis.get('dimensions', {}).get('width', 0) < 100:
                recommendations.append("รูปภาพมีขนาดเล็ก ควรใช้รูปภาพที่มีความละเอียดสูงขึ้น")
                
        if not recommendations:
            recommendations.append("การวิเคราะห์เสร็จสิ้นแล้ว ผลลัพธ์น่าเชื่อถือ")
            
        return recommendations
