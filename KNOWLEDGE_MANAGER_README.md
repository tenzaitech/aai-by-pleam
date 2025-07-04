# 🧠 Knowledge Manager

ระบบจัดการฐานความรู้สำหรับ AI-Powered Learning System

## 📋 ภาพรวม

Knowledge Manager เป็นระบบที่ช่วยให้คุณสามารถ:
- เพิ่มความรู้จาก URL หรือข้อความ
- จัดหมวดหมู่ความรู้
- ค้นหาความรู้
- จัดการฐานความรู้ผ่าน Web Dashboard

## 🚀 ฟีเจอร์หลัก

### ✅ เพิ่มความรู้
- **จาก URL**: เพิ่มความรู้จากเว็บไซต์โดยอัตโนมัติ
- **จากข้อความ**: เพิ่มความรู้โดยตรงจากข้อความ

### ✅ จัดหมวดหมู่
- n8n Workflow Automation
- Zapier Automation  
- Make (Integromat) Automation
- General Automation Knowledge
- Chrome Automation
- AI Integration

### ✅ ค้นหาและจัดการ
- ค้นหาความรู้ด้วยคำค้นหา
- กรองตามหมวดหมู่
- ดูรายละเอียดความรู้
- แก้ไขและลบความรู้

### ✅ สถิติและรายงาน
- จำนวนความรู้ทั้งหมด
- สถิติตามหมวดหมู่
- วันที่สร้างและอัปเดต

## 🛠️ การติดตั้ง

### 1. ตรวจสอบ Dependencies
```bash
pip install requests
```

### 2. ตรวจสอบไฟล์ที่จำเป็น
- `core/knowledge_manager.py` - ระบบหลัก
- `dashboard/app.py` - Web API
- `dashboard/templates/dashboard.html` - Web UI

## 📁 โครงสร้างไฟล์

```
Learning-doc-datafiles/
├── knowledge-base.json      # ฐานความรู้หลัก
├── categories.json          # ข้อมูลหมวดหมู่
└── [future folders]         # ไฟล์เพิ่มเติมในอนาคต
```

## 🎮 การใช้งาน

### 1. ผ่าน Web Dashboard
```bash
python dashboard/app.py
```
เปิดเบราว์เซอร์ไปที่: `http://localhost:5000`

### 2. ผ่าน Python Code
```python
from core.knowledge_manager import knowledge_manager

# เพิ่มความรู้จากข้อความ
result = knowledge_manager.add_knowledge_from_text(
    title="ชื่อเรื่อง",
    content="เนื้อหา",
    category="n8n",
    description="คำอธิบาย"
)

# เพิ่มความรู้จาก URL
result = knowledge_manager.add_knowledge_from_url(
    url="https://example.com",
    category="n8n",
    title="ชื่อเรื่อง (ไม่บังคับ)",
    description="คำอธิบาย (ไม่บังคับ)"
)

# ค้นหาความรู้
results = knowledge_manager.search_knowledge("คำค้นหา")

# ดูสถิติ
stats = knowledge_manager.get_statistics()
```

### 3. ทดสอบระบบ
```bash
python test_knowledge_manager.py
```

## 🔧 API Endpoints

### GET `/api/knowledge/statistics`
ดูสถิติฐานความรู้

### GET `/api/knowledge/search?q=<query>&category=<category>&limit=<limit>`
ค้นหาความรู้

### GET `/api/knowledge/categories`
ดูหมวดหมู่ทั้งหมด

### GET `/api/knowledge/category/<category>`
ดูความรู้ตามหมวดหมู่

### POST `/api/knowledge/add`
เพิ่มความรู้ใหม่
```json
{
    "type": "url|text",
    "url": "https://example.com",
    "title": "ชื่อเรื่อง",
    "content": "เนื้อหา",
    "category": "n8n",
    "description": "คำอธิบาย"
}
```

### PUT `/api/knowledge/update/<knowledge_id>`
อัปเดตความรู้

### DELETE `/api/knowledge/delete/<knowledge_id>`
ลบความรู้

### GET `/api/knowledge/<knowledge_id>`
ดูรายละเอียดความรู้

## 🎯 ตัวอย่างการใช้งาน

### ตัวอย่าง 1: เพิ่มความรู้ n8n
```python
# เพิ่มความรู้เกี่ยวกับ n8n webhook
knowledge_manager.add_knowledge_from_text(
    title="n8n Webhook Setup",
    content="วิธีการตั้งค่า webhook ใน n8n: 1. สร้าง workflow ใหม่ 2. เพิ่ม Webhook node 3. ตั้งค่า endpoint 4. ทดสอบการเชื่อมต่อ",
    category="n8n",
    description="ขั้นตอนการตั้งค่า webhook ใน n8n"
)
```

### ตัวอย่าง 2: เพิ่มความรู้จาก URL
```python
# เพิ่มความรู้จาก n8n documentation
knowledge_manager.add_knowledge_from_url(
    url="https://docs.n8n.io/nodes/n8n-nodes-base.webhook/",
    category="n8n",
    title="n8n Webhook Documentation"
)
```

### ตัวอย่าง 3: ค้นหาความรู้
```python
# ค้นหาความรู้เกี่ยวกับ webhook
results = knowledge_manager.search_knowledge("webhook", category="n8n")
for result in results:
    print(f"Title: {result['title']}")
    print(f"Description: {result['description']}")
    print(f"Relevance Score: {result['relevance_score']}")
```

## 📊 สถิติที่ได้

```json
{
    "total_items": 4,
    "categories": {
        "n8n": 2,
        "zapier": 1,
        "chrome": 1
    },
    "last_updated": "2025-07-02T08:46:36.541660",
    "created": "2025-07-02T08:45:24.801268"
}
```

## 🔍 การค้นหา

ระบบค้นหาจะค้นหาใน:
- ชื่อเรื่อง (relevance score: 10)
- คำอธิบาย (relevance score: 5)
- เนื้อหา (relevance score: 1)
- แท็ก (relevance score: 1)

ผลลัพธ์จะเรียงตาม relevance score จากมากไปน้อย

## 🎨 Web Dashboard

### ฟีเจอร์ UI:
- **Tab เพิ่มความรู้**: เพิ่มจาก URL หรือข้อความ
- **Tab ค้นหา**: ค้นหาและจัดการความรู้
- **Tab สถิติ**: ดูสถิติและรายงาน

### การใช้งาน:
1. เปิด Dashboard
2. เลือก Tab ที่ต้องการ
3. กรอกข้อมูลและกดปุ่มดำเนินการ
4. ดูผลลัพธ์และจัดการความรู้

## 🚀 การพัฒนาต่อ

### ฟีเจอร์ที่วางแผน:
- [ ] การเรียนรู้จากไฟล์ PDF
- [ ] การเรียนรู้จาก YouTube videos
- [ ] การเชื่อมต่อกับ AI models
- [ ] การสร้าง knowledge graphs
- [ ] การ export/import ข้อมูล
- [ ] การ backup/restore ฐานความรู้

### การปรับปรุง:
- [ ] เพิ่มความแม่นยำในการค้นหา
- [ ] เพิ่มการวิเคราะห์เนื้อหา
- [ ] เพิ่มการแนะนำความรู้ที่เกี่ยวข้อง
- [ ] เพิ่มการจัดการสิทธิ์ผู้ใช้

## 🐛 การแก้ไขปัญหา

### ปัญหาที่พบบ่อย:

1. **Knowledge Manager not available**
   - ตรวจสอบว่า `core/knowledge_manager.py` มีอยู่
   - ตรวจสอบ dependencies

2. **Error fetching URL content**
   - ตรวจสอบ URL ว่าถูกต้อง
   - ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต

3. **Permission denied**
   - ตรวจสอบสิทธิ์การเขียนไฟล์ใน `Learning-doc-datafiles/`

## 📞 การสนับสนุน

หากมีปัญหาหรือต้องการความช่วยเหลือ:
1. ตรวจสอบ log files
2. รัน `python test_knowledge_manager.py`
3. ตรวจสอบ console errors

---

**🎉 Knowledge Manager พร้อมใช้งานแล้ว!**

เริ่มต้นการเรียนรู้และจัดการความรู้ของคุณได้เลย! 