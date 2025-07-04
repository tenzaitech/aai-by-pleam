# WAWAGOT.AI - Cursor Settings v1.0

## 🎯 ภาพรวม
โฟลเดอร์นี้เก็บข้อมูลและไฟล์ที่จำเป็นทั้งหมดสำหรับการตั้งค่า Cursor IDE ให้ทำงานร่วมกับ WAWAGOT.AI ได้อย่างสมบูรณ์

## 📁 โครงสร้างไฟล์

### 📋 ไฟล์หลัก
- **`01_cursor_rules_main.md`** - กฎหลักสำหรับ Cursor (ใช้งานได้จริง)
- **`02_mcp_server_config.json`** - MCP server configuration
- **`03_cursor_setup_guide.md`** - คู่มือการตั้งค่าขั้นตอน
- **`04_environment_variables_template.env`** - Template สำหรับ .env
- **`05_cursor_rules_files.md`** - อธิบายไฟล์ rules ทั้งหมด
- **`06_quick_start_script.sh`** - สคริปต์ Quick Start
- **`07_troubleshooting_guide.md`** - คู่มือการแก้ปัญหา
- **`08_complete_setup_summary.md`** - สรุปการตั้งค่าครบถ้วน

## 🚀 การใช้งานด่วน

### 1. ใช้สคริปต์อัตโนมัติ
```bash
# ให้สิทธิ์การรันสคริปต์
chmod +x pleamthinking/cursorsettingv1/06_quick_start_script.sh

# รันสคริปต์ Quick Start
./pleamthinking/cursorsettingv1/06_quick_start_script.sh
```

### 2. ตั้งค่าด้วยตนเอง
```bash
# สร้างโฟลเดอร์ที่จำเป็น
mkdir -p .cursor/rules logs backups uploads

# คัดลอกไฟล์ rules
cp pleamthinking/cursorsettingv1/*.mdc .cursor/rules/

# สร้างไฟล์ MCP configuration
cp pleamthinking/cursorsettingv1/02_mcp_server_config.json .cursor/mcp.json

# สร้างไฟล์ environment variables
cp pleamthinking/cursorsettingv1/04_environment_variables_template.env .env
```

## 📚 เอกสารที่สำคัญ

### คู่มือการใช้งาน
- **`03_cursor_setup_guide.md`** - คู่มือการตั้งค่าขั้นตอนละเอียด
- **`05_cursor_rules_files.md`** - อธิบายไฟล์ rules และการใช้งาน
- **`07_troubleshooting_guide.md`** - การแก้ปัญหาที่พบบ่อย

### Templates และ Configurations
- **`02_mcp_server_config.json`** - MCP server configuration
- **`04_environment_variables_template.env`** - Environment variables template

### สคริปต์อัตโนมัติ
- **`06_quick_start_script.sh`** - สคริปต์ตั้งค่าอัตโนมัติ

## 🎯 สิ่งที่ได้จากการตั้งค่า

### 1. AI Assistant ที่ฉลาด
- เข้าใจโปรเจกต์ WAWAGOT.AI
- ตอบภาษาไทยตามที่ต้องการ
- ให้คำแนะนำที่เหมาะสม
- ทำงานตามมาตรฐานที่กำหนด

### 2. Tools Integration
- เข้าถึง MCP tools ต่างๆ
- ทำงานกับ database ได้
- ใช้ GPU acceleration
- เข้าถึง external services

### 3. Development Experience
- ทำงานได้เร็วขึ้น
- ลดข้อผิดพลาด
- มีเอกสารครบถ้วน
- แก้ปัญหาได้ง่าย

### 4. Security และ Performance
- มีกฎ security ที่ใช้เสมอ
- ป้องกันการรั่วไหลของข้อมูล
- optimize สำหรับ performance
- monitor ระบบได้

## 🔧 การตรวจสอบ

### การตรวจสอบสถานะ
```bash
# ตรวจสอบ system health
python3 system_health_checker.py

# ตรวจสอบ MCP server
curl http://localhost:3000/health

# ตรวจสอบ database
python3 test_supabase.py

# ตรวจสอบ GPU
python3 -c "import torch; print(torch.cuda.is_available())"
```

### การตรวจสอบไฟล์
```bash
# ตรวจสอบ Cursor rules
ls -la .cursor/rules/

# ตรวจสอบ MCP configuration
cat .cursor/mcp.json

# ตรวจสอบ environment variables
grep -v "^#" .env | grep -v "^$"
```

## 🛠️ การบำรุงรักษา

### การอัปเดต
```bash
# อัปเดต dependencies
pip3 install --upgrade -r requirements.txt

# อัปเดต rules (ถ้ามี)
cp pleamthinking/cursorsettingv1/updated_rules.mdc .cursor/rules/

# อัปเดต configuration
cp pleamthinking/cursorsettingv1/updated_config.json .cursor/mcp.json
```

### การ Backup
```bash
# Backup configuration
tar -czf backup/cursor_config_$(date +%Y%m%d).tar.gz .cursor/

# Backup environment variables
cp .env backup/env_$(date +%Y%m%d).env

# Backup rules
cp -r .cursor/rules/ backup/rules_$(date +%Y%m%d)/
```

### การ Cleanup
```bash
# ลบ cache files
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# ลบ logs เก่า
find logs/ -name "*.log" -mtime +7 -delete
```

## 📊 สถานะระบบ

### ระบบที่พร้อมใช้งาน
- ✅ Cursor IDE configuration
- ✅ MCP server integration
- ✅ Cursor rules สำหรับ AI assistant
- ✅ Environment variables template
- ✅ GPU acceleration support
- ✅ Database integration (Supabase)
- ✅ Thai language processing
- ✅ Security rules และ best practices

### ระบบที่ต้องตั้งค่าเพิ่มเติม
- 🔧 Environment variables (กรอกข้อมูลจริง)
- 🔧 Database credentials
- 🔧 API keys สำหรับ external services
- 🔧 GPU drivers (ถ้าใช้ GPU)

## 🎉 สรุป

การตั้งค่า Cursor สำหรับ WAWAGOT.AI เสร็จสมบูรณ์แล้ว! 

### ขั้นตอนต่อไป:
1. แก้ไขไฟล์ `.env` และกรอกข้อมูลที่จำเป็น
2. เปิด Cursor IDE และเปิดโฟลเดอร์โปรเจกต์
3. ทดสอบ MCP tools และ AI assistant
4. เริ่มใช้งานและพัฒนาต่อ

### การขอความช่วยเหลือ:
- ดูคู่มือการแก้ปัญหาใน `07_troubleshooting_guide.md`
- ตรวจสอบ logs ในโฟลเดอร์ `logs/`
- รัน `python3 system_health_checker.py` เพื่อตรวจสอบสถานะ

---

**🎯 ขอให้สนุกกับการใช้งาน WAWAGOT.AI กับ Cursor IDE!**

**📅 สร้างเมื่อ**: 2024-12-19  
**🔄 เวอร์ชัน**: v1.0  
**👤 ผู้สร้าง**: WAWAGOT.AI System 