# Retell.AI Implementation Guide for WAWAGOT.AI
# ===============================================================================
# WAWAGOT.AI - Retell.AI Practical Implementation
# ===============================================================================
# Created: 2024-12-19
# Purpose: Step-by-step implementation guide for Retell.AI integration
# ===============================================================================

## 1. QUICK START IMPLEMENTATION
### ===============================================================================

### 1.1 Basic Setup
```python
# requirements.txt
retell-sdk==1.0.0
requests==2.31.0
asyncio==3.4.3
python-dotenv==1.0.0
```

### 1.2 Environment Configuration
```bash
# .env
RETELL_API_KEY=your_retell_api_key_here
RETELL_FROM_NUMBER=+14157774444
RETELL_WEBHOOK_URL=https://your-domain.com/webhook
```

### 1.3 Basic Client Implementation
```python
import os
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class RetellAIClient:
    def __init__(self):
        self.api_key = os.getenv("RETELL_API_KEY")
        self.from_number = os.getenv("RETELL_FROM_NUMBER")
        self.base_url = "https://api.retellai.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_call(self, to_number, agent_id=None):
        """สร้างการโทรออก"""
        payload = {
            "from_number": self.from_number,
            "to_number": to_number
        }
        
        if agent_id:
            payload["agent_id"] = agent_id
        
        try:
            response = requests.post(
                f"{self.base_url}/create-phone-call",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_call_status(self, call_id):
        """ดูสถานะการโทร"""
        try:
            response = requests.get(
                f"{self.base_url}/calls/{call_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def end_call(self, call_id):
        """จบการโทร"""
        try:
            response = requests.post(
                f"{self.base_url}/calls/{call_id}/end",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
```

## 2. WAWAGOT.AI INTEGRATION
### ===============================================================================

### 2.1 Integration Class
```python
class WAWAGOTRetellIntegration:
    def __init__(self, wawagot_system):
        self.wawagot = wawagot_system
        self.retell_client = RetellAIClient()
        self.active_calls = {}
        self.call_history = {}
    
    async def initiate_ai_call(self, to_number, context=None):
        """เริ่มการโทร AI"""
        try:
            # สร้างการโทร
            call_response = self.retell_client.create_call(to_number)
            
            if "error" in call_response:
                return {
                    "success": False,
                    "error": call_response["error"]
                }
            
            call_id = call_response.get("call_id")
            
            # บันทึกข้อมูลการโทร
            self.active_calls[call_id] = {
                "to_number": to_number,
                "start_time": datetime.now(),
                "context": context or {},
                "status": "initiated"
            }
            
            # เริ่มการติดตาม
            asyncio.create_task(self.monitor_call(call_id))
            
            return {
                "success": True,
                "call_id": call_id,
                "agent_id": call_response.get("agent_id")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def monitor_call(self, call_id):
        """ติดตามการโทร"""
        while call_id in self.active_calls:
            try:
                status = self.retell_client.get_call_status(call_id)
                
                if "error" in status:
                    print(f"Error monitoring call {call_id}: {status['error']}")
                    break
                
                # อัพเดทสถานะ
                self.active_calls[call_id]["status"] = status.get("call_status")
                
                # บันทึก transcript
                if "transcript" in status:
                    self.active_calls[call_id]["transcript"] = status["transcript"]
                
                # ตรวจสอบการจบ
                if status.get("call_status") in ["ended", "failed"]:
                    await self.process_call_completion(call_id, status)
                    break
                
                await asyncio.sleep(5)  # ตรวจสอบทุก 5 วินาที
                
            except Exception as e:
                print(f"Monitoring error for call {call_id}: {e}")
                break
    
    async def process_call_completion(self, call_id, final_status):
        """ประมวลผลเมื่อการโทรจบ"""
        call_data = self.active_calls.get(call_id, {})
        
        # สร้างข้อมูลสรุป
        summary = {
            "call_id": call_id,
            "to_number": call_data.get("to_number"),
            "start_time": call_data.get("start_time"),
            "end_time": datetime.now(),
            "duration_ms": final_status.get("duration_ms", 0),
            "transcript": final_status.get("transcript", ""),
            "sentiment": final_status.get("call_analysis", {}).get("user_sentiment"),
            "success": final_status.get("call_analysis", {}).get("call_successful"),
            "summary": final_status.get("call_analysis", {}).get("call_summary"),
            "recording_url": final_status.get("recording_url"),
            "context": call_data.get("context", {})
        }
        
        # บันทึกประวัติ
        self.call_history[call_id] = summary
        
        # บันทึกไปยัง WAWAGOT.AI knowledge manager
        if self.wawagot and hasattr(self.wawagot, 'knowledge_manager'):
            await self.wawagot.knowledge_manager.store_call_data(summary)
        
        # ลบจาก active calls
        if call_id in self.active_calls:
            del self.active_calls[call_id]
        
        return summary
```

