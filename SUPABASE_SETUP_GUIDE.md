# 🗄️ คู่มือการตั้งค่า Supabase สำหรับระบบ WAWAGOT.AI

## 📋 สรุป

ระบบ WAWAGOT.AI ต้องการตาราง 10 ตารางใน Supabase เพื่อเก็บข้อมูลต่างๆ ของระบบ

## 🚀 ขั้นตอนการสร้างตาราง

### 1. เข้าสู่ Supabase Dashboard

1. ไปที่ [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. เข้าสู่ระบบด้วยบัญชีของคุณ
3. เลือกโปรเจค **TENZAITECH-DATABASE**

### 2. เข้าสู่ SQL Editor

1. คลิกที่ **SQL Editor** ในเมนูด้านซ้าย
2. คลิก **New Query** เพื่อสร้าง query ใหม่

### 3. รัน SQL Script

1. คัดลอกเนื้อหาจากไฟล์ `wawagot_tables.sql`
2. วางใน SQL Editor
3. คลิก **Run** เพื่อรัน script

## 📊 ตารางที่สร้าง

### 1. `conversation_logs` - บันทึกบทสนทนา
- เก็บข้อมูลการสนทนาระหว่างผู้ใช้กับ AI
- ข้อมูล: session_id, user_id, user_message, ai_response, timestamp, model_used, tokens_used, response_time_ms, status, metadata

### 2. `user_profiles` - ข้อมูลผู้ใช้
- เก็บข้อมูลโปรไฟล์ของผู้ใช้
- ข้อมูล: user_id, email, username, full_name, avatar_url, preferences, created_at, updated_at, last_login, is_active

### 3. `system_logs` - บันทึกระบบ
- เก็บ log ต่างๆ ของระบบ
- ข้อมูล: level, component, message, timestamp, user_id, session_id, metadata, stack_trace

### 4. `knowledge_base` - ฐานความรู้
- เก็บข้อมูลความรู้และเอกสารต่างๆ
- ข้อมูล: title, content, category, tags, source, created_at, updated_at, created_by, is_active, metadata

### 5. `backup_logs` - บันทึกการสำรองข้อมูล
- เก็บข้อมูลการสำรองข้อมูล
- ข้อมูล: backup_type, status, file_path, file_size, start_time, end_time, duration_seconds, records_backed_up, error_message, metadata

### 6. `health_checks` - การตรวจสอบระบบ
- เก็บข้อมูลการตรวจสอบสุขภาพระบบ
- ข้อมูล: check_type, status, response_time_ms, timestamp, details, error_message

### 7. `alerts` - การแจ้งเตือน
- เก็บข้อมูลการแจ้งเตือนต่างๆ
- ข้อมูล: alert_type, severity, title, message, timestamp, is_resolved, resolved_at, resolved_by, metadata

### 8. `environment_data` - ข้อมูลสภาพแวดล้อม
- เก็บข้อมูลสภาพแวดล้อมของระบบ
- ข้อมูล: component, metric_name, metric_value, unit, timestamp, metadata

### 9. `file_management` - การจัดการไฟล์
- เก็บข้อมูลการจัดการไฟล์
- ข้อมูล: file_name, file_path, file_size, file_type, mime_type, uploaded_by, uploaded_at, is_processed, processing_status, metadata

### 10. `system_config` - การตั้งค่าระบบ
- เก็บการตั้งค่าต่างๆ ของระบบ
- ข้อมูล: config_key, config_value, config_type, description, is_active, created_at, updated_at, updated_by

## 🔧 ฟีเจอร์ที่สร้าง

### Indexes
- สร้าง indexes สำหรับการค้นหาที่รวดเร็ว
- ครอบคลุมทุกตารางหลัก

### Row Level Security (RLS)
- เปิดใช้งาน RLS สำหรับความปลอดภัย
- สร้าง policies สำหรับการเข้าถึงข้อมูล

### Triggers
- สร้าง triggers สำหรับอัพเดท updated_at อัตโนมัติ
- ครอบคลุมตารางที่มีฟิลด์ updated_at

### Views
- `system_summary` - สรุปข้อมูลระบบ
- `recent_activity` - กิจกรรมล่าสุด

### Functions
- `update_updated_at_column()` - อัพเดท updated_at

## 📝 ข้อมูลตัวอย่าง

### System Config
- system_name: WAWAGOT.AI
- version: 2.0.0
- max_conversation_length: 1000
- ai_model: gpt-4
- backup_retention_days: 90
- log_level: INFO
- max_file_size_mb: 100
- session_timeout_minutes: 30
- enable_notifications: true
- auto_backup_enabled: true

### Knowledge Base
- การใช้งานระบบ WAWAGOT.AI
- การตั้งค่า Environment Variables
- การเชื่อมต่อ Supabase
- การใช้งาน Google API
- การจัดการไฟล์และ Backup

### Health Checks
- database_connection
- api_connection
- file_system
- memory_usage
- cpu_usage

## ✅ การตรวจสอบ

หลังจากสร้างตารางแล้ว ให้รันสคริปต์ตรวจสอบ:

```bash
python create_tables_via_api.py
```

หรือ

```bash
python check_supabase_tables.py
```

## 🔍 การแก้ไขปัญหา

### ปัญหา: ตารางไม่ถูกสร้าง
**สาเหตุ:** SQL script ไม่รันสำเร็จ
**วิธีแก้:**
1. ตรวจสอบ error ใน SQL Editor
2. รัน SQL ทีละส่วน
3. ตรวจสอบสิทธิ์การเข้าถึง

### ปัญหา: ไม่สามารถเชื่อมต่อได้
**สาเหตุ:** Environment variables ไม่ถูกต้อง
**วิธีแก้:**
1. ตรวจสอบ SUPABASE_URL และ SUPABASE_KEY
2. ตรวจสอบไฟล์ .env
3. รีสตาร์ท terminal

### ปัญหา: RLS ปิดกั้นการเข้าถึง
**สาเหตุ:** Row Level Security ทำงาน
**วิธีแก้:**
1. ปรับแต่ง policies ใน Supabase Dashboard
2. ตรวจสอบ auth.uid() ใน policies
3. ปิด RLS ชั่วคราวสำหรับการทดสอบ

## 📞 การสนับสนุน

หากมีปัญหาในการสร้างตาราง:

1. ตรวจสอบ error messages ใน Supabase Dashboard
2. ดู logs ใน SQL Editor
3. ตรวจสอบ Network tab ใน Developer Tools
4. ติดต่อทีมพัฒนา

## 🎯 ขั้นตอนถัดไป

หลังจากสร้างตารางสำเร็จ:

1. ทดสอบการเชื่อมต่อด้วย Python script
2. เพิ่มข้อมูลตัวอย่าง
3. ตั้งค่า RLS policies ตามความต้องการ
4. ทดสอบการทำงานของระบบ
5. ตั้งค่า monitoring และ alerts

---

**หมายเหตุ:** ไฟล์ `wawagot_tables.sql` มี SQL script ที่สมบูรณ์สำหรับสร้างตารางทั้งหมด พร้อมข้อมูลตัวอย่างและฟีเจอร์เพิ่มเติม 