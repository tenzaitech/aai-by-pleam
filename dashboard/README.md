# 🚀 WAWA AI System Dashboard

## 📋 **ภาพรวม**

Dashboard แบบ Real-time สำหรับระบบ WAWA AI ที่รวมการตรวจสอบสถานะระบบ การควบคุม God Mode Knowledge Base และการจัดการทรัพยากรระบบ

## ✨ **ฟีเจอร์หลัก**

### 🎯 **System Overview**
- **Real-time Status Monitoring** - ตรวจสอบสถานะระบบแบบ Real-time
- **Capability Status** - แสดงสถานะของแต่ละระบบย่อย
- **System Resources** - ตรวจสอบการใช้ CPU, Memory, Disk, GPU
- **Performance Metrics** - แสดงประสิทธิภาพของระบบ

### 🧠 **God Mode Knowledge Base**
- **Session Management** - จัดการ God Mode sessions
- **Command History** - ดูประวัติคำสั่งที่ใช้
- **Pattern Recognition** - แสดงรูปแบบที่ระบบเรียนรู้
- **Learning Analytics** - วิเคราะห์การเรียนรู้ของระบบ
- **Statistics Dashboard** - สถิติการใช้งาน

### 🔧 **System Control**
- **Chrome Process Management** - ควบคุม Chrome processes
- **Dashboard Restart** - รีสตาร์ท dashboard
- **Resource Monitoring** - ตรวจสอบทรัพยากรระบบ
- **Performance Optimization** - ปรับแต่งประสิทธิภาพ

### 📊 **Real-time Logs**
- **Live Log Monitoring** - ดู logs แบบ Real-time
- **Log Filtering** - กรอง logs ตามระดับ
- **Search & Export** - ค้นหาและส่งออก logs

## 🚀 **การติดตั้ง**

### 1. **ติดตั้ง Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **รัน Dashboard**
```bash
cd dashboard
python app.py
```

### 3. **เข้าถึง Dashboard**
เปิดเบราว์เซอร์ไปที่: `http://localhost:5000`

## 📁 **โครงสร้างไฟล์**

```
dashboard/
├── app.py                 # Flask application
├── templates/
│   └── dashboard.html     # Main dashboard template
├── static/
│   └── style.css         # Custom styles
└── README.md             # This file
```

## 🔌 **API Endpoints**

### **System Status**
- `GET /api/status` - ข้อมูลสถานะระบบ
- `GET /api/system/cleanup-chrome` - ล้าง Chrome processes
- `POST /api/system/restart-dashboard` - รีสตาร์ท dashboard

### **God Mode Knowledge**
- `GET /api/godmode/statistics` - สถิติ God Mode
- `GET /api/godmode/sessions` - รายการ sessions
- `GET /api/godmode/commands` - ประวัติคำสั่ง
- `GET /api/godmode/patterns` - รูปแบบที่เรียนรู้
- `GET /api/godmode/learnings` - การเรียนรู้
- `POST /api/godmode/start-session` - เริ่ม session ใหม่
- `POST /api/godmode/end-session` - จบ session
- `POST /api/godmode/save-command` - บันทึกคำสั่ง
- `POST /api/godmode/save-learning` - บันทึกการเรียนรู้

### **Knowledge Manager**
- `GET /api/knowledge/statistics` - สถิติ Knowledge Base
- `GET /api/knowledge/search` - ค้นหาความรู้
- `GET /api/knowledge/categories` - รายการหมวดหมู่
- `POST /api/knowledge/add` - เพิ่มความรู้
- `PUT /api/knowledge/update/<id>` - อัปเดตความรู้
- `DELETE /api/knowledge/delete/<id>` - ลบความรู้

## 🎨 **UI Components**

### **Status Cards**
- แสดงสถานะระบบแบบ Real-time
- Progress bars สำหรับการใช้งานทรัพยากร
- Color-coded status indicators

### **Capability Grid**
- แสดงสถานะของแต่ละระบบย่อย
- Hover effects และ animations
- Detailed descriptions

### **God Mode Panel**
- Session controls
- Statistics dashboard
- Command history viewer
- Pattern analysis

### **Resource Monitor**
- CPU usage graphs
- Memory consumption
- Disk space monitoring
- GPU status (if available)

### **Log Viewer**
- Real-time log streaming
- Level-based filtering
- Search functionality
- Export capabilities

## 🔧 **การกำหนดค่า**

### **Environment Variables**
```bash
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
```

### **Configuration Options**
- Port: 5000 (default)
- Host: 0.0.0.0 (all interfaces)
- Debug mode: True (development)
- Socket.IO: Enabled for real-time updates

## 📊 **การใช้งาน**

### **1. ตรวจสอบสถานะระบบ**
- ดู Overview tab สำหรับภาพรวม
- ตรวจสอบ Capabilities tab สำหรับรายละเอียด
- ดู Resources tab สำหรับการใช้งานทรัพยากร

### **2. จัดการ God Mode**
- เริ่ม/จบ sessions ใน God Mode tab
- ดูสถิติการใช้งาน
- ตรวจสอบประวัติคำสั่ง
- วิเคราะห์รูปแบบการเรียนรู้

### **3. ควบคุมระบบ**
- ล้าง Chrome processes
- รีสตาร์ท dashboard
- ตรวจสอบ logs
- ปรับแต่งการตั้งค่า

### **4. จัดการความรู้**
- เพิ่มความรู้ใหม่
- ค้นหาความรู้ที่มีอยู่
- อัปเดตหรือลบความรู้
- ดูสถิติการใช้งาน

## 🛠️ **การพัฒนา**

### **เพิ่มฟีเจอร์ใหม่**
1. เพิ่ม route ใน `app.py`
2. อัปเดต template ใน `dashboard.html`
3. เพิ่ม JavaScript functions
4. อัปเดต CSS styles

### **Customization**
- แก้ไข `style.css` สำหรับ UI
- ปรับแต่ง `dashboard.html` สำหรับ layout
- เพิ่ม API endpoints ใน `app.py`

## 🔍 **Troubleshooting**

### **Dashboard ไม่เริ่ม**
```bash
# ตรวจสอบ dependencies
pip install -r requirements.txt

# ตรวจสอบ port
netstat -an | grep 5000

# รันใน debug mode
python app.py --debug
```

### **Socket.IO ไม่ทำงาน**
```bash
# ตรวจสอบ CORS settings
# ตรวจสอบ firewall
# ตรวจสอบ browser console
```

### **God Mode ไม่เชื่อมต่อ**
```bash
# ตรวจสอบ God Mode Knowledge Manager
python -c "from alldata_godmode.god_mode_knowledge_manager import GodModeKnowledgeManager; print('OK')"

# ตรวจสอบ database
ls -la alldata_godmode/
```

## 📈 **Performance**

### **Optimization Tips**
- ใช้ caching สำหรับข้อมูลที่ไม่เปลี่ยนแปลงบ่อย
- ลด frequency ของ background updates
- ใช้ pagination สำหรับข้อมูลจำนวนมาก
- Optimize database queries

### **Monitoring**
- ตรวจสอบ CPU usage
- ตรวจสอบ memory consumption
- ตรวจสอบ network traffic
- ตรวจสอบ database performance

## 🔒 **Security**

### **Best Practices**
- ใช้ HTTPS ใน production
- ตั้งค่า CORS อย่างเหมาะสม
- Validate input data
- ใช้ authentication ถ้าจำเป็น
- ตรวจสอบ logs อย่างสม่ำเสมอ

## 📝 **Changelog**

### **v1.1.1** (Current)
- ✅ เพิ่ม God Mode Knowledge Base integration
- ✅ เพิ่ม Real-time system monitoring
- ✅ เพิ่ม Resource management
- ✅ เพิ่ม Advanced UI components
- ✅ เพิ่ม API endpoints
- ✅ เพิ่ม Log management

### **v1.0.0**
- ✅ Basic dashboard functionality
- ✅ System status monitoring
- ✅ Knowledge manager integration

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 **License**

MIT License - ดูไฟล์ LICENSE สำหรับรายละเอียด

## 📞 **Support**

หากมีปัญหาหรือคำถาม:
- สร้าง Issue ใน GitHub
- ตรวจสอบ Documentation
- ติดต่อทีมพัฒนา

---

**🚀 WAWA AI System Dashboard - Empowering AI with Real-time Control** 