# 🧠 WAWAGOT.AI - Context & Documentation for AI Memory

โฟลเดอร์นี้เก็บเอกสารและไฟล์ที่จำเป็นทั้งหมดสำหรับการตั้งค่า Cursor IDE และการกระตุ้นความทรงจำของ AI assistant เมื่อลืมหรือต้องการตั้งค่าใหม่

## 📁 ไฟล์ในโฟลเดอร์

### 🎯 **ไฟล์หลักสำหรับการตั้งค่า Cursor**

#### 📋 [01_cursor_rules_main.md](./01_cursor_rules_main.md)
**Cursor Rules หลัก** - กฎการทำงานของ AI assistant
- กฎการสื่อสาร (ภาษาไทย)
- รูปแบบการทำงาน (ละเอียดและครอบคลุม)
- ความชอบทางเทคนิค
- การบูรณาการความทรงจำระยะยาว

#### ⚙️ [02_mcp_server_config.json](./02_mcp_server_config.json)
**MCP Server Configuration** - การตั้งค่า MCP server
- Server endpoints
- Tool definitions
- Connection settings

#### 📖 [03_cursor_setup_guide.md](./03_cursor_setup_guide.md)
**คู่มือการตั้งค่า Cursor** - ขั้นตอนการตั้งค่าทั้งหมด
- การติดตั้ง dependencies
- การตั้งค่า environment variables
- การตั้งค่า MCP server
- การทดสอบระบบ

#### 🔧 [04_environment_variables_template.env](./04_environment_variables_template.env)
**Environment Variables Template** - เทมเพลตไฟล์ .env
- Supabase configuration
- AI services API keys
- System settings
- Security configuration

#### 📝 [05_cursor_rules_files.md](./05_cursor_rules_files.md)
**คำอธิบายไฟล์ Cursor Rules** - รายละเอียดไฟล์ทั้งหมด
- วัตถุประสงค์ของแต่ละไฟล์
- วิธีการใช้งาน
- การบำรุงรักษา

#### 🚀 [06_quick_start_script.sh](./06_quick_start_script.sh)
**สคริปต์ Quick Start** - การตั้งค่าอัตโนมัติ
- การติดตั้ง dependencies
- การตั้งค่าไฟล์
- การทดสอบระบบ

#### 🔧 [07_troubleshooting_guide.md](./07_troubleshooting_guide.md)
**คู่มือการแก้ปัญหา** - แก้ปัญหาที่พบบ่อย
- ปัญหา MCP server
- ปัญหาการเชื่อมต่อฐานข้อมูล
- ปัญหา GPU/CUDA
- การแก้ไขทั่วไป

#### 📊 [08_complete_setup_summary.md](./08_complete_setup_summary.md)
**สรุปการตั้งค่าครบถ้วน** - สรุปขั้นตอนทั้งหมด
- ขั้นตอนการตั้งค่า
- การตรวจสอบสถานะ
- คำแนะนำการบำรุงรักษา

### 🌐 **HTML Documentation (สำหรับ Cursor Docs)**

#### 🏠 [index.html](./index.html)
**Documentation หลัก** - ภาพรวมระบบครบถ้วน
- ภาพรวมระบบ WAWAGOT.AI
- สถาปัตยกรรมและเทคโนโลยี
- การตั้งค่าและใช้งาน
- API และ Components

#### 🔌 [api-reference.html](./api-reference.html)
**API Reference** - เอกสาร API ครบถ้วน
- MCP Server Endpoints
- Dashboard API
- AI Services API
- ตัวอย่างการใช้งาน

#### 🏗️ [architecture.html](./architecture.html)
**System Architecture** - สถาปัตยกรรมระบบ
- Core Components
- Data Flow
- Security Architecture
- Scalability & Deployment

#### 🚀 [quick-start.html](./quick-start.html)
**Quick Start Guide** - คู่มือการเริ่มต้น
- ข้อกำหนดระบบ
- การติดตั้ง step-by-step
- การทดสอบระบบ
- การแก้ปัญหา

#### 📚 [README.md](./README.md)
**คู่มือการใช้งาน docs** - อธิบายไฟล์ HTML
- การใช้งานใน Cursor IDE
- การบำรุงรักษา
- Template สำหรับไฟล์ใหม่

## 🎯 วิธีการใช้งาน

### สำหรับการตั้งค่า Cursor ใหม่
1. **อ่าน** [03_cursor_setup_guide.md](./03_cursor_setup_guide.md)
2. **คัดลอก** [01_cursor_rules_main.md](./01_cursor_rules_main.md) เป็น `.cursorrules`
3. **คัดลอก** [02_mcp_server_config.json](./02_mcp_server_config.json) เป็น `.cursor/mcp.json`
4. **ตั้งค่า** environment variables จาก [04_environment_variables_template.env](./04_environment_variables_template.env)
5. **รัน** [06_quick_start_script.sh](./06_quick_start_script.sh) (ถ้าต้องการ)

### สำหรับการกระตุ้นความทรงจำ AI
1. **อ่าน** [01_cursor_rules_main.md](./01_cursor_rules_main.md) เพื่อทบทวนกฎการทำงาน
2. **ตรวจสอบ** [08_complete_setup_summary.md](./08_complete_setup_summary.md) เพื่อดูสถานะระบบ
3. **ใช้** HTML docs เป็น reference สำหรับการพัฒนา

### สำหรับ Cursor Docs Feature
1. **เพิ่มโฟลเดอร์นี้** เป็น custom docs ใน Cursor IDE
2. **Cursor จะ crawl และ index** ไฟล์ HTML ทั้งหมด
3. **AI assistant จะเข้าใจ** โปรเจกต์ได้ดีขึ้น

## 🔄 ขั้นตอนการตั้งค่า Cursor อย่างรวดเร็ว

```bash
# 1. คัดลอกไฟล์หลัก
cp 01_cursor_rules_main.md .cursorrules
mkdir -p .cursor
cp 02_mcp_server_config.json .cursor/mcp.json

# 2. ตั้งค่า environment variables
cp 04_environment_variables_template.env .env
# แก้ไข .env ด้วย credentials ของคุณ

# 3. รัน quick start script (optional)
chmod +x 06_quick_start_script.sh
./06_quick_start_script.sh

# 4. เปิด Cursor IDE
cursor .
```

## 📞 การขอความช่วยเหลือ

หากมีปัญหา:
1. **ตรวจสอบ** [07_troubleshooting_guide.md](./07_troubleshooting_guide.md)
2. **อ่าน** [08_complete_setup_summary.md](./08_complete_setup_summary.md)
3. **รัน** system health checker
4. **ตรวจสอบ** logs ในโฟลเดอร์ `logs/`

## 🎯 วัตถุประสงค์ของโฟลเดอร์นี้

- **เก็บความทรงจำ** ของการตั้งค่า Cursor IDE
- **อำนวยความสะดวก** ในการตั้งค่าใหม่
- **เป็น reference** สำหรับการพัฒนา
- **ช่วย AI assistant** เข้าใจโปรเจกต์ได้ดีขึ้น
- **ลดเวลา** ในการตั้งค่าและแก้ปัญหา

---

**สร้างเมื่อ:** 2024-12-19  
**วัตถุประสงค์:** Context & Documentation for AI Memory  
**สถานะ:** Complete ✅ 