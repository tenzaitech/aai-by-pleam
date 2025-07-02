@echo off
echo ========================================
echo    Backup-byGod Dashboard Launcher
echo ========================================
echo.

cd /d "D:\FULL-AI-IDEA\AI-NEWEVOKE_VER1\backup-bygod"

echo [INFO] Starting Dashboard Server...
echo [INFO] Server will be available at: http://localhost:5000
echo [INFO] Press Ctrl+C to stop the server
echo.

python dashboard/app.py

pause 