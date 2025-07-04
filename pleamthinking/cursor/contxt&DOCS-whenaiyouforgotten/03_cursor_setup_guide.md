# คู่มือการตั้งค่า Cursor สำหรับ WAWAGOT.AI (ใช้งานได้จริง)

## 🎯 ภาพรวม
คู่มือนี้จะแนะนำการตั้งค่า Cursor IDE ให้ทำงานร่วมกับ WAWAGOT.AI ได้อย่างมีประสิทธิภาพ

## 📋 ขั้นตอนการติดตั้ง

### 1. การติดตั้ง Cursor
```bash
# ดาวน์โหลด Cursor จาก https://cursor.sh
# ติดตั้งตามคำแนะนำของระบบปฏิบัติการ
```

### 2. การตั้งค่า MCP Server
1. **สร้างไฟล์ `.cursor/mcp.json`** ในโปรเจกต์:
```json
{
  "mcpServers": {
    "wawagot-ai-server": {
      "command": "python",
      "args": ["wawagot_mcp_server.py"],
      "env": {
        "PYTHONPATH": ".",
        "WAWAGOT_ENV": "development"
      }
    }
  }
}
```

2. **ตรวจสอบ MCP Server**:
```bash
# รัน MCP server
python wawagot_mcp_server.py

# ตรวจสอบ endpoint
curl http://localhost:3000/tools
```

### 3. การตั้งค่า Cursor Rules
1. **สร้างโฟลเดอร์ `.cursor/rules/`**
2. **คัดลอกไฟล์ rules** จาก `pleamthinking/cursorsettingv1/`:
   - `wawagot-ai-rules.mdc`
   - `thai-language-rules.mdc`
   - `ai-ml-rules.mdc`
   - `security-rules.mdc`

### 4. การตั้งค่า Environment Variables
1. **สร้างไฟล์ `.env`** จาก template:
```bash
cp env_template.txt .env
```

2. **กรอกข้อมูลที่จำเป็น**:
```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Google Services
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# AI Services
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# System
WAWAGOT_ENV=development
LOG_LEVEL=INFO
```

## 🔧 การตั้งค่าขั้นสูง

### 1. การตั้งค่า Python Environment
```bash
# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

### 2. การตั้งค่า GPU Support
```bash
# ตรวจสอบ CUDA
python -c "import torch; print(torch.cuda.is_available())"

# ติดตั้ง PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. การตั้งค่า Database
```bash
# รัน migrations
python database/migrate.py

# ตรวจสอบการเชื่อมต่อ
python test_supabase.py
```

## 🚀 การใช้งาน

### 1. การเปิดโปรเจกต์
```bash
# เปิด Cursor
cursor .

# หรือเปิดจาก Cursor IDE
# File > Open Folder > เลือกโฟลเดอร์โปรเจกต์
```

### 2. การทดสอบ MCP Tools
1. **เปิด Command Palette** (Ctrl+Shift+P)
2. **พิมพ์ "MCP"** เพื่อดู tools ที่ใช้ได้
3. **ทดสอบ tools** ต่างๆ

### 3. การใช้งาน AI Assistant
1. **เปิด Chat** (Ctrl+L)
2. **ถามคำถาม** เกี่ยวกับโปรเจกต์
3. **ใช้ AI** ช่วยเขียนโค้ดและแก้ปัญหา

## 🔍 การแก้ปัญหา

### ปัญหาที่พบบ่อย

#### 1. MCP Server ไม่ทำงาน
```bash
# ตรวจสอบ port
netstat -an | grep 3000

# ตรวจสอบ logs
tail -f logs/mcp_server.log

# รีสตาร์ท server
pkill -f wawagot_mcp_server.py
python wawagot_mcp_server.py
```

#### 2. Cursor Rules ไม่ทำงาน
```bash
# ตรวจสอบไฟล์ rules
ls -la .cursor/rules/

# ตรวจสอบ syntax
cat .cursor/rules/wawagot-ai-rules.mdc

# รีสตาร์ท Cursor
```

#### 3. Environment Variables ไม่ถูกโหลด
```bash
# ตรวจสอบไฟล์ .env
cat .env

# ตรวจสอบการโหลด
python -c "import os; print(os.getenv('SUPABASE_URL'))"
```

### การ Debug
```bash
# เปิด debug mode
export DEBUG=1
export LOG_LEVEL=DEBUG

# ตรวจสอบ logs
tail -f logs/*.log
```

## 📊 การตรวจสอบสถานะ

### 1. System Health Check
```bash
python system_health_checker.py
```

### 2. MCP Server Status
```bash
curl http://localhost:3000/health
```

### 3. Database Connection
```bash
python test_supabase.py
```

## 🔄 การบำรุงรักษา

### 1. การอัปเดต Dependencies
```bash
# อัปเดต Python packages
pip install --upgrade -r requirements.txt

# อัปเดต Node.js packages
npm update
```

### 2. การ Backup Configuration
```bash
# Backup Cursor settings
cp -r .cursor/ backup/cursor_settings/

# Backup environment variables
cp .env backup/env_backup/
```

### 3. การ Cleanup
```bash
# ลบ cache
rm -rf __pycache__/
rm -rf .pytest_cache/

# ลบ logs เก่า
find logs/ -name "*.log" -mtime +7 -delete
```

## 📚 ทรัพยากรเพิ่มเติม

### เอกสารที่เกี่ยวข้อง
- `docs/cursor_setup_guide.md` - คู่มือการตั้งค่าขั้นสูง
- `docs/API.md` - เอกสาร API
- `docs/TROUBLESHOOTING.md` - คู่มือการแก้ปัญหา

### ลิงก์ที่เป็นประโยชน์
- [Cursor Documentation](https://cursor.sh/docs)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Supabase Documentation](https://supabase.com/docs)

## 🎯 สรุป

การตั้งค่า Cursor สำหรับ WAWAGOT.AI ประกอบด้วย:
1. **การติดตั้ง MCP Server** สำหรับ tools integration
2. **การตั้งค่า Cursor Rules** สำหรับ AI assistant behavior
3. **การกำหนดค่า Environment Variables** สำหรับ services
4. **การทดสอบและตรวจสอบ** ระบบทั้งหมด

หลังจากตั้งค่าเสร็จแล้ว คุณจะสามารถ:
- ใช้ AI assistant ที่เข้าใจโปรเจกต์ของคุณ
- เข้าถึง tools และ services ต่างๆ ผ่าน MCP
- ทำงานได้อย่างมีประสิทธิภาพด้วย Cursor IDE

---

**หมายเหตุ**: คู่มือนี้จะอัปเดตตามการเปลี่ยนแปลงของระบบและ feedback จากผู้ใช้ 