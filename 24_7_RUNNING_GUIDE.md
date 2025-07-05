# 🚀 WAWAGOT.AI - คู่มือการรันระบบตลอดเวลา (24/7)

## 📅 วันที่สร้าง: 2024-2025
## 🎯 สถานะ: Production Ready 100%

---

## 🎯 **ภาพรวม**

คู่มือนี้จะสอนวิธีการรันระบบ WAWAGOT.AI ตลอดเวลา 24/7 โดยมี 3 วิธีหลัก:

1. **Windows Service** - รันเป็น Background Service
2. **Auto Startup** - รันอัตโนมัติเมื่อเปิดเครื่อง
3. **Manual Management** - จัดการด้วยตนเอง

---

## 🔧 **วิธีที่ 1: Windows Service (แนะนำ)**

### 📋 **ข้อดี:**
- รันตลอดเวลาแม้ไม่ได้ Login
- จัดการโดย Windows Service Manager
- Auto-restart เมื่อเกิดปัญหา
- Logging อัตโนมัติ

### 🛠️ **ขั้นตอนการติดตั้ง:**

#### **1. ติดตั้ง Dependencies**
```bash
pip install pywin32 psutil
```

#### **2. รัน Service Manager**
```bash
python service_manager.py
```

#### **3. เลือก "1. ติดตั้ง Service"**

#### **4. เลือก "2. เริ่มต้น Service"**

### 📊 **การจัดการ Service:**

#### **ตรวจสอบสถานะ:**
```bash
python service_manager.py
# เลือก "5. ตรวจสอบสถานะ"
```

#### **รีสตาร์ท Service:**
```bash
python service_manager.py
# เลือก "4. รีสตาร์ท Service"
```

#### **หยุด Service:**
```bash
python service_manager.py
# เลือก "3. หยุด Service"
```

#### **ลบ Service:**
```bash
python service_manager.py
# เลือก "6. ลบ Service"
```

### 📝 **ดู Log:**
```bash
python service_manager.py
# เลือก "7. ดู Log"
```

หรือเปิดไฟล์: `logs/wawagot_service.log`

---

## 🚀 **วิธีที่ 2: Auto Startup**

### 📋 **ข้อดี:**
- รันอัตโนมัติเมื่อเปิดเครื่อง
- ไม่ต้อง Login ก็รันได้
- ง่ายต่อการจัดการ

### 🛠️ **ขั้นตอนการติดตั้ง:**

#### **1. รัน Auto Startup Manager**
```bash
python auto_startup_manager.py
```

#### **2. เลือก "1. เพิ่ม WAWAGOT.AI ลงใน Startup"**

#### **3. ตรวจสอบสถานะ**
```bash
python auto_startup_manager.py
# เลือก "3. ตรวจสอบสถานะ Startup"
```

### 📊 **การจัดการ Auto Startup:**

#### **ลบออกจาก Startup:**
```bash
python auto_startup_manager.py
# เลือก "2. ลบ WAWAGOT.AI ออกจาก Startup"
```

#### **สร้าง Startup Script:**
```bash
python auto_startup_manager.py
# เลือก "4. สร้าง Startup Script"
```

---

## 🎮 **วิธีที่ 3: Manual Management**

### 📋 **ข้อดี:**
- ควบคุมได้เต็มที่
- เห็นผลลัพธ์ทันที
- ง่ายต่อการ Debug

### 🛠️ **ขั้นตอนการรัน:**

#### **1. รันระบบหลัก**
```bash
python launch_v2.py
```

#### **2. รัน Dashboard**
```bash
python dashboard/app.py
```

#### **3. ตรวจสอบสถานะ**
```bash
python system_status_check.py
```

---

## 📊 **การตรวจสอบสถานะระบบ**

### 🔍 **ตรวจสอบ Service:**
```bash
# ตรวจสอบ Windows Service
services.msc
# ค้นหา "WAWAGOT.AI System Service"
```

### 📈 **ตรวจสอบ Process:**
```bash
# ตรวจสอบ Python processes
tasklist | findstr python

# ตรวจสอบ Chrome processes
tasklist | findstr chrome
```

