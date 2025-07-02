# BACKUP-BYGOD SYSTEM v1.0 - AI-Powered Backup & Restore
# PowerShell Launcher Script

# Set window title
$Host.UI.RawUI.WindowTitle = "🚀 BACKUP-BYGOD SYSTEM v1.0 - AI-Powered Backup & Restore"

# Set console colors
$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "Green"
Clear-Host

# ASCII Art Banner
Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║                    🚀 BACKUP-BYGOD SYSTEM v1.0              ║" -ForegroundColor Yellow
Write-Host "  ║                AI-Powered Backup & Restore                   ║" -ForegroundColor Yellow
Write-Host "  ║                                                              ║" -ForegroundColor Cyan
Write-Host "  ║  Features:                                                   ║" -ForegroundColor White
Write-Host "  ║  ✅ Parallel Processing (5x faster)                         ║" -ForegroundColor Green
Write-Host "  ║  ✅ AI-Powered Optimization                                  ║" -ForegroundColor Green
Write-Host "  ║  ✅ GPU Acceleration Support                                 ║" -ForegroundColor Green
Write-Host "  ║  ✅ One-Click Backup & Restore                               ║" -ForegroundColor Green
Write-Host "  ║  ✅ Smart Templates                                          ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Loading animation
Write-Host "  🚀 Starting BACKUP-BYGOD System..." -ForegroundColor Yellow
Start-Sleep -Milliseconds 500

Write-Host "  📊 Loading AI modules..." -ForegroundColor Blue
Start-Sleep -Milliseconds 300

Write-Host "  ⚡ Initializing parallel processors..." -ForegroundColor Magenta
Start-Sleep -Milliseconds 300

Write-Host "  🔧 Setting up smart templates..." -ForegroundColor Cyan
Start-Sleep -Milliseconds 300

Write-Host "  🎯 System ready! Launching..." -ForegroundColor Green
Write-Host ""

# Launch the system
try {
    python launch.py
} catch {
    Write-Host "  ❌ Error launching system: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  💡 Try running: python run_system.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 