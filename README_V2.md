# WAWAGOT V.2 - AI-Powered Chrome Automation System

## 🚀 ภาพรวม

WAWAGOT V.2 เป็นระบบ AI-powered Chrome automation ที่พัฒนาขึ้นใหม่ด้วยสถาปัตยกรรม Web Application ที่ทันสมัย ประกอบด้วย Backend API Server และ Frontend Dashboard ที่สวยงาม

## ✨ คุณสมบัติหลัก

### 🤖 AI Integration
- **OpenAI GPT-4 Vision** - ประมวลผลภาพและข้อความ
- **Thai Language Processing** - รองรับภาษาไทยเต็มรูปแบบ
- **Natural Language Commands** - สั่งการด้วยภาษาธรรมชาติ
- **Visual Recognition** - วิเคราะห์ภาพและ OCR

### 🌐 Chrome Automation
- **Browser Control** - ควบคุม Chrome ผ่าน API
- **Web Scraping** - ดึงข้อมูลจากเว็บไซต์
- **Screenshot & Recording** - ถ่ายภาพและบันทึกหน้าจอ
- **Form Automation** - กรอกฟอร์มอัตโนมัติ

### 🧠 Knowledge Management
- **Vector Database** - เก็บข้อมูลระยะยาวใน Supabase
- **Local/Cloud Storage** - เลือกเก็บข้อมูลในเครื่องหรือ Cloud
- **Smart Search** - ค้นหาข้อมูลแบบฉลาด
- **Learning System** - ระบบเรียนรู้และปรับปรุง

### 🔧 System Features
- **Parallel Processing** - ทำงานหลายอย่างพร้อมกัน
- **Background Tasks** - ทำงานเบื้องหลังอัตโนมัติ
- **Real-time Monitoring** - ดูสถานะการทำงานแบบ Real-time
- **Error Handling** - จัดการข้อผิดพลาดอย่างครอบคลุม

### 🌍 Integrations
- **LINE Bot** - เชื่อมต่อ LINE Bot
- **n8n Workflows** - อัตโนมัติขั้นสูง
- **OSINT Tools** - เครื่องมือค้นหาข้อมูล
- **API Endpoints** - RESTful API สำหรับการเชื่อมต่อ

## 🏗️ สถาปัตยกรรม

```
WAWAGOT V.2
├── Backend (FastAPI)
│   ├── API Server (Port 8000)
│   ├── Master Controller
│   ├── Chrome Controller
│   ├── AI Integration
│   ├── Knowledge Manager
│   └── Visual Recognition
├── Frontend (Web Dashboard)
│   ├── Modern UI (Port 3000)
│   ├── Real-time Updates
│   ├── Configuration Panel
│   └── System Monitoring
└── Database
    ├── Supabase (Vector DB)
    ├── Local Storage
    └── Backup System
```

## 📋 ความต้องการระบบ

### ระบบปฏิบัติการ
- Windows 10/11
- macOS 10.15+
- Ubuntu 18.04+

### Python
- Python 3.8+
- pip package manager

### Dependencies
- FastAPI & Uvicorn
- OpenAI API
- Selenium WebDriver
- Supabase Client
- OpenCV & Tesseract
- PyThaiNLP

## 🚀 การติดตั้ง

### 1. Clone Repository
```bash
git clone <repository-url>
cd wawagot.ai
```

### 2. ติดตั้ง Dependencies
```bash
pip install -r requirements_v2.txt
```

### 3. ตั้งค่า Environment Variables
สร้างไฟล์ `.env` และกำหนดค่า:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# System Configuration
WAWAGOT_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Chrome Configuration
CHROME_HEADLESS=false
CHROME_TIMEOUT=30

# AI Configuration
AI_MODEL=gpt-4-vision-preview
AI_TEMPERATURE=0.7
```

### 4. รันระบบ
```bash
python launch_v2.py
```

## 🌐 การใช้งาน

### 1. เข้าถึง Dashboard
เปิดเบราว์เซอร์ไปที่: `http://localhost:3000`

### 2. API Documentation
ดู API docs ที่: `http://localhost:8000/docs`

### 3. ตัวอย่างการใช้งาน

#### ส่งคำสั่ง AI
```bash
curl -X POST "http://localhost:8000/api/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "เปิดเว็บ Google และค้นหาข้อมูล",
    "language": "thai"
  }'
```

#### ควบคุม Chrome
```bash
curl -X POST "http://localhost:8000/api/chrome" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "navigate",
    "url": "https://www.google.com"
  }'
```

#### ประมวลผล AI
```bash
curl -X POST "http://localhost:8000/api/ai" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "วิเคราะห์ภาพนี้",
    "use_vision": true
  }'
```

## 📊 Dashboard Features

### 🎯 แดชบอร์ดหลัก
- สถานะระบบแบบ Real-time
- การดำเนินการด่วน
- บันทึกระบบ
- สถิติการใช้งาน

### 💬 คำสั่ง AI
- ส่งคำสั่งภาษาไทย/อังกฤษ
- ประวัติคำสั่ง
- ผลลัพธ์การประมวลผล

### 🌐 ควบคุม Chrome
- การนำทางเว็บไซต์
- การโต้ตอบกับหน้าเว็บ
- การถ่ายภาพหน้าจอ
- การเลื่อนและรีเฟรช

### 🧠 AI Processing
- ประมวลผลข้อความ
- วิเคราะห์ภาพ
- การตั้งค่า AI Model

### 👁️ Visual Recognition
- อัปโหลดและวิเคราะห์ภาพ
- OCR ข้อความ
- การจดจำวัตถุ

### 📚 ฐานความรู้
- ค้นหาข้อมูล
- เพิ่มข้อมูลใหม่
- จัดการฐานความรู้

### ⚙️ การตั้งค่า
- ตั้งค่า Chrome
- ตั้งค่า AI
- ตั้งค่าระบบ
- การสำรองข้อมูล

## 🔧 การพัฒนา

### โครงสร้างโปรเจค
```
wawagot.ai/
├── api_server.py          # FastAPI Backend
├── launch_v2.py           # System Launcher
├── requirements_v2.txt    # Dependencies
├── frontend/              # Frontend Files
│   ├── index.html
│   ├── style.css
│   └── script.js
├── system/                # Core System
│   └── core/
│       └── controllers/
├── config/                # Configuration
├── logs/                  # Log Files
├── data/                  # Data Storage
└── docs/                  # Documentation
```

### การเพิ่ม Feature ใหม่
1. สร้าง API endpoint ใน `api_server.py`
2. เพิ่ม UI component ใน `frontend/`
3. อัปเดต JavaScript ใน `script.js`
4. ทดสอบและ debug

## 🚀 การ Deploy

### Local Development
```bash
python launch_v2.py
```

### Production (Render)
1. สร้าง Render account
2. Connect GitHub repository
3. ตั้งค่า environment variables
4. Deploy

### Docker (Coming Soon)
```bash
docker build -t wawagot-v2 .
docker run -p 8000:8000 -p 3000:3000 wawagot-v2
```

## 🔒 ความปลอดภัย

### API Security
- CORS protection
- Input validation
- Rate limiting
- Error handling

### Data Protection
- Environment variables
- Secure API keys
- Data encryption
- Backup system

## 📈 Performance

### Optimization
- Async processing
- Parallel execution
- Caching system
- Memory management

### Monitoring
- System health checks
- Performance metrics
- Error tracking
- Usage analytics

## 🐛 การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

#### 1. Chrome Driver Error
```bash
# ติดตั้ง ChromeDriver
pip install webdriver-manager
```

#### 2. OpenAI API Error
```bash
# ตรวจสอบ API Key
echo $OPENAI_API_KEY
```

#### 3. Supabase Connection Error
```bash
# ตรวจสอบ Supabase credentials
cat .env | grep SUPABASE
```

#### 4. Port Already in Use
```bash
# เปลี่ยน port ใน launch_v2.py
backend_url = "http://localhost:8001"
frontend_url = "http://localhost:3001"
```

## 📞 การสนับสนุน

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [System Architecture](./docs/ARCHITECTURE.md)
- [Development Guide](./docs/DEVELOPMENT.md)

### Issues & Bugs
- สร้าง Issue ใน GitHub
- ตรวจสอบ logs ใน `logs/` folder
- ใช้ debug mode: `DEBUG=true`

### Community
- Discord Server
- GitHub Discussions
- Email Support

## 🎯 Roadmap

### Version 2.1 (Q2 2024)
- [ ] Mobile App
- [ ] Advanced AI Models
- [ ] Multi-language Support
- [ ] Plugin System

### Version 2.2 (Q3 2024)
- [ ] Cloud Deployment
- [ ] Enterprise Features
- [ ] Advanced Analytics
- [ ] API Marketplace

### Version 2.3 (Q4 2024)
- [ ] AI Agent Framework
- [ ] Workflow Automation
- [ ] Integration Hub
- [ ] Advanced Security

## 📄 License

MIT License - ดูรายละเอียดใน [LICENSE](LICENSE) file

## 👥 Contributors

- **WAWA** - Lead Developer
- **AI Assistant** - Development Support
- **Community** - Testing & Feedback

## 🙏 Acknowledgments

- OpenAI สำหรับ GPT-4
- Supabase สำหรับ Database
- FastAPI Community
- Thai NLP Community

---

**WAWAGOT V.2** - เร็วขึ้น 5 เท่า ด้วย AI 🚀 