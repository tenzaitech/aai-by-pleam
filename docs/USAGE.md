# 📖 คู่มือการใช้งาน

## 🎯 วิธีใช้ระบบ AI-Powered Chrome Automation

### 🚀 การเริ่มต้น
```bash
python run_system.py
```

### 🇹🇭 คำสั่งภาษาไทย
```
"เปิดเว็บไซต์ Google"
"คลิกที่ปุ่มค้นหา"
"กรอกข้อมูลในช่อง username"
"ถ่ายภาพหน้าจอ"
"เลื่อนลงไปดูเนื้อหา"
```

### 🎯 ความสามารถหลัก

#### 1. Chrome Automation
- เปิด/ปิด browser
- นำทางไปยัง URL
- คลิก elements
- กรอกฟอร์ม

#### 2. Thai Language Support
- เข้าใจคำสั่งไทย
- OCR ข้อความไทย
- วิเคราะห์หน้าจอไทย

#### 3. AI Integration
- วิเคราะห์รูปภาพ
- หา elements อัตโนมัติ
- คำสั่งธรรมชาติ

#### 4. Visual Recognition
- ตรวจจับ elements
- วิเคราะห์สี
- อ่านข้อความ

### 🔧 การตั้งค่า
```python
# เปลี่ยนการตั้งค่า
from core.config_manager import ConfigManager

config = ConfigManager()
config.update_config('chrome', {'headless': True})
```

### 📊 การ Monitor
- ดู logs ใน logs/system.log
- ตรวจสอบ screenshots ใน screenshots/
- ดูข้อมูลใน data/

---
**สร้างโดย WAWA** 🧠
