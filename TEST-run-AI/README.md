# WAWAGOT V.2 API Test Suite

โฟลเดอร์นี้ประกอบด้วยชุดการทดสอบ API อัตโนมัติสำหรับ WAWAGOT V.2

## 📁 ไฟล์ในโฟลเดอร์

- `run_tests.py` - Script หลักสำหรับรันการทดสอบทั้งหมด
- `test_api_run.py` - Script ทดสอบ API endpoints
- `requirements.txt` - Dependencies สำหรับการทดสอบ
- `README.md` - คู่มือการใช้งาน

## 🚀 วิธีการใช้งาน

### 1. รันระบบ WAWAGOT V.2 ก่อน
```bash
cd wawagot.ai
python launch_v2.py
```

### 2. รันการทดสอบ API
```bash
cd TEST-run-AI
python run_tests.py
```

### 3. รันการทดสอบเฉพาะ API
```bash
cd TEST-run-AI
python test_api_run.py
```

## 🧪 การทดสอบที่ครอบคลุม

### ✅ Health Check
- ตรวจสอบสถานะระบบ
- ตรวจสอบการเชื่อมต่อ API server

### ✅ AI Commands
- ทดสอบการส่งคำสั่งภาษาไทย
- ทดสอบการประมวลผล AI

### ✅ Chrome Automation
- ทดสอบการนำทางเว็บไซต์
- ทดสอบการควบคุมเบราว์เซอร์

### ✅ AI Processing
- ทดสอบการประมวลผลข้อความ
- ทดสอบการวิเคราะห์ภาพ

### ✅ Knowledge Management
- ทดสอบการเก็บข้อมูล
- ทดสอบการค้นหาข้อมูล

### ✅ Configuration
- ทดสอบการอ่านการตั้งค่า
- ทดสอบการอัปเดตการตั้งค่า

### ✅ System Control
- ทดสอบการรีสตาร์ทระบบ
- ทดสอบการปิดระบบ

## 📊 ผลการทดสอบ

### สถานะที่คาดหวัง
- **200 OK** - การทำงานปกติ
- **503 Service Unavailable** - ระบบไม่พร้อมใช้งาน
- **500 Internal Server Error** - เกิดข้อผิดพลาดในระบบ

### การแปลผล
- ✅ **สำเร็จ** - API ทำงานปกติ
- ⚠️ **คำเตือน** - มีปัญหาเล็กน้อย
- ❌ **ล้มเหลว** - เกิดข้อผิดพลาด

## 🔧 การแก้ไขปัญหา

### ปัญหา: ModuleNotFoundError
```bash
pip install requests
```

### ปัญหา: Connection refused
1. ตรวจสอบว่าได้รัน `python launch_v2.py` แล้ว
2. ตรวจสอบว่า API server ทำงานที่ port 8000
3. ตรวจสอบ firewall settings

### ปัญหา: Timeout
1. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
2. ตรวจสอบ API server response time
3. เพิ่ม timeout ใน test script

## 📝 การเพิ่ม Test Cases

### เพิ่ม Test Function
```python
def test_new_feature():
    data = {
        "parameter": "value"
    }
    resp = requests.post(f"{BASE_URL}/api/new-endpoint", json=data)
    print_result("New Feature Test", resp)
```

### เพิ่มใน main()
```python
def main():
    test_health()
    test_new_feature()  # เพิ่มบรรทัดนี้
    # ... other tests
```

## 🎯 เป้าหมาย

- ✅ ตรวจสอบ API endpoints ทั้งหมด
- ✅ ตรวจสอบการทำงานของระบบ
- ✅ ตรวจสอบการจัดการข้อผิดพลาด
- ✅ ตรวจสอบประสิทธิภาพการทำงาน

## 📞 การสนับสนุน

หากพบปัญหาในการทดสอบ:
1. ตรวจสอบ logs ใน `wawagot.ai/logs/`
2. ตรวจสอบ API documentation ที่ `http://localhost:8000/docs`
3. ตรวจสอบ system status ใน Dashboard

---

**พัฒนาโดย:** WAWA & AI Assistant  
**วันที่:** มกราคม 2024 