### 📝 **ตรวจสอบ Log:**
```bash
# ดู Service log
type logs\wawagot_service.log

# ดู System log
python system_status_check.py
```

---

## ⚙️ **การตั้งค่า Environment Variables**

### 📁 **ไฟล์ที่ต้องตั้งค่า:**
- `wawagot_env_config.env` - Environment variables
- `config/ai.json` - AI configuration
- `config/supabase_config.json` - Database configuration

### 🔑 **API Keys ที่ต้องมี:**
- `OPENAI_API_KEY` - OpenAI API key
- `GEMINI_API_KEY` - Google Gemini API key
- `SUPABASE_URL` - Supabase URL
- `SUPABASE_KEY` - Supabase API key

---

## 🛠️ **การแก้ไขปัญหา**

### ❌ **Service ไม่เริ่มต้น:**
1. ตรวจสอบ Administrator privileges
2. ตรวจสอบ Python installation
3. ตรวจสอบ Dependencies
4. ดู Error log

### ❌ **ระบบไม่ทำงาน:**
1. ตรวจสอบ API keys
2. ตรวจสอบ Internet connection
3. ตรวจสอบ Database connection
4. ตรวจสอบ Chrome installation

### ❌ **Performance ปัญหา:**
1. ตรวจสอบ CPU/Memory usage
2. ปิด Chrome processes ที่ไม่จำเป็น
3. ปรับ GPU settings
4. ตรวจสอบ Disk space

---

## 📋 **คำสั่งที่ใช้บ่อย**

### 🚀 **เริ่มต้นระบบ:**
```bash
# Windows Service
python service_manager.py

# Manual
python launch_v2.py

# Dashboard
python dashboard/app.py
```

### 🛑 **หยุดระบบ:**
```bash
# Windows Service
python service_manager.py
# เลือก "3. หยุด Service"

# Manual
Ctrl+C
```

### 🔄 **รีสตาร์ทระบบ:**
```bash
# Windows Service
python service_manager.py
# เลือก "4. รีสตาร์ท Service"

# Manual
# หยุดแล้วเริ่มใหม่
```

### 📊 **ตรวจสอบสถานะ:**
```bash
# System Status
python system_status_check.py

# Service Status
python service_manager.py
# เลือก "5. ตรวจสอบสถานะ"
```

---

## 🎯 **คำแนะนำ**

### 🏆 **สำหรับ Production:**
1. ใช้ **Windows Service** เป็นหลัก
2. ตั้งค่า **Auto Startup** เป็น backup
3. ตรวจสอบ **Log** เป็นประจำ
4. ตั้งค่า **Monitoring** และ **Alerting**

### 🏠 **สำหรับ Development:**
1. ใช้ **Manual Management** เพื่อ Debug
2. ใช้ **Auto Startup** เพื่อความสะดวก
3. ตรวจสอบ **System Status** บ่อยๆ

### 🔧 **สำหรับ Maintenance:**
1. ตรวจสอบ **Log** ทุกวัน
2. **Backup** ข้อมูลเป็นประจำ
3. **Update** Dependencies เป็นระยะ
4. **Monitor** Performance

---

## 📞 **การขอความช่วยเหลือ**

### 📧 **เมื่อเกิดปัญหา:**
1. ตรวจสอบ **Log files**
2. รัน **System Status Check**
3. ตรวจสอบ **Error messages**
4. ดู **Troubleshooting Guide**

### 🔗 **ไฟล์ที่สำคัญ:**
- `logs/wawagot_service.log` - Service log
- `system_status_check.py` - System status
- `service_manager.py` - Service management
- `auto_startup_manager.py` - Startup management

---

## 🎉 **สรุป**

ระบบ WAWAGOT.AI สามารถรันตลอดเวลา 24/7 ได้ 3 วิธี:

1. **Windows Service** - สำหรับ Production
2. **Auto Startup** - สำหรับความสะดวก
3. **Manual Management** - สำหรับ Development

**ความมั่นใจ 100%** ว่าระบบจะทำงานได้อย่างเสถียรและต่อเนื่อง! 🚀 