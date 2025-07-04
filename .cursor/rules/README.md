# Cursor Rules for WAWAGOT.AI

## 📋 Overview

ไฟล์ Cursor rules เหล่านี้ถูกออกแบบมาเพื่อให้ AI assistant ทำงานได้อย่างมีประสิทธิภาพและสอดคล้องกับมาตรฐานของโปรเจกต์ WAWAGOT.AI

## 📁 File Structure

```
.cursor/rules/
├── README.md                    # ไฟล์นี้ - คำอธิบายการใช้งาน
├── wawagot-ai-rules.mdc        # กฎหลักสำหรับโปรเจกต์ (alwaysApply: true)
├── thai-language-rules.mdc     # กฎสำหรับการประมวลผลภาษาไทย
├── ai-ml-rules.mdc            # กฎสำหรับ AI/ML development
└── security-rules.mdc         # กฎสำหรับ security (alwaysApply: true)
```

## 🎯 Usage

### การใช้งานหลัก
- **wawagot-ai-rules.mdc**: ใช้กับไฟล์ทั้งหมดในโปรเจกต์
- **security-rules.mdc**: ใช้กับไฟล์ที่เกี่ยวข้องกับ security (alwaysApply: true)

### การใช้งานเฉพาะ
- **thai-language-rules.mdc**: ใช้กับไฟล์ที่เกี่ยวข้องกับการประมวลผลภาษาไทย
- **ai-ml-rules.mdc**: ใช้กับไฟล์ที่เกี่ยวข้องกับ AI/ML development

## 🔧 Configuration

### File Format
ไฟล์ rules ใช้รูปแบบ `.mdc` (Markdown) ที่มี frontmatter:

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

## 📋 Rules Categories

### 1. General Rules (wawagot-ai-rules.mdc)
- การสื่อสารภาษาไทย
- มาตรฐานการเขียนโค้ด
- การจัดการโปรเจกต์
- การทำงานกับ external services

### 2. Thai Language Rules (thai-language-rules.mdc)
- การประมวลผลภาษาไทย
- UI/UX สำหรับผู้ใช้ไทย
- การจัดการข้อมูลภาษาไทย
- การทดสอบภาษาไทย

### 3. AI/ML Rules (ai-ml-rules.mdc)
- การพัฒนาโมเดล ML
- การใช้ GPU acceleration
- การจัดการข้อมูล
- การ deploy โมเดล

### 4. Security Rules (security-rules.mdc)
- การจัดการ credentials
- การ validate input
- การป้องกันการโจมตี
- การ monitor security

## 🚀 Best Practices

### การเขียน Rules ใหม่
1. ใช้รูปแบบ `.mdc` ที่มี frontmatter
2. ระบุ globs patterns ที่เหมาะสม
3. ใช้ alwaysApply: true สำหรับกฎสำคัญ
4. เขียนคำอธิบายที่ชัดเจน

### การจัดการ Rules
1. แยกกฎตามหมวดหมู่
2. ใช้ชื่อไฟล์ที่สื่อความหมาย
3. อัปเดตกฎเป็นประจำ
4. ทดสอบกฎกับไฟล์จริง

## 🔍 Troubleshooting

### ปัญหาที่พบบ่อย
1. **Rules ไม่ทำงาน**: ตรวจสอบ globs patterns
2. **Rules ขัดแย้งกัน**: ตรวจสอบ alwaysApply settings
3. **Performance issues**: ลดจำนวน rules หรือปรับ globs

### การ Debug
1. ตรวจสอบ Cursor logs
2. ทดสอบ rules กับไฟล์ตัวอย่าง
3. ตรวจสอบ syntax ของ frontmatter

## 📚 References

- [Cursor Documentation](https://cursor.sh/docs)
- [Cursor Rules Format](https://cursor.sh/docs/rules)
- [Glob Patterns](https://en.wikipedia.org/wiki/Glob_(programming))

## 🔄 Maintenance

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

**หมายเหตุ**: Rules เหล่านี้ถูกออกแบบมาเพื่อให้ AI assistant ทำงานได้อย่างมีประสิทธิภาพและสอดคล้องกับมาตรฐานของโปรเจกต์ WAWAGOT.AI 