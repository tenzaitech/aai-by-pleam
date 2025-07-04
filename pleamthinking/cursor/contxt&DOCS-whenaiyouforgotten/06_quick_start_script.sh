#!/bin/bash

# ===============================================================================
# WAWAGOT.AI - Cursor Setup Quick Start Script
# ===============================================================================
# สคริปต์นี้จะตั้งค่า Cursor IDE ให้ทำงานร่วมกับ WAWAGOT.AI ได้อย่างรวดเร็ว
# ===============================================================================

echo "🚀 เริ่มต้นการตั้งค่า Cursor สำหรับ WAWAGOT.AI..."

# ===============================================================================
# 1. สร้างโฟลเดอร์ที่จำเป็น
# ===============================================================================
echo "📁 สร้างโฟลเดอร์ที่จำเป็น..."

# สร้างโฟลเดอร์ .cursor/rules
mkdir -p .cursor/rules

# สร้างโฟลเดอร์ logs
mkdir -p logs

# สร้างโฟลเดอร์ backups
mkdir -p backups

# สร้างโฟลเดอร์ uploads
mkdir -p uploads

echo "✅ สร้างโฟลเดอร์เสร็จสิ้น"

# ===============================================================================
# 2. คัดลอกไฟล์ Cursor Rules
# ===============================================================================
echo "📋 คัดลอกไฟล์ Cursor Rules..."

# ตรวจสอบว่าไฟล์ต้นฉบับมีอยู่หรือไม่
if [ -f "pleamthinking/cursorsettingv1/wawagot-ai-rules.mdc" ]; then
    cp pleamthinking/cursorsettingv1/wawagot-ai-rules.mdc .cursor/rules/
    echo "✅ คัดลอก wawagot-ai-rules.mdc"
else
    echo "⚠️  ไม่พบไฟล์ wawagot-ai-rules.mdc"
fi

if [ -f "pleamthinking/cursorsettingv1/thai-language-rules.mdc" ]; then
    cp pleamthinking/cursorsettingv1/thai-language-rules.mdc .cursor/rules/
    echo "✅ คัดลอก thai-language-rules.mdc"
else
    echo "⚠️  ไม่พบไฟล์ thai-language-rules.mdc"
fi

if [ -f "pleamthinking/cursorsettingv1/ai-ml-rules.mdc" ]; then
    cp pleamthinking/cursorsettingv1/ai-ml-rules.mdc .cursor/rules/
    echo "✅ คัดลอก ai-ml-rules.mdc"
else
    echo "⚠️  ไม่พบไฟล์ ai-ml-rules.mdc"
fi

if [ -f "pleamthinking/cursorsettingv1/security-rules.mdc" ]; then
    cp pleamthinking/cursorsettingv1/security-rules.mdc .cursor/rules/
    echo "✅ คัดลอก security-rules.mdc"
else
    echo "⚠️  ไม่พบไฟล์ security-rules.mdc"
fi

# ===============================================================================
# 3. สร้างไฟล์ MCP Configuration
# ===============================================================================
echo "🔧 สร้างไฟล์ MCP Configuration..."

cat > .cursor/mcp.json << 'EOF'
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
EOF

echo "✅ สร้างไฟล์ .cursor/mcp.json"

# ===============================================================================
# 4. สร้างไฟล์ Environment Variables
# ===============================================================================
echo "🌍 สร้างไฟล์ Environment Variables..."

if [ -f "pleamthinking/cursorsettingv1/04_environment_variables_template.env" ]; then
    cp pleamthinking/cursorsettingv1/04_environment_variables_template.env .env
    echo "✅ สร้างไฟล์ .env จาก template"
    echo "⚠️  กรุณาแก้ไขไฟล์ .env และกรอกข้อมูลที่จำเป็น"
else
    echo "⚠️  ไม่พบไฟล์ environment template"
fi

# ===============================================================================
# 5. ตรวจสอบ Dependencies
# ===============================================================================
echo "📦 ตรวจสอบ Dependencies..."

# ตรวจสอบ Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 พร้อมใช้งาน"
    python3 --version
else
    echo "❌ ไม่พบ Python3 กรุณาติดตั้งก่อน"
fi

# ตรวจสอบ pip
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 พร้อมใช้งาน"
else
    echo "❌ ไม่พบ pip3 กรุณาติดตั้งก่อน"
fi

# ตรวจสอบ Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js พร้อมใช้งาน"
    node --version
else
    echo "⚠️  ไม่พบ Node.js (ไม่จำเป็นสำหรับการทำงานพื้นฐาน)"
fi

# ===============================================================================
# 6. ติดตั้ง Python Dependencies
# ===============================================================================
echo "📦 ติดตั้ง Python Dependencies..."

if [ -f "requirements.txt" ]; then
    echo "กำลังติดตั้ง dependencies จาก requirements.txt..."
    pip3 install -r requirements.txt
    echo "✅ ติดตั้ง dependencies เสร็จสิ้น"
else
    echo "⚠️  ไม่พบไฟล์ requirements.txt"
fi

# ===============================================================================
# 7. ตรวจสอบ MCP Server
# ===============================================================================
echo "🔍 ตรวจสอบ MCP Server..."

if [ -f "wawagot_mcp_server.py" ]; then
    echo "✅ พบไฟล์ wawagot_mcp_server.py"
    
    # ทดสอบรัน MCP server
    echo "🧪 ทดสอบรัน MCP server..."
    timeout 5s python3 wawagot_mcp_server.py &
    MCP_PID=$!
    sleep 2
    
    # ตรวจสอบว่า server ทำงานหรือไม่
    if curl -s http://localhost:3000/tools > /dev/null 2>&1; then
        echo "✅ MCP server ทำงานปกติ"
    else
        echo "⚠️  MCP server อาจมีปัญหา กรุณาตรวจสอบ logs"
    fi
    
    # หยุด MCP server
    kill $MCP_PID 2>/dev/null
else
    echo "❌ ไม่พบไฟล์ wawagot_mcp_server.py"
fi

# ===============================================================================
# 8. ตรวจสอบ GPU Support
# ===============================================================================
echo "🎮 ตรวจสอบ GPU Support..."

# ตรวจสอบ CUDA
if command -v nvidia-smi &> /dev/null; then
    echo "✅ พบ NVIDIA GPU"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
else
    echo "⚠️  ไม่พบ NVIDIA GPU หรือ CUDA driver"
fi

# ตรวจสอบ PyTorch
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')" 2>/dev/null || echo "⚠️  PyTorch ยังไม่ได้ติดตั้ง"

# ===============================================================================
# 9. สร้างไฟล์ README สำหรับ Cursor
# ===============================================================================
echo "📚 สร้างไฟล์ README..."

cat > .cursor/README.md << 'EOF'
# Cursor Setup for WAWAGOT.AI

## ไฟล์ที่สำคัญ
- `.cursor/mcp.json` - MCP server configuration
- `.cursor/rules/` - Cursor rules สำหรับ AI assistant
- `.env` - Environment variables (กรุณาแก้ไข)

## การใช้งาน
1. เปิด Cursor IDE
2. เปิดโฟลเดอร์โปรเจกต์
3. ตรวจสอบ MCP tools ใน Command Palette (Ctrl+Shift+P)
4. เริ่มใช้งาน AI assistant

## การแก้ปัญหา
- ตรวจสอบ logs ในโฟลเดอร์ logs/
- ตรวจสอบไฟล์ .env ว่ากรอกข้อมูลครบถ้วน
- รีสตาร์ท Cursor หากมีปัญหา
EOF

echo "✅ สร้างไฟล์ README"

# ===============================================================================
# 10. สรุปผลการตั้งค่า
# ===============================================================================
echo ""
echo "🎉 การตั้งค่าเสร็จสิ้น!"
echo ""
echo "📋 สรุปสิ่งที่ทำ:"
echo "✅ สร้างโฟลเดอร์ที่จำเป็น"
echo "✅ คัดลอกไฟล์ Cursor Rules"
echo "✅ สร้างไฟล์ MCP Configuration"
echo "✅ สร้างไฟล์ Environment Variables"
echo "✅ ตรวจสอบ Dependencies"
echo "✅ ติดตั้ง Python Dependencies"
echo "✅ ตรวจสอบ MCP Server"
echo "✅ ตรวจสอบ GPU Support"
echo "✅ สร้างไฟล์ README"
echo ""
echo "🚀 ขั้นตอนต่อไป:"
echo "1. แก้ไขไฟล์ .env และกรอกข้อมูลที่จำเป็น"
echo "2. เปิด Cursor IDE และเปิดโฟลเดอร์โปรเจกต์"
echo "3. ทดสอบ MCP tools ใน Command Palette"
echo "4. เริ่มใช้งาน AI assistant"
echo ""
echo "📚 เอกสารเพิ่มเติม:"
echo "- pleamthinking/cursorsettingv1/03_cursor_setup_guide.md"
echo "- pleamthinking/cursorsettingv1/05_cursor_rules_files.md"
echo ""
echo "🔧 การแก้ปัญหา:"
echo "- ตรวจสอบ logs ในโฟลเดอร์ logs/"
echo "- รัน python3 system_health_checker.py"
echo "- ตรวจสอบไฟล์ .env"
echo ""
echo "🎯 ขอให้สนุกกับการใช้งาน WAWAGOT.AI กับ Cursor IDE!" 