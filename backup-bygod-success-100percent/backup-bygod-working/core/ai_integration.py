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
    
    async def smart_analysis(self, data: Dict[str, Any]):
        """วิเคราะห์อัจฉริยะ"""
        if self.use_openai:
            return await self._smart_analysis_openai(data)
        else:
            return await self._smart_analysis_local(data)
    
    async def _smart_analysis_openai(self, data: Dict[str, Any]):
        """วิเคราะห์อัจฉริยะด้วย OpenAI"""
        try:
            prompt = f"Analyze this data: {json.dumps(data, ensure_ascii=False)}"
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ OpenAI Smart Analysis Error: {e}")
            return await self._smart_analysis_local(data)
    
    async def _smart_analysis_local(self, data: Dict[str, Any]):
        """วิเคราะห์อัจฉริยะแบบ Local"""
        analysis = {
            "method": "Local Smart Analysis",
            "data_type": type(data).__name__,
            "data_keys": list(data.keys()) if isinstance(data, dict) else [],
            "summary": "Local AI processing completed successfully",
            "recommendations": [
                "ใช้ Local Processing สำหรับการวิเคราะห์พื้นฐาน",
                "อัปเกรดเป็น OpenAI API สำหรับการวิเคราะห์ขั้นสูง"
            ]
        }
        return json.dumps(analysis, indent=2, ensure_ascii=False)
