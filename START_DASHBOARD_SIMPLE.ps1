Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Backup-byGod Dashboard Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "D:\FULL-AI-IDEA\AI-NEWEVOKE_VER1\backup-bygod"

Write-Host "[INFO] Starting Dashboard Server..." -ForegroundColor Green
Write-Host "[INFO] Server will be available at: http://localhost:5000" -ForegroundColor Yellow
Write-Host "[INFO] Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python dashboard/app.py

Read-Host "Press Enter to exit" 