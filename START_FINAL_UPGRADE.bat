@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🚀 FINAL UPGRADE - backup-bygod v2.0.0
echo ========================================
echo.
echo 📋 เริ่มการ UPGRADE ขั้นสุดท้าย...
echo 📅 เวลา: %date% %time%
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ไม่พบ Python กรุณาติดตั้ง Python 3.8+ ก่อน
    pause
    exit /b 1
)

echo ✅ Python พร้อมใช้งาน

REM Check required files
if not exist "FINAL_UPGRADE_LAUNCHER.py" (
    echo ❌ ไม่พบไฟล์ FINAL_UPGRADE_LAUNCHER.py
    pause
    exit /b 1
)

if not exist "config\final_upgrade_config.json" (
    echo ❌ ไม่พบไฟล์ config\final_upgrade_config.json
    pause
    exit /b 1
)

echo ✅ ไฟล์ที่จำเป็นพร้อมใช้งาน

REM Create logs directory
if not exist "logs" mkdir logs

echo.
echo 🔄 เริ่มการ UPGRADE...
echo.

REM Run the final upgrade
python FINAL_UPGRADE_LAUNCHER.py

if errorlevel 1 (
    echo.
    echo ❌ การ UPGRADE ล้มเหลว
    echo 📋 ตรวจสอบ logs ในโฟลเดอร์ logs\
    pause
    exit /b 1
) else (
    echo.
    echo ✅ การ UPGRADE สำเร็จ!
    echo 📊 ตรวจสอบรายงานใน FINAL_UPGRADE_REPORT.json
    echo.
)

echo.
echo 🎉 FINAL UPGRADE COMPLETED!
echo.
pause 