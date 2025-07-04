# คู่มือการแก้ปัญหา Cursor Setup (ใช้งานได้จริง)

## 🚨 ปัญหาที่พบบ่อยและวิธีแก้ไข

### 1. MCP Server ไม่ทำงาน

#### อาการ
- ไม่เห็น MCP tools ใน Command Palette
- ข้อความ error เกี่ยวกับ MCP server
- ไม่สามารถเชื่อมต่อกับ localhost:3000

#### วิธีแก้ไข
```bash
# ตรวจสอบว่า MCP server ทำงานอยู่หรือไม่
ps aux | grep wawagot_mcp_server

# ตรวจสอบ port 3000
netstat -an | grep 3000

# รีสตาร์ท MCP server
pkill -f wawagot_mcp_server.py
python3 wawagot_mcp_server.py

# ตรวจสอบ logs
tail -f logs/mcp_server.log
```

#### การตรวจสอบ
```bash
# ทดสอบ endpoint
curl http://localhost:3000/tools

# ตรวจสอบไฟล์ mcp.json
cat .cursor/mcp.json
```

### 2. Cursor Rules ไม่ทำงาน

#### อาการ
- AI assistant ไม่ตอบตามกฎที่กำหนด
- ไม่เห็นการเปลี่ยนแปลงในพฤติกรรม
- ข้อความ error เกี่ยวกับ rules

#### วิธีแก้ไข
```bash
# ตรวจสอบไฟล์ rules
ls -la .cursor/rules/

# ตรวจสอบ syntax ของไฟล์ rules
cat .cursor/rules/wawagot-ai-rules.mdc | head -10

# รีสตาร์ท Cursor IDE
# ปิด Cursor และเปิดใหม่
```

#### การตรวจสอบ
```bash
# ตรวจสอบ globs patterns
grep -r "globs:" .cursor/rules/

# ตรวจสอบ alwaysApply settings
grep -r "alwaysApply" .cursor/rules/
```

### 3. Environment Variables ไม่ถูกโหลด

#### อาการ
- ข้อความ error เกี่ยวกับ missing environment variables
- ไม่สามารถเชื่อมต่อกับ database หรือ services
- ข้อความ "None" หรือ "undefined" ในค่าต่างๆ

#### วิธีแก้ไข
```bash
# ตรวจสอบไฟล์ .env
cat .env

# ตรวจสอบการโหลด environment variables
python3 -c "import os; print('SUPABASE_URL:', os.getenv('SUPABASE_URL'))"

# สร้างไฟล์ .env ใหม่
cp pleamthinking/cursorsettingv1/04_environment_variables_template.env .env
```

#### การตรวจสอบ
```bash
# ตรวจสอบว่ามีไฟล์ .env หรือไม่
ls -la .env

# ตรวจสอบ format ของไฟล์ .env
grep -v "^#" .env | grep -v "^$"
```

### 4. Python Dependencies ไม่ครบ

#### อาการ
- ImportError เมื่อรันโค้ด
- ModuleNotFoundError
- ข้อความ error เกี่ยวกับ packages

#### วิธีแก้ไข
```bash
# ตรวจสอบ Python version
python3 --version

# ตรวจสอบ installed packages
pip3 list

# ติดตั้ง dependencies
pip3 install -r requirements.txt

# อัปเดต pip
pip3 install --upgrade pip
```

#### การตรวจสอบ
```bash
# ตรวจสอบ virtual environment
which python3

# ตรวจสอบ packages ที่ติดตั้ง
pip3 freeze
```

### 5. GPU Support ไม่ทำงาน

#### อาการ
- ข้อความ "CUDA not available"
- การประมวลผลช้า
- ไม่สามารถใช้ GPU acceleration

#### วิธีแก้ไข
```bash
# ตรวจสอบ NVIDIA GPU
nvidia-smi

# ตรวจสอบ CUDA installation
nvcc --version

# ตรวจสอบ PyTorch CUDA support
python3 -c "import torch; print(torch.cuda.is_available())"

# ติดตั้ง PyTorch with CUDA
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### การตรวจสอบ
```bash
# ตรวจสอบ GPU memory
nvidia-smi --query-gpu=memory.used,memory.total --format=csv

# ตรวจสอบ CUDA devices
python3 -c "import torch; print(torch.cuda.device_count())"
```

### 6. Database Connection Issues

#### อาการ
- ไม่สามารถเชื่อมต่อกับ Supabase
- ข้อความ error เกี่ยวกับ database
- Timeout errors

#### วิธีแก้ไข
```bash
# ตรวจสอบ Supabase URL และ Key
echo $SUPABASE_URL
echo $SUPABASE_KEY