## 3. USE CASE IMPLEMENTATIONS
### ===============================================================================

### 3.1 Customer Service Bot
```python
class CustomerServiceBot:
    def __init__(self, retell_integration):
        self.retell = retell_integration
        self.service_agents = {
            "general": "agent_general_support",
            "technical": "agent_technical_support",
            "billing": "agent_billing_support"
        }
    
    async def handle_customer_inquiry(self, phone_number, inquiry_type="general"):
        """จัดการคำถามลูกค้า"""
        agent_id = self.service_agents.get(inquiry_type, "agent_general_support")
        
        context = {
            "inquiry_type": inquiry_type,
            "timestamp": datetime.now().isoformat(),
            "priority": "normal"
        }
        
        result = await self.retell.initiate_ai_call(
            to_number=phone_number,
            context=context
        )
        
        return result
```

### 3.2 Appointment Scheduler
```python
class AppointmentScheduler:
    def __init__(self, retell_integration, calendar_system):
        self.retell = retell_integration
        self.calendar = calendar_system
    
    async def schedule_appointment(self, phone_number, preferred_date=None):
        """นัดหมายลูกค้า"""
        # ดึงเวลาที่ว่าง
        available_slots = await self.calendar.get_available_slots(preferred_date)
        
        context = {
            "action": "schedule_appointment",
            "preferred_date": preferred_date,
            "available_slots": available_slots,
            "customer_phone": phone_number
        }
        
        result = await self.retell.initiate_ai_call(
            to_number=phone_number,
            context=context
        )
        
        return result
```

### 3.3 Survey System
```python
class SurveySystem:
    def __init__(self, retell_integration, survey_database):
        self.retell = retell_integration
        self.survey_db = survey_database
    
    async def conduct_survey(self, phone_number, survey_id):
        """ดำเนินการสำรวจ"""
        # ดึงข้อมูลสำรวจ
        survey_data = await self.survey_db.get_survey(survey_id)
        
        context = {
            "action": "conduct_survey",
            "survey_id": survey_id,
            "survey_name": survey_data.get("name"),
            "questions": survey_data.get("questions", []),
            "estimated_duration": survey_data.get("estimated_duration", 5)
        }
        
        result = await self.retell.initiate_ai_call(
            to_number=phone_number,
            context=context
        )
        
        return result
```

## 4. ANALYTICS & MONITORING
### ===============================================================================

### 4.1 Call Analytics
```python
class CallAnalytics:
    def __init__(self, retell_integration):
        self.retell = retell_integration
        self.analytics_data = {}
    
    def generate_call_report(self, call_id):
        """สร้างรายงานการโทร"""
        call_data = self.retell.call_history.get(call_id)
        
        if not call_data:
            return {"error": "Call data not found"}
        
        # คำนวณสถิติ
        duration_minutes = call_data.get("duration_ms", 0) / 60000
        sentiment_score = self.calculate_sentiment_score(call_data.get("sentiment"))
        
        report = {
            "call_id": call_id,
            "duration_minutes": round(duration_minutes, 2),
            "sentiment_score": sentiment_score,
            "success_rate": 1 if call_data.get("success") else 0,
            "key_topics": self.extract_key_topics(call_data.get("transcript", "")),
            "action_items": self.extract_action_items(call_data.get("summary", "")),
            "call_summary": call_data.get("summary"),
            "recording_url": call_data.get("recording_url")
        }
        
        return report
    
    def calculate_sentiment_score(self, sentiment):
        """คำนวณคะแนนความรู้สึก"""
        sentiment_scores = {
            "Positive": 1.0,
            "Neutral": 0.5,
            "Negative": 0.0
        }
        return sentiment_scores.get(sentiment, 0.5)
    
    def extract_key_topics(self, transcript):
        """ดึงหัวข้อสำคัญ"""
        # ใช้ keyword extraction หรือ NLP
        topics = []
        # Implementation here
        return topics
    
    def extract_action_items(self, summary):
        """ดึงรายการที่ต้องทำ"""
        action_items = []
        # Implementation here
        return action_items
    
    def get_call_statistics(self):
        """ดึงสถิติการโทร"""
        total_calls = len(self.retell.call_history)
        successful_calls = sum(1 for call in self.retell.call_history.values() 
                             if call.get("success"))
        
        avg_duration = sum(call.get("duration_ms", 0) for call in self.retell.call_history.values()) / total_calls if total_calls > 0 else 0
        
        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "success_rate": (successful_calls / total_calls * 100) if total_calls > 0 else 0,
            "average_duration_minutes": round(avg_duration / 60000, 2)
        }
```

### 4.2 Real-time Dashboard
```python
class RetellDashboard:
    def __init__(self, retell_integration):
        self.retell = retell_integration
        self.analytics = CallAnalytics(retell_integration)
    
    def get_dashboard_data(self):
        """ดึงข้อมูล dashboard"""
        active_calls = len(self.retell.active_calls)
        call_stats = self.analytics.get_call_statistics()
        
        # ดึงการโทรล่าสุด
        recent_calls = list(self.retell.call_history.values())[-10:]
        
        return {
            "active_calls": active_calls,
            "call_statistics": call_stats,
            "recent_calls": recent_calls,
            "system_status": "operational"
        }
    
    def get_call_details(self, call_id):
        """ดึงรายละเอียดการโทร"""
        if call_id in self.retell.active_calls:
            return self.retell.active_calls[call_id]
        elif call_id in self.retell.call_history:
            return self.retell.call_history[call_id]
        else:
            return {"error": "Call not found"}
```

## 5. ERROR HANDLING & LOGGING
### ===============================================================================

### 5.1 Error Handler
```python
import logging
from datetime import datetime

class RetellErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger("retell_ai")
        self.logger.setLevel(logging.INFO)
        
        # สร้าง file handler
        fh = logging.FileHandler("retell_ai.log")
        fh.setLevel(logging.INFO)
        
        # สร้าง formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        
        self.logger.addHandler(fh)
    
    def log_call_error(self, call_id, error, context=None):
        """บันทึกข้อผิดพลาดการโทร"""
        error_data = {
            "call_id": call_id,
            "error": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        self.logger.error(f"Call error: {error_data}")
        return error_data
    
    def log_call_success(self, call_id, duration, context=None):
        """บันทึกการโทรสำเร็จ"""
        success_data = {
            "call_id": call_id,
            "duration_ms": duration,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        self.logger.info(f"Call success: {success_data}")
        return success_data
```

### 5.2 Retry Mechanism
```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """Decorator สำหรับ retry เมื่อล้มเหลว"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

class RetellClientWithRetry(RetellAIClient):
    @retry_on_failure(max_retries=3, delay=1)
    def create_call(self, to_number, agent_id=None):
        """สร้างการโทรออกพร้อม retry"""
        return super().create_call(to_number, agent_id)
    
    @retry_on_failure(max_retries=3, delay=1)
    def get_call_status(self, call_id):
        """ดูสถานะการโทรพร้อม retry"""
        return super().get_call_status(call_id)
```

## 6. TESTING & VALIDATION
### ===============================================================================

### 6.1 Test Suite
```python
import unittest
import asyncio
from unittest.mock import Mock, patch

class TestRetellIntegration(unittest.TestCase):
    def setUp(self):
        self.retell_client = RetellAIClient()
        self.integration = WAWAGOTRetellIntegration(Mock())
    
    def test_create_call(self):
        """ทดสอบการสร้างการโทร"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                "call_id": "test_call_id",
                "agent_id": "test_agent_id"
            }
            mock_post.return_value.raise_for_status.return_value = None
            
            result = self.retell_client.create_call("+1234567890")
            
            self.assertIn("call_id", result)
            self.assertEqual(result["call_id"], "test_call_id")
    
    def test_get_call_status(self):
        """ทดสอบการดูสถานะการโทร"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                "call_status": "active",
                "duration_ms": 30000
            }
            mock_get.return_value.raise_for_status.return_value = None
            
            result = self.retell_client.get_call_status("test_call_id")
            
            self.assertEqual(result["call_status"], "active")
    
    @asyncio.coroutine
    def test_initiate_ai_call(self):
        """ทดสอบการเริ่มการโทร AI"""
        with patch.object(self.retell_client, 'create_call') as mock_create:
            mock_create.return_value = {
                "call_id": "test_call_id",
                "agent_id": "test_agent_id"
            }
            
            result = yield from self.integration.initiate_ai_call("+1234567890")
            
            self.assertTrue(result["success"])
            self.assertEqual(result["call_id"], "test_call_id")
```

### 6.2 Integration Test
```python
class TestRetellIntegrationEndToEnd:
    def __init__(self, retell_integration):
        self.integration = retell_integration
        self.test_results = []
    
    async def run_full_test(self):
        """รันการทดสอบแบบ end-to-end"""
        tests = [
            self.test_call_creation,
            self.test_call_monitoring,
            self.test_call_completion,
            self.test_analytics
        ]
        
        for test in tests:
            try:
                result = await test()
                self.test_results.append({
                    "test": test.__name__,
                    "status": "passed" if result else "failed",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.test_results.append({
                    "test": test.__name__,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return self.test_results
    
    async def test_call_creation(self):
        """ทดสอบการสร้างการโทร"""
        # ใช้หมายเลขทดสอบ
        result = await self.integration.initiate_ai_call("+15551234567")
        return result.get("success", False)
    
    async def test_call_monitoring(self):
        """ทดสอบการติดตามการโทร"""
        # Implementation
        return True
    
    async def test_call_completion(self):
        """ทดสอบการจบการโทร"""
        # Implementation
        return True
    
    async def test_analytics(self):
        """ทดสอบการวิเคราะห์"""
        # Implementation
        return True
```

## 7. DEPLOYMENT CHECKLIST
### ===============================================================================

### 7.1 Pre-deployment Checklist
- [ ] **API Key Configuration**
  - [ ] Retell.AI API key ได้รับการตั้งค่า
  - [ ] หมายเลขโทรออกได้รับการยืนยัน
  - [ ] Webhook URL ได้รับการตั้งค่า (ถ้าจำเป็น)

- [ ] **Environment Setup**
  - [ ] Python environment ได้รับการติดตั้ง
  - [ ] Dependencies ได้รับการติดตั้ง
  - [ ] Environment variables ได้รับการตั้งค่า

- [ ] **Testing**
  - [ ] Unit tests ผ่าน
  - [ ] Integration tests ผ่าน
  - [ ] End-to-end tests ผ่าน

- [ ] **Monitoring**
  - [ ] Logging ได้รับการตั้งค่า
  - [ ] Error handling ได้รับการตั้งค่า
  - [ ] Analytics dashboard ได้รับการตั้งค่า

### 7.2 Production Deployment
```python
# production_config.py
import os

class ProductionConfig:
    # Retell.AI Configuration
    RETELL_API_KEY = os.getenv("RETELL_PROD_API_KEY")
    RETELL_FROM_NUMBER = os.getenv("RETELL_PROD_FROM_NUMBER")
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = "/var/log/retell_ai.log"
    
    # Performance Configuration
    MAX_CONCURRENT_CALLS = 100
    CALL_MONITORING_INTERVAL = 5  # seconds
    
    # Security Configuration
    ENCRYPTION_ENABLED = True
    AUDIT_LOGGING_ENABLED = True
    
    # Analytics Configuration
    ANALYTICS_ENABLED = True
    DATA_RETENTION_DAYS = 90
```

## 8. TROUBLESHOOTING GUIDE
### ===============================================================================

### 8.1 Common Issues

#### Issue: API Key Authentication Failed
```python
# Solution: ตรวจสอบ API key
def verify_api_key():
    try:
        response = requests.get(
            "https://api.retellai.com/v2/agents",
            headers={"Authorization": f"Bearer {os.getenv('RETELL_API_KEY')}"}
        )
        return response.status_code == 200
    except Exception as e:
        print(f"API key verification failed: {e}")
        return False
```

#### Issue: Call Creation Failed
```python
# Solution: ตรวจสอบหมายเลขโทรศัพท์
def validate_phone_number(phone_number):
    import re
    pattern = r'^\+[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone_number))
```

#### Issue: Call Monitoring Not Working
```python
# Solution: ตรวจสอบการเชื่อมต่อ
def check_connectivity():
    try:
        response = requests.get("https://api.retellai.com/v2/health")
        return response.status_code == 200
    except Exception as e:
        print(f"Connectivity check failed: {e}")
        return False
```

### 8.2 Debug Mode
```python
class DebugRetellClient(RetellAIClient):
    def __init__(self, debug=True):
        super().__init__()
        self.debug = debug
    
    def create_call(self, to_number, agent_id=None):
        if self.debug:
            print(f"DEBUG: Creating call to {to_number}")
        
        result = super().create_call(to_number, agent_id)
        
        if self.debug:
            print(f"DEBUG: Call creation result: {result}")
        
        return result
```

## 9. PERFORMANCE OPTIMIZATION
### ===============================================================================

### 9.1 Connection Pooling
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OptimizedRetellClient(RetellAIClient):
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        
        # ตั้งค่า retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def create_call(self, to_number, agent_id=None):
        payload = {
            "from_number": self.from_number,
            "to_number": to_number
        }
        
        if agent_id:
            payload["agent_id"] = agent_id
        
        try:
            response = self.session.post(
                f"{self.base_url}/create-phone-call",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
```

### 9.2 Async Optimization
```python
import aiohttp
import asyncio

class AsyncRetellClient:
    def __init__(self):
        self.api_key = os.getenv("RETELL_API_KEY")
        self.from_number = os.getenv("RETELL_FROM_NUMBER")
        self.base_url = "https://api.retellai.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_call_async(self, to_number, agent_id=None):
        """สร้างการโทรออกแบบ async"""
        payload = {
            "from_number": self.from_number,
            "to_number": to_number
        }
        
        if agent_id:
            payload["agent_id"] = agent_id
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/create-phone-call",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
    
    async def get_call_status_async(self, call_id):
        """ดูสถานะการโทรแบบ async"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/calls/{call_id}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
```

## 10. CONCLUSION
### ===============================================================================

### 10.1 Implementation Summary
1. **Basic Setup** - การตั้งค่าพื้นฐาน Retell.AI
2. **WAWAGOT.AI Integration** - การรวมเข้ากับระบบ WAWAGOT.AI
3. **Use Case Implementation** - การใช้งานจริง
4. **Analytics & Monitoring** - การวิเคราะห์และติดตาม
5. **Error Handling** - การจัดการข้อผิดพลาด
6. **Testing** - การทดสอบ
7. **Deployment** - การ deploy
8. **Troubleshooting** - การแก้ไขปัญหา
9. **Performance Optimization** - การปรับปรุงประสิทธิภาพ

### 10.2 Next Steps
1. **Start with Pilot** - เริ่มต้นด้วยโครงการนำร่อง
2. **Monitor Performance** - ติดตามประสิทธิภาพ
3. **Gather Feedback** - รวบรวมข้อเสนอแนะ
4. **Scale Gradually** - ขยายแบบค่อยเป็นค่อยไป
5. **Optimize Continuously** - ปรับปรุงอย่างต่อเนื่อง

### 10.3 Success Metrics
- **Call Success Rate** > 95%
- **Response Time** < 1 second
- **Uptime** > 99.9%
- **Customer Satisfaction** > 4.5/5

# ===============================================================================
# END OF RETELL.AI IMPLEMENTATION GUIDE
# =============================================================================== 