# Gemini CLI และ Google Generative AI - ความรู้และวิธีการใช้งาน

## 📋 สรุปความรู้ Gemini CLI

### 🎯 **Gemini CLI คืออะไร**
- **Gemini CLI** เป็น Command Line Interface สำหรับใช้งาน Google Gemini AI
- เป็นเครื่องมือที่ช่วยให้ใช้งาน Gemini AI ได้ผ่าน command line โดยไม่ต้องเขียนโค้ด
- รองรับการใช้งานแบบ interactive และ batch processing

### 🔧 **การติดตั้งและ Setup**

#### **1. ติดตั้ง Google Generative AI Library**
```bash
pip install google-generativeai
```

#### **2. ตั้งค่า API Key**
```bash
# วิธีที่ 1: ตั้ง Environment Variable
export GOOGLE_API_KEY="your_api_key_here"

# วิธีที่ 2: ใช้ใน Python Code
import google.generativeai as genai
genai.configure(api_key="your_api_key_here")
```

#### **3. วิธีได้ API Key**
1. ไปที่ [Google AI Studio](https://makersuite.google.com/app/apikey)
2. สร้าง API Key ใหม่
3. คัดลอก API Key มาใช้งาน

### 🚀 **การใช้งานพื้นฐาน**

#### **1. การใช้งานใน Python**
```python
import google.generativeai as genai

# ตั้งค่า API Key
genai.configure(api_key="your_api_key")

# สร้าง model
model = genai.GenerativeModel('gemini-pro')

# ส่งคำถาม
response = model.generate_content("สวัสดีครับ")
print(response.text)
```

#### **2. การใช้งานแบบ Interactive**
```python
# สร้าง chat session
chat = model.start_chat(history=[])

# สนทนาแบบต่อเนื่อง
response = chat.send_message("ช่วยอธิบายเรื่อง AI หน่อย")
print(response.text)

response = chat.send_message("ขอบคุณครับ")
print(response.text)
```

### 📊 **Models ที่ใช้งานได้**

#### **1. Text Models**
- `gemini-pro` - สำหรับงานทั่วไป, coding, analysis
- `gemini-pro-vision` - สำหรับงานที่ต้องการประมวลผลรูปภาพ

#### **2. Features หลัก**
- **Text Generation** - สร้างข้อความ, code, analysis
- **Image Analysis** - วิเคราะห์รูปภาพ, OCR
- **Code Generation** - สร้างโค้ด, debug, explain
- **Multimodal** - ทำงานกับข้อความและรูปภาพพร้อมกัน

### 🛠️ **การใช้งานใน WAWAGOT System**

#### **1. Integration กับ Smart Command Hub**
```python
# ตัวอย่างการใช้งานใน smart_command_hub.py
import google.generativeai as genai

class GeminiAIHelper:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def suggest_command(self, user_input):
        prompt = f"ช่วยแนะนำคำสั่งสำหรับ: {user_input}"
        response = self.model.generate_content(prompt)
        return response.text
    
    def analyze_logs(self, log_data):
        prompt = f"วิเคราะห์ log นี้: {log_data}"
        response = self.model.generate_content(prompt)
        return response.text
```

#### **2. การใช้งานใน Dashboard**
```python
# ตัวอย่างการใช้งานใน orange_dashboard.py
@app.route('/ai_analysis')
def ai_analysis():
    gemini = GeminiAIHelper(api_key)
    analysis = gemini.analyze_system_status()
    return jsonify({'analysis': analysis})
```

### 📈 **Use Cases ที่น่าสนใจ**

#### **1. Smart Command Suggestions**
- วิเคราะห์คำสั่งที่ผู้ใช้พิมพ์
- แนะนำคำสั่งที่เหมาะสม
- เรียนรู้ pattern การใช้งาน

#### **2. Log Analysis**
- วิเคราะห์ log files อัตโนมัติ
- แจ้งเตือนปัญหา
- ให้คำแนะนำการแก้ไข

#### **3. Code Generation**
- สร้างโค้ดตามความต้องการ
- Debug โค้ดที่มีปัญหา
- อธิบายโค้ดที่ซับซ้อน

#### **4. System Monitoring**
- วิเคราะห์สถานะระบบ
- แนะนำการ optimize
- คาดการณ์ปัญหา

### 🔒 **Security และ Best Practices**

#### **1. API Key Management**
```python
# ใช้ environment variables
import os
api_key = os.getenv('GOOGLE_API_KEY')

# หรือใช้ config file
import json
with open('config.json') as f:
    config = json.load(f)
    api_key = config['google_api_key']
```

#### **2. Rate Limiting**
```python
import time

def safe_api_call(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            time.sleep(1)  # หน่วงเวลา 1 วินาที
            return result
        except Exception as e:
            print(f"API Error: {e}")
            return None
    return wrapper
```

### 📚 **Resources และ Documentation**

#### **1. Official Documentation**
- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Python Library Documentation](https://github.com/google/generative-ai-python)

#### **2. Examples และ Tutorials**
- [Quick Start Guide](https://ai.google.dev/gemini-api/docs/quickstart)
- [Code Examples](https://github.com/google/generative-ai-python/tree/main/examples)

### 🎯 **การประยุกต์ใช้ใน WAWAGOT V2.5**

#### **1. Enhanced AI Assistant**
- ใช้ Gemini ช่วยวิเคราะห์คำสั่ง
- แนะนำการใช้งานระบบ
- ช่วยแก้ไขปัญหา

#### **2. Smart Logging**
- วิเคราะห์ log แบบ real-time
- แจ้งเตือนปัญหา
- ให้คำแนะนำการแก้ไข

#### **3. Code Generation**
- สร้าง automation scripts
- Generate test cases
- สร้าง documentation

#### **4. System Optimization**
- วิเคราะห์ performance
- แนะนำการปรับปรุง
- คาดการณ์ปัญหา

---

## 💾 **บันทึกในความทรงจำ**

✅ **Gemini CLI และ Google Generative AI** - ติดตั้งและพร้อมใช้งาน  
✅ **API Key Setup** - ต้องตั้งค่า GOOGLE_API_KEY  
✅ **Integration Ready** - สามารถใช้งานใน WAWAGOT system ได้  
✅ **Use Cases** - Smart commands, log analysis, code generation, monitoring  
✅ **Security** - API key management และ rate limiting  

**ความมั่นใจ: 95%** - ระบบพร้อมใช้งาน Gemini AI ใน WAWAGOT V2.5 