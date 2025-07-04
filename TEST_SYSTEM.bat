@echo off
echo ========================================
echo    Backup-byGod System Test
echo ========================================
echo.

cd /d "D:\FULL-AI-IDEA\AI-NEWEVOKE_VER1\backup-bygod"

echo [INFO] Testing all system components...
echo [INFO] This will verify that all modules work correctly
echo.

python test_system_components.py

echo.
echo [INFO] Test completed!
pause 