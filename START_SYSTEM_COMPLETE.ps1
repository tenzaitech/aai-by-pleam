Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Backup-byGod Complete System Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "D:\FULL-AI-IDEA\AI-NEWEVOKE_VER1\backup-bygod"

Write-Host "[INFO] Checking system status..." -ForegroundColor Green
Write-Host "[INFO] Current directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

Write-Host "[INFO] Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[SUCCESS] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found! Please install Python first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[INFO] Checking required files..." -ForegroundColor Green
if (-not (Test-Path "dashboard\app.py")) {
    Write-Host "[ERROR] Dashboard app.py not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "core\")) {
    Write-Host "[ERROR] Core directory not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[SUCCESS] All checks passed!" -ForegroundColor Green
Write-Host ""

Write-Host "[INFO] Starting Backup-byGod Dashboard..." -ForegroundColor Green
Write-Host "[INFO] Server will be available at: http://localhost:5000" -ForegroundColor Yellow
Write-Host "[INFO] Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Write-Host "[INFO] Starting system..." -ForegroundColor Green
python dashboard/app.py

Write-Host ""
Write-Host "[INFO] System stopped." -ForegroundColor Green
Read-Host "Press Enter to exit" 