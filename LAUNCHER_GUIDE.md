# WAWAGOT V.2 Launcher Guide

## 🚀 วิธีรันระบบ WAWAGOT V.2

### **ปัญหาที่พบ: PowerShell ไม่รองรับ `&&`**

PowerShell ไม่รองรับ `&&` operator เหมือน Bash/Linux เนื่องจาก:
- **Bash**: `command1 && command2` (AND operator)
- **PowerShell**: ใช้ `;` หรือ `-and` แทน

---

## 📋 วิธีรันระบบ (เลือกวิธีใดวิธีหนึ่ง)

### **1. PowerShell Script (แนะนำ)**
```powershell
# รัน PowerShell script
.\run_wawagot.ps1
```

### **2. Batch Script (Windows CMD)**
```cmd
# รัน Batch script
run_wawagot.bat
```

### **3. Cross-Platform Python Launcher**
```bash
# รัน Python launcher (ทำงานได้ทุก OS)
python launch_cross_platform.py
```

### **4. Manual Steps (PowerShell)**
```powershell
# วิธีที่ 1: ใช้ ; แทน &&
cd C:\AI_ULTRA_PROJECT\wawagot.ai; .\.venv-gpu\Scripts\Activate.ps1; python launch_v2.py

# วิธีที่ 2: แยกคำสั่ง
cd C:\AI_ULTRA_PROJECT\wawagot.ai
.\.venv-gpu\Scripts\Activate.ps1
python launch_v2.py
```

### **5. Manual Steps (Windows CMD)**
```cmd
# ใช้ call แทน &&
cd C:\AI_ULTRA_PROJECT\wawagot.ai && call .venv-gpu\Scripts\activate.bat && python launch_v2.py
```

---

## 🔧 PowerShell Operators ที่ถูกต้อง

### **Sequential Execution**
```powershell
# ❌ ไม่ทำงาน
command1 && command2

# ✅ วิธีที่ถูกต้อง
command1; command2                    # Run sequentially
command1 -and command2                # Logical AND
command1 | command2                   # Pipeline
if (command1) { command2 }            # Conditional execution
```

### **Error Handling**
```powershell
# ✅ ตรวจสอบ exit code
if ($LASTEXITCODE -eq 0) { command2 }

# ✅ ใช้ try-catch
try { command1 } catch { command2 }
```

---

## 📁 ไฟล์ที่สร้างขึ้น

### **1. run_wawagot.ps1**
- PowerShell script สำหรับ Windows
- ตรวจสอบ dependencies อัตโนมัติ
- Activate virtual environment
- รันระบบ

### **2. run_wawagot.bat**
- Batch script สำหรับ Windows CMD
- ทำงานเหมือน PowerShell script
- ใช้ Windows CMD syntax

### **3. launch_cross_platform.py**
- Python launcher ทำงานได้ทุก OS
- ตรวจสอบ OS อัตโนมัติ
- Setup environment อัตโนมัติ
- Error handling ครบถ้วน

### **4. launch_v2.py (แก้ไขแล้ว)**
- แก้ไข subprocess.run ให้ใช้ shell=True บน Windows
- เปลี่ยน opencv-python เป็น cv2
- แก้ไข Unicode encoding issues

---

## 🎯 วิธีที่ดีที่สุด

### **สำหรับ Windows:**
1. **ใช้ `run_wawagot.ps1`** (PowerShell)
2. **ใช้ `run_wawagot.bat`** (CMD)
3. **ใช้ `launch_cross_platform.py`** (Python)

### **สำหรับ Linux/macOS:**
1. **ใช้ `launch_cross_platform.py`** (Python)
2. **ใช้ `&&` operator** (Bash)

---

## 🔍 การแก้ไขปัญหา

### **ปัญหา: `&&` ไม่ทำงาน**
```powershell
# ❌ Error
cd C:\path && activate && python script.py

# ✅ แก้ไข
cd C:\path; activate; python script.py
```

### **ปัญหา: Virtual Environment ไม่ activate**
```powershell
# ✅ วิธีที่ถูกต้อง
.\.venv-gpu\Scripts\Activate.ps1    # PowerShell
call .venv-gpu\Scripts\activate.bat # CMD
source .venv-gpu/bin/activate       # Bash
```

### **ปัญหา: Dependencies ไม่ครบ**
```powershell
# ✅ ติดตั้งใหม่
python -m pip install -r requirements_v2_finetuned.txt
```

---

## 📊 สรุป

| Method | Windows | Linux/macOS | Auto Setup | Error Handling |
|--------|---------|-------------|------------|----------------|
| `run_wawagot.ps1` | ✅ | ❌ | ✅ | ✅ |
| `run_wawagot.bat` | ✅ | ❌ | ✅ | ✅ |
| `launch_cross_platform.py` | ✅ | ✅ | ✅ | ✅ |
| Manual | ✅ | ✅ | ❌ | ❌ |

**แนะนำ: ใช้ `launch_cross_platform.py` สำหรับความยืดหยุ่นสูงสุด** 