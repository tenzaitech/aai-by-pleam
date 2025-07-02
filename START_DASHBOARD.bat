@echo off
chcp 65001 >nul
title Backup-byGod Dashboard Launcher

echo.
echo ========================================
echo    🚀 Backup-byGod Dashboard Launcher
echo ========================================
echo.

cd /d "%~dp0"

echo 📋 กำลังตรวจสอบ dependencies...
python -c "import flask, flask_socketio, psutil" 2>nul
if errorlevel 1 (
    echo ⚠️  กำลังติดตั้ง dependencies...
    pip install flask flask-socketio psutil
    if errorlevel 1 (
        echo ❌ ไม่สามารถติดตั้ง dependencies ได้
        pause
        exit /b 1
    )
)

echo ✅ Dependencies พร้อม

echo.
echo 🌐 กำลังเริ่มต้น Dashboard Server...
echo 📍 URL: http://localhost:5000
echo 🔗 เปิดเบราว์เซอร์และไปที่ URL ข้างต้น
echo.
echo 💡 กด Ctrl+C เพื่อหยุด server
echo.

cd dashboard
python app.py

pause 