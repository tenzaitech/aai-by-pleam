# WAWAGOT.AI Web Dashboard (bolt.new integration)

## แนวคิด
- สร้าง Web UI/UX สำหรับดู log, ค้นหา, export, จัดการ session/tag/backup
- เตรียม template/export endpoint สำหรับนำเข้า bolt.new
- UI/UX ใช้งานง่าย ปลอดภัย (admin-only)

## โครงสร้างไฟล์ export
- รองรับ json/csv/txt
- Export ได้ทั้ง session, conversations, backup, tag
- ตัวอย่าง endpoint: `/export/session/{session_id}`

## การใช้งานร่วมกับ bolt.new
- export ไฟล์จาก API หรือ CLI
- import เข้า bolt.new ได้ทันที
- สามารถ custom template/endpoint เพิ่มเติมได้

## หมายเหตุ
- ระบบ WebDashboard จะพัฒนาเมื่อระบบ backend ทุกส่วนสมบูรณ์และผ่านการทดสอบแล้ว 