# ทดสอบการเชื่อมต่อ
python3 test_supabase.py

# ตรวจสอบ network connectivity
ping api.supabase.com
```

#### การตรวจสอบ
```bash
# ตรวจสอบ Supabase project
curl -H "apikey: $SUPABASE_KEY" "$SUPABASE_URL/rest/v1/"
```

### 7. Cursor IDE Performance Issues

#### อาการ
- Cursor ทำงานช้า
- ใช้ memory มาก
- เกิด lag หรือ freeze

#### วิธีแก้ไข
```bash
# ตรวจสอบ system resources
top
htop

# ลบ cache ของ Cursor
rm -rf ~/.cursor/Cache/
rm -rf ~/.cursor/User/workspaceStorage/

# ลดจำนวน rules
ls -la .cursor/rules/ | wc -l
```

#### การตรวจสอบ
```bash
# ตรวจสอบ memory usage
free -h

# ตรวจสอบ disk space
df -h
```

## 🔧 การ Debug ขั้นสูง

### 1. การเปิด Debug Mode
```bash
# เปิด debug mode
export DEBUG=1
export LOG_LEVEL=DEBUG

# รัน MCP server ใน debug mode
python3 wawagot_mcp_server.py --debug
```

### 2. การตรวจสอบ Logs
```bash
# ตรวจสอบ logs ทั้งหมด
ls -la logs/

# ดู logs ล่าสุด
tail -f logs/*.log

# ค้นหา error ใน logs
grep -i error logs/*.log
```

### 3. การตรวจสอบ Network
```bash
# ตรวจสอบ ports ที่ใช้งาน
netstat -tulpn | grep LISTEN

# ตรวจสอบ firewall
sudo ufw status

# ทดสอบ connectivity
curl -v http://localhost:3000/health
```

## 📊 การตรวจสอบสถานะระบบ

### 1. System Health Check
```bash
# รัน health checker
python3 system_health_checker.py

# ตรวจสอบ system status
python3 system_status_check.py
```

### 2. Performance Monitoring
```bash
# ตรวจสอบ CPU usage
top -p $(pgrep -f wawagot)

# ตรวจสอบ memory usage
ps aux | grep wawagot

# ตรวจสอบ disk I/O
iotop
```

### 3. Network Monitoring
```bash
# ตรวจสอบ network connections
ss -tulpn

# ตรวจสอบ bandwidth
iftop

# ตรวจสอบ latency
ping -c 5 api.supabase.com
```

## 🛠️ การบำรุงรักษา

### 1. การ Cleanup
```bash
# ลบ cache files
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# ลบ logs เก่า
find logs/ -name "*.log" -mtime +7 -delete

# ลบ temporary files
find . -name "*.tmp" -delete
```

### 2. การ Backup
```bash
# Backup configuration
tar -czf backup/cursor_config_$(date +%Y%m%d).tar.gz .cursor/

# Backup environment variables
cp .env backup/env_$(date +%Y%m%d).env

# Backup rules
cp -r .cursor/rules/ backup/rules_$(date +%Y%m%d)/
```

### 3. การ Update
```bash
# อัปเดต Python packages
pip3 install --upgrade -r requirements.txt

# อัปเดต Node.js packages
npm update

# อัปเดต system packages
sudo apt update && sudo apt upgrade
```

## 📞 การขอความช่วยเหลือ

### 1. ข้อมูลที่ต้องเตรียม
- ข้อความ error ที่เกิดขึ้น
- ระบบปฏิบัติการและ version
- Python version
- Cursor version
- Logs ที่เกี่ยวข้อง

### 2. การรายงานปัญหา
```bash
# สร้าง diagnostic report
python3 system_health_checker.py > diagnostic_report.txt

# รวม logs
tar -czf logs_$(date +%Y%m%d).tar.gz logs/

# สร้าง system info
uname -a > system_info.txt
python3 --version >> system_info.txt
```

### 3. การติดต่อ
- ตรวจสอบเอกสารใน `pleamthinking/cursorsettingv1/`
- ดูคู่มือการใช้งานใน `docs/`
- ตรวจสอบ GitHub issues

---

**หมายเหตุ**: คู่มือนี้จะอัปเดตตามปัญหาที่พบและ feedback จากผู้ใช้ 