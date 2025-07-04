@echo off
echo ========================================
echo    Backup-byGod Complete System Launcher
echo ========================================
echo.

cd /d "D:\FULL-AI-IDEA\AI-NEWEVOKE_VER1\backup-bygod"

echo [INFO] Checking system status...
echo [INFO] Current directory: %CD%
echo.

echo [INFO] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b 1
)

echo [INFO] Checking required files...
if not exist "dashboard\app.py" (
    echo [ERROR] Dashboard app.py not found!
    pause
    exit /b 1
)

if not exist "core\" (
    echo [ERROR] Core directory not found!
    pause
    exit /b 1
)

echo [INFO] All checks passed!
echo.

echo [INFO] Starting Backup-byGod Dashboard...
echo [INFO] Server will be available at: http://localhost:5000
echo [INFO] Press Ctrl+C to stop the server
echo.

echo [INFO] Starting system...
python dashboard/app.py

echo.
echo [INFO] System stopped.
pause 