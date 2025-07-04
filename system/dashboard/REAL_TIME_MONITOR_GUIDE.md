# 🚀 Real-time Monitor - คู่มือการใช้งาน

## 📋 ภาพรวม
Real-time Monitor เป็นระบบติดตามและแสดงผลข้อมูลแบบเรียลไทม์สำหรับ WAWAGOT V.2 ที่แสดง:
- System Logs แบบเรียลไทม์
- Active Workflows และสถานะ
- System Performance Metrics
- Alerts และ Notifications

## 🔗 การเข้าถึง

### วิธีที่ 1: ผ่าน Dashboard หลัก
1. เปิด Dashboard: `http://localhost:8000`
2. คลิกที่ "Real-time Monitor" ในเมนูด้านบน

### วิธีที่ 2: เข้าถึงโดยตรง
```
http://localhost:8000/real-time-monitor
```

## 🎯 ฟีเจอร์หลัก

### 1. System Logs
- แสดง logs จากทุก module ในระบบ
- กรองตาม Level (Debug, Info, Warning, Error, Critical)
- กรองตาม Module (Chrome Controller, AI Integration, etc.)
- Auto-refresh ทุก 5 วินาที
- Export logs เป็น JSON

### 2. Active Workflows
- แสดง workflows ที่กำลังทำงานอยู่
- Progress bar แสดงความคืบหน้า
- สถานะ: Pending, Running, Completed, Failed
- ประวัติ workflows ล่าสุด

### 3. System Performance
- CPU Usage (ปัจจุบันและเฉลี่ย 1 ชั่วโมง)
- Memory Usage (ปัจจุบันและเฉลี่ย 1 ชั่วโมง)
- Disk Usage (ปัจจุบันและเฉลี่ย 1 ชั่วโมง)
- จำนวน Active Processes
- Performance Alerts

### 4. Alerts & Notifications
- แสดง alerts ที่ยังไม่ได้รับการแก้ไข
- ระดับความรุนแรง: Info, Warning, Error, Critical
- Auto-dismiss สำหรับ alerts ระดับต่ำ
- Manual acknowledge สำหรับ alerts สำคัญ

## 🎮 การควบคุม

### Connection Status
- **Connected**: เชื่อมต่อกับ backend สำเร็จ
- **Disconnected**: ไม่สามารถเชื่อมต่อได้
- **Reconnecting**: กำลังพยายามเชื่อมต่อใหม่

### Control Buttons
- **Refresh**: อัพเดทข้อมูลทันที
- **Auto Refresh**: เปิด/ปิดการอัพเดทอัตโนมัติ
- **Reset Status**: รีเซ็ตสถานะการเชื่อมต่อ

### Log Controls
- **Clear**: ลบ logs ทั้งหมด
- **Export**: ดาวน์โหลด logs เป็นไฟล์

## 📊 การกรองข้อมูล

### Log Level Filter
- All Levels
- Debug
- Info
- Warning
- Error
- Critical

### Module Filter
- All Modules
- Auto Learning
- Knowledge Manager
- Chrome Controller
- AI Integration
- Command Processor
- Supabase
- Visual Recognition
- Backup Controller
- System Monitor
- Thai Processor
- Direct Control
- Screen Reader
- Master Controller
- Environment Cards
- Config Manager

## 🔧 การตั้งค่า

### Auto-refresh Interval
- ปรับได้ระหว่าง 1-60 วินาที
- ค่าเริ่มต้น: 5 วินาที

### Log Retention
- เก็บ logs ไว้ 1 วัน
- Auto-cleanup ทุก 24 ชั่วโมง

### Alert Rules
- Info: Auto-dismiss หลังจาก 30 วินาที
- Warning: Auto-dismiss หลังจาก 2 นาที
- Error: ต้อง acknowledge เอง
- Critical: ต้อง acknowledge เอง + แสดง popup

## 🚨 การแก้ไขปัญหา

### ไม่สามารถเชื่อมต่อได้
1. ตรวจสอบว่า dashboard กำลังทำงานที่ port 8000
2. ตรวจสอบ firewall settings
3. รีสตาร์ท dashboard

### ไม่แสดงข้อมูล
1. ตรวจสอบว่า logging system ทำงานอยู่
2. ตรวจสอบ database connection
3. ดู error logs ใน browser console

### Performance Issues
1. ลด auto-refresh interval
2. ลดจำนวน logs ที่แสดง
3. ใช้ filter เพื่อลดข้อมูล

## 📱 Responsive Design
- รองรับ Desktop, Tablet, Mobile
- Auto-adjust layout ตามขนาดหน้าจอ
- Touch-friendly controls บน mobile

## 🔒 Security
- WebSocket connection ใช้ CORS protection
- API endpoints มี rate limiting
- Logs ไม่เก็บข้อมูลที่ละเอียดอ่อน

## 📈 การใช้งานขั้นสูง

### Custom Alerts
สามารถสร้าง custom alert rules ได้ผ่าน API:
```python
from system.core.logging.alert_system import get_alert_system

alert_system = get_alert_system()
alert_system.create_alert(
    level="warning",
    message="Custom alert message",
    module="custom_module",
    data={"key": "value"}
)
```

### Performance Monitoring
ติดตาม performance metrics แบบ custom:
```python
from system.core.logging.performance_tracker import get_performance_tracker

tracker = get_performance_tracker()
tracker.record_metric("custom_metric", 42.5)
```

### Workflow Tracking
ติดตาม custom workflows:
```python
from system.core.logging.workflow_monitor import get_workflow_monitor

monitor = get_workflow_monitor()
workflow_id = monitor.start_workflow("custom_workflow", {"param": "value"})
monitor.update_progress(workflow_id, 50)
monitor.complete_workflow(workflow_id, "success")
```

## 🎯 การใช้งานในชีวิตจริง

### ตัวอย่างการใช้งาน
1. **Development**: ติดตามการทำงานของ AI modules
2. **Debugging**: ดู logs เพื่อหาสาเหตุของปัญหา
3. **Monitoring**: ติดตาม performance ของระบบ
4. **Alerting**: รับการแจ้งเตือนเมื่อมีปัญหา

### Best Practices
1. เปิด real-time monitor ไว้ตลอดเวลาขณะพัฒนา
2. ตั้ง alert rules ที่เหมาะสม
3. ใช้ filters เพื่อลด noise
4. Export logs อย่างสม่ำเสมอเพื่อ backup

---

**🎉 Real-time Monitor พร้อมใช้งานแล้ว!**
เข้าถึงได้ที่: `http://localhost:8000/real-time-monitor` 