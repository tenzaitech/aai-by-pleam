# 🚀 Chrome Automation 100% - Installation Guide

## 📋 **ข้อกำหนดระบบ**

### **ระบบปฏิบัติการที่รองรับ:**
- Windows 10/11
- macOS 10.15+
- Ubuntu 18.04+

### **ข้อกำหนดขั้นต่ำ:**
- RAM: 4GB
- Storage: 2GB
- Python 3.8+
- Node.js 16+
- Chrome Browser

## 🔧 **การติดตั้ง**

### **1. ติดตั้ง Python Dependencies**
```bash
# ติดตั้ง Python packages
pip install -r requirements.txt

# หรือติดตั้งทีละตัว
pip install opencv-python pytesseract Pillow pyautogui selenium
pip install tensorflow torch transformers openai
pip install flask flask-cors websockets aiohttp
```

### **2. ติดตั้ง Node.js Dependencies**
```bash
# ติดตั้ง Node.js packages
npm install

# หรือติดตั้งทีละตัว
npm install puppeteer selenium-webdriver chrome-remote-interface
npm install tesseract.js opencv4nodejs robotjs sharp
npm install express cors dotenv
```

### **3. ติดตั้ง Tesseract OCR**
```bash
# Windows (ใช้ Chocolatey)
choco install tesseract

# macOS (ใช้ Homebrew)
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-tha  # สำหรับภาษาไทย
```

### **4. ติดตั้ง Chrome WebDriver**
```bash
# สำหรับ Selenium
pip install webdriver-manager

# หรือดาวน์โหลด ChromeDriver จาก:
# https://chromedriver.chromium.org/
```

## 🔑 **การตั้งค่า API Keys**

### **1. สร้างไฟล์ .env**
```bash
# สร้างไฟล์ .env ในโฟลเดอร์หลัก
touch .env
```

### **2. เพิ่ม API Keys**
```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Chrome Path (ถ้าจำเป็น)
CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe

# Tesseract Path (ถ้าจำเป็น)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## 🧪 **การทดสอบ**

### **1. ทดสอบการติดตั้ง**
```bash
# ทดสอบ Python modules
python -c "import cv2, pytesseract, pyautogui; print('✅ Python modules OK')"

# ทดสอบ Node.js modules
node -e "console.log('✅ Node.js OK')"
```

### **2. ทดสอบ Master Controller**
```bash
# รัน Master Controller
python master-controller.py
```

### **3. ทดสอบแต่ละ Controller**
```bash
# ทดสอบ Puppeteer
node -e "const PuppeteerController = require('./core/puppeteer-controller.js'); console.log('✅ Puppeteer OK')"

# ทดสอบ Selenium
python -c "from core.selenium_controller import SeleniumController; print('✅ Selenium OK')"

# ทดสอบ OCR
python -c "from core.ocr_processor import OCRProcessor; print('✅ OCR OK')"
```

## 🚨 **การแก้ไขปัญหา**

### **ปัญหา: Chrome ไม่เปิด**
```bash
# ตรวจสอบ Chrome path
# Windows: C:\Program Files\Google\Chrome\Application\chrome.exe
# macOS: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
# Linux: /usr/bin/google-chrome
```

### **ปัญหา: Tesseract ไม่พบ**
```bash
# ตรวจสอบ Tesseract installation
tesseract --version

# ตั้งค่า path ใน Python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### **ปัญหา: OpenAI API Error**
```bash
# ตรวจสอบ API key
echo $OPENAI_API_KEY

# ทดสอบ API
python -c "import openai; openai.api_key='your_key'; print('✅ OpenAI OK')"
```

### **ปัญหา: Permission Denied**
```bash
# ให้สิทธิ์การเข้าถึง
chmod +x master-controller.py
chmod +x core/*.py
```

## 📚 **การใช้งานพื้นฐาน**

### **1. เริ่มต้นใช้งาน**
```python
from master_controller import ChromeAutomationMaster

# สร้าง instance
master = ChromeAutomationMaster()

# เริ่มต้น controllers
master.initialize_all_controllers()

# เริ่ม browser session
master.start_browser_session('puppeteer', headless=False)
```

### **2. การใช้งานทั่วไป**
```python
# เปิดเว็บไซต์
master.navigate_to_url("https://www.google.com")

# ถ่าย screenshot และวิเคราะห์
analysis = master.take_screenshot_and_analyze("screenshot.png")

# Smart click
master.smart_click("search box")

# กรอกฟอร์มอัตโนมัติ
form_data = {"username": "test", "password": "test123"}
master.automated_form_filling(form_data)
```

## 🔒 **ความปลอดภัย**

### **1. API Key Security**
- อย่า commit API keys ลง Git
- ใช้ environment variables
- หมุนเวียน API keys เป็นประจำ

### **2. Browser Security**
- ใช้ headless mode ใน production
- ตั้งค่า user agent ที่เหมาะสม
- จำกัดการเข้าถึงไฟล์ระบบ

### **3. Error Handling**
- ใช้ try-catch blocks
- Log errors อย่างเหมาะสม
- มี fallback mechanisms

## 📞 **การสนับสนุน**

### **ติดต่อ:**
- Email: tenzaigroup.tech@gmail.com
- GitHub Issues: สำหรับ bug reports
- Documentation: อ่านไฟล์ README.md

### **Resources:**
- [Puppeteer Documentation](https://pptr.dev/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

---

**Last Updated:** 2 กรกฎาคม 2025  
**Version:** 1.0.0 