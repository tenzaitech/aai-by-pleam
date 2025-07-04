# ไฟล์ Cursor Rules ทั้งหมด (ใช้งานได้จริง)

## 📁 โครงสร้างไฟล์

```
.cursor/rules/
├── README.md                    # คำอธิบายการใช้งาน
├── wawagot-ai-rules.mdc        # กฎหลักสำหรับโปรเจกต์ (alwaysApply: true)
├── thai-language-rules.mdc     # กฎสำหรับการประมวลผลภาษาไทย
├── ai-ml-rules.mdc            # กฎสำหรับ AI/ML development
└── security-rules.mdc         # กฎสำหรับ security (alwaysApply: true)
```

## 📋 รายละเอียดไฟล์

### 1. wawagot-ai-rules.mdc
**วัตถุประสงค์**: กฎหลักสำหรับโปรเจกต์ WAWAGOT.AI
**การใช้งาน**: ใช้กับไฟล์ทั้งหมดในโปรเจกต์
**alwaysApply**: true

**เนื้อหาหลัก**:
- การสื่อสารภาษาไทย
- มาตรฐานการเขียนโค้ด
- การจัดการโปรเจกต์
- การทำงานกับ external services
- การบูรณาการความทรงจำ
- แนวทางการแก้ปัญหา

### 2. thai-language-rules.mdc
**วัตถุประสงค์**: กฎสำหรับการประมวลผลภาษาไทย
**การใช้งาน**: ใช้กับไฟล์ที่เกี่ยวข้องกับภาษาไทย
**alwaysApply**: false

**เนื้อหาหลัก**:
- การประมวลผลข้อความภาษาไทย
- UI/UX สำหรับผู้ใช้ไทย
- การจัดการข้อมูลภาษาไทย
- การทดสอบภาษาไทย
- การใช้ UTF-8 encoding

### 3. ai-ml-rules.mdc
**วัตถุประสงค์**: กฎสำหรับ AI/ML development
**การใช้งาน**: ใช้กับไฟล์ที่เกี่ยวข้องกับ AI/ML
**alwaysApply**: false

**เนื้อหาหลัก**:
- การพัฒนาโมเดล ML
- การใช้ GPU acceleration
- การจัดการข้อมูล
- การ deploy โมเดล
- การ monitor performance

### 4. security-rules.mdc
**วัตถุประสงค์**: กฎสำหรับ security
**การใช้งาน**: ใช้กับไฟล์ที่เกี่ยวข้องกับ security
**alwaysApply**: true

**เนื้อหาหลัก**:
- การจัดการ credentials
- การ validate input
- การป้องกันการโจมตี
- การ monitor security
- การจัดการ secrets

## 🔧 การใช้งาน

### การคัดลอกไฟล์
```bash
# คัดลอกไฟล์ rules ไปยัง .cursor/rules/
cp pleamthinking/cursorsettingv1/*.mdc .cursor/rules/
```

### การตรวจสอบไฟล์
```bash
# ตรวจสอบไฟล์ rules
ls -la .cursor/rules/

# ตรวจสอบ syntax
cat .cursor/rules/wawagot-ai-rules.mdc
```

### การอัปเดตไฟล์
```bash
# อัปเดตไฟล์ rules
cp pleamthinking/cursorsettingv1/updated_rules.mdc .cursor/rules/

# รีสตาร์ท Cursor
```

## 📝 รูปแบบไฟล์

### Frontmatter
```yaml
---
description: "คำอธิบายกฎ"
globs: ["**/*.py", "**/*.js"]  # ไฟล์ที่ใช้กฎนี้
alwaysApply: true/false        # ใช้เสมอหรือไม่
---
```

### Globs Patterns
- `**/*.py`: ไฟล์ Python ทั้งหมด
- `**/*.js`: ไฟล์ JavaScript ทั้งหมด
- `**/*.ts`: ไฟล์ TypeScript ทั้งหมด
- `**/*.html`: ไฟล์ HTML ทั้งหมด
- `**/*.md`: ไฟล์ Markdown ทั้งหมด

## 🎯 ประโยชน์

### 1. ความสอดคล้อง
- AI assistant ทำงานตามมาตรฐานเดียวกัน
- ลดความขัดแย้งในการเขียนโค้ด
- รักษาคุณภาพของโค้ด

### 2. ประสิทธิภาพ
- ลดเวลาในการกำหนดกฎซ้ำ
- ทำงานได้เร็วขึ้นด้วยกฎที่เหมาะสม
- ลดข้อผิดพลาด

### 3. ความปลอดภัย
- มีกฎ security ที่ใช้เสมอ
- ป้องกันการรั่วไหลของข้อมูล
- รักษาความปลอดภัยของระบบ

### 4. การบำรุงรักษา
- แยกกฎตามหมวดหมู่
- ง่ายต่อการอัปเดต
- มีเอกสารครบถ้วน

## 🔍 การแก้ปัญหา

### ปัญหาที่พบบ่อย

#### 1. Rules ไม่ทำงาน
```bash
# ตรวจสอบ globs patterns
cat .cursor/rules/wawagot-ai-rules.mdc | head -10

# ตรวจสอบ syntax
python -c "import yaml; yaml.safe_load(open('.cursor/rules/wawagot-ai-rules.mdc'))"
```

#### 2. Rules ขัดแย้งกัน
```bash
# ตรวจสอบ alwaysApply settings
grep -r "alwaysApply" .cursor/rules/

# ตรวจสอบ globs ที่ซ้ำกัน
grep -r "globs:" .cursor/rules/
```

#### 3. Performance issues
```bash
# ลดจำนวน rules
ls -la .cursor/rules/ | wc -l

# ปรับ globs patterns
cat .cursor/rules/*.mdc | grep "globs:"
```

## 📚 การอ้างอิง

### เอกสารที่เกี่ยวข้อง
- `pleamthinking/cursorsettingv1/01_cursor_rules_main.md` - กฎหลัก
- `pleamthinking/cursorsettingv1/03_cursor_setup_guide.md` - คู่มือการตั้งค่า

### ลิงก์ที่เป็นประโยชน์
- [Cursor Documentation](https://cursor.sh/docs)
- [Cursor Rules Format](https://cursor.sh/docs/rules)
- [Glob Patterns](https://en.wikipedia.org/wiki/Glob_(programming))

## 🔄 การบำรุงรักษา

### การอัปเดต Rules
1. ตรวจสอบ rules เป็นประจำ
2. อัปเดตตาม best practices ใหม่
3. เพิ่ม rules ตามความต้องการ
4. ลบ rules ที่ไม่ใช้แล้ว

### การ Backup
1. Backup rules ก่อนแก้ไข
2. ใช้ version control
3. ทดสอบ rules หลังแก้ไข
4. Document การเปลี่ยนแปลง

---

**หมายเหตุ**: ไฟล์ rules เหล่านี้ถูกออกแบบมาเพื่อให้ AI assistant ทำงานได้อย่างมีประสิทธิภาพและสอดคล้องกับมาตรฐานของโปรเจกต์ WAWAGOT.AI 