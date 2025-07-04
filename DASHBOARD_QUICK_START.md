# Backup-byGod Dashboard - Quick Start Guide

## 🚀 วิธีเริ่มต้นใช้งาน

### วิธีที่ 1: ใช้ Batch File (แนะนำ)
1. ดับเบิลคลิกที่ไฟล์ `START_DASHBOARD_SIMPLE.bat`
2. รอสักครู่ให้ระบบเริ่มต้น
3. เปิดเบราว์เซอร์ไปที่ `http://localhost:5000`

### วิธีที่ 2: ใช้ PowerShell
1. ดับเบิลคลิกที่ไฟล์ `START_DASHBOARD_SIMPLE.ps1`
2. หรือเปิด PowerShell แล้วรัน:
   ```powershell
   .\START_DASHBOARD_SIMPLE.ps1
   ```

### วิธีที่ 3: ใช้ Command Line
1. เปิด Command Prompt หรือ PowerShell
2. ไปที่โฟลเดอร์:
   ```cmd
   cd D:\FULL-AI-IDEA\AI-NEWEVOKE_VER1\backup-bygod
   ```
3. รันคำสั่ง:
   ```cmd
   python dashboard/app.py
   ```

## 📊 ฟีเจอร์ที่ใช้งานได้

### 1. System Overview
- แสดงสถานะระบบทั้งหมด
- ข้อมูลการใช้งานทรัพยากร
- สถิติการทำงาน

### 2. God Mode Statistics
- สถิติการใช้งาน God Mode
- ประวัติการทำงาน
- ข้อมูลการเรียนรู้

### 3. System Capabilities
- สถานะของแต่ละโมดูล
- การเชื่อมต่อระบบ
- การแจ้งเตือนปัญหา

### 4. Real-time Logs
- แสดง log แบบ real-time
- กรอง log ตามระดับความสำคัญ
- การแจ้งเตือนข้อผิดพลาด

## 🔧 การแก้ไขปัญหา

### ปัญหา: ไม่สามารถเข้าถึง localhost:5000 ได้
**วิธีแก้:**
1. ตรวจสอบว่า Python ถูกติดตั้งแล้ว
2. ตรวจสอบว่า port 5000 ไม่ถูกใช้งานโดยโปรแกรมอื่น
3. ลองรันคำสั่งใหม่

### ปัญหา: ระบบแสดง error
**วิธีแก้:**
1. ตรวจสอบ log ในหน้าจอ
2. ตรวจสอบว่าไฟล์ทั้งหมดอยู่ในตำแหน่งที่ถูกต้อง
3. ลองรีสตาร์ทระบบ

### ปัญหา: Chrome ถูกปิดอัตโนมัติ
**วิธีแก้:**
- ระบบได้ถูกปรับให้ไม่ปิด Chrome อัตโนมัติแล้ว
- Chrome จะทำงานจนกว่าคุณจะปิดเอง

## 📁 โครงสร้างไฟล์

```
backup-bygod/
├── dashboard/
│   ├── app.py              # ไฟล์หลักของ dashboard
│   ├── templates/
│   │   └── dashboard.html  # หน้าเว็บหลัก
│   └── static/
│       ├── dashboard.js    # JavaScript สำหรับ frontend
│       └── style.css       # CSS styles
├── core/                   # โมดูลหลักของระบบ
├── config/                 # ไฟล์การตั้งค่า
├── data/                   # ข้อมูลระบบ
├── alldata_godmode/        # ข้อมูล God Mode
└── START_DASHBOARD_SIMPLE.bat  # ไฟล์เริ่มต้นระบบ
```

## 🎯 การใช้งานขั้นสูง

### การเชื่อมต่อ AI Assistant
ระบบรองรับการเชื่อมต่อ AI Assistant ผ่าน:
- REST API
- WebSocket
- Command Line Interface

### การปรับแต่งการตั้งค่า
แก้ไขไฟล์ในโฟลเดอร์ `config/` เพื่อปรับแต่ง:
- การตั้งค่า AI
- การตั้งค่า Chrome
- การตั้งค่าระบบ

## 📞 การสนับสนุน

หากมีปัญหา กรุณาตรวจสอบ:
1. ไฟล์ log ในหน้าจอ
2. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
3. ตรวจสอบสิทธิ์การเข้าถึงไฟล์

---
**Backup-byGod Dashboard v1.1.2** - Powered by AI Technology 