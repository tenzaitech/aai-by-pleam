# 📚 WAWAGOT.AI Documentation

โฟลเดอร์นี้ประกอบด้วยเอกสาร HTML สำหรับ Cursor Docs feature ที่จะช่วยให้ AI assistant เข้าใจโปรเจกต์ได้ดีขึ้น

## 📁 ไฟล์ในโฟลเดอร์

### 🏠 [index.html](./index.html)
**Documentation หลัก** - ภาพรวมระบบ สถาปัตยกรรม การตั้งค่า และการใช้งาน
- ภาพรวมระบบ WAWAGOT.AI
- สถาปัตยกรรมและเทคโนโลยีที่ใช้
- การตั้งค่าและติดตั้ง
- API และ Endpoints
- AI/ML Components
- ฐานข้อมูลและ Storage
- ความปลอดภัย
- การแก้ปัญหา

### 🔌 [api-reference.html](./api-reference.html)
**API Reference** - เอกสาร API ครบถ้วน
- MCP Server Endpoints
- Dashboard API
- AI Services API
- Database API
- Authentication
- ตัวอย่างการใช้งาน

### 🏗️ [architecture.html](./architecture.html)
**System Architecture** - สถาปัตยกรรมระบบโดยละเอียด
- ภาพรวมสถาปัตยกรรม
- Core Components
- Data Flow
- Security Architecture
- Scalability
- Deployment

### 🚀 [quick-start.html](./quick-start.html)
**Quick Start Guide** - คู่มือการเริ่มต้นใช้งานอย่างรวดเร็ว
- ข้อกำหนดระบบ
- การติดตั้ง step-by-step
- การตั้งค่า Cursor IDE
- การทดสอบระบบ
- การแก้ปัญหา

## 🎯 การใช้งาน

### สำหรับ Cursor IDE
1. เปิด Cursor IDE ในโปรเจกต์
2. ไปที่ Settings > Docs
3. เพิ่มโฟลเดอร์ `pleamthinking/cursorsettingv1/docs/` เป็น custom docs
4. Cursor จะ crawl และ index เอกสารเหล่านี้

### สำหรับการพัฒนา
- ใช้เป็น reference สำหรับการพัฒนา
- อัปเดตเอกสารเมื่อมีการเปลี่ยนแปลงระบบ
- เพิ่มเอกสารใหม่ตามความต้องการ

## 🔧 การบำรุงรักษา

### การอัปเดตเอกสาร
1. แก้ไขไฟล์ HTML ที่เกี่ยวข้อง
2. ตรวจสอบความถูกต้องของข้อมูล
3. ทดสอบการแสดงผลในเบราว์เซอร์
4. Commit และ push การเปลี่ยนแปลง

### การเพิ่มเอกสารใหม่
1. สร้างไฟล์ HTML ใหม่
2. ใช้ template จากไฟล์ที่มีอยู่
3. เพิ่มลิงก์ในไฟล์ README นี้
4. อัปเดต navigation ในไฟล์หลัก

## 📋 Template สำหรับไฟล์ใหม่

```html
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WAWAGOT.AI - [ชื่อเอกสาร]</title>
    <style>
        /* ใช้ CSS จากไฟล์อื่น */
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>[ชื่อเอกสาร]</h1>
            <p>WAWAGOT.AI - [คำอธิบาย]</p>
        </div>
        
        <div class="content">
            <!-- เนื้อหาเอกสาร -->
        </div>
        
        <div class="footer">
            <p><strong>WAWAGOT.AI [ชื่อเอกสาร]</strong> - สร้างเมื่อ [วันที่]</p>
        </div>
    </div>
</body>
</html>
```

## 🔗 ลิงก์ที่เกี่ยวข้อง

- [Cursor Rules](../01_cursor_rules_main.md)
- [MCP Server Config](../02_mcp_server_config.json)
- [Setup Guide](../03_cursor_setup_guide.md)
- [Environment Template](../04_environment_variables_template.env)
- [Troubleshooting Guide](../07_troubleshooting_guide.md)

## 📞 การขอความช่วยเหลือ

หากมีปัญหาเกี่ยวกับเอกสาร:
1. ตรวจสอบ [Troubleshooting Guide](../07_troubleshooting_guide.md)
2. ดู logs ในโฟลเดอร์ `logs/`
3. รัน `system_health_checker.py`
4. สร้าง issue ใน GitHub repository

---

**สร้างเมื่อ:** 2024-12-19  
**อัปเดตล่าสุด:** 2024-12-19  
**เวอร์ชัน:** 1.0.0 