@echo off
echo ========================================
echo    🚀 Backup-byGod Dashboard Server
echo ========================================
echo.
echo Starting Dashboard Server...
echo.
echo 🌐 Dashboard will be available at:
echo    http://localhost:5000
echo.
echo 📊 Features available:
echo    - System Capabilities Monitor
echo    - Real-time Log Monitor
echo    - Project Status Report
echo    - 🧠 Knowledge Manager (NEW!)
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd /d "%~dp0"
python dashboard/app.py

pause 