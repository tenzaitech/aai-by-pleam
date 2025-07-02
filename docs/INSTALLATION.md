# 📦 คู่มือการติดตั้ง

## 🚀 การติดตั้งระบบ AI-Powered Chrome Automation

### 📋 ข้อกำหนด
- Python 3.8+
- Chrome Browser
- Cursor IDE

### 🔧 ขั้นตอนการติดตั้ง

#### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

#### 2. ตั้งค่า API Keys
```bash
# สร้างไฟล์ .env
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

#### 3. ทดสอบการติดตั้ง
```bash
python -c "import selenium, openai, pythainlp; print('✅ ติดตั้งสำเร็จ')"
```

### 🎯 การใช้งานครั้งแรก
```bash
python run_system.py
```

### 🔍 การแก้ไขปัญหา
- ตรวจสอบ Chrome version
- ตรวจสอบ API key
- ตรวจสอบ dependencies

---
**สร้างโดย WAWA** 🧠
