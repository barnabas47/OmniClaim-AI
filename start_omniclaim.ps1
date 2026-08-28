# OmniClaim AI - 1-Click PowerShell Launcher
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
$dir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $dir

$env:PATH = "C:\Users\Barnas\AppData\Local\Programs\Python\Python312;C:\Users\Barnas\AppData\Local\Programs\Python\Python312\Scripts;C:\Program Files\nodejs;" + $env:PATH

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  OmniClaim AI - Autonomous Passenger Rights Advocate" -ForegroundColor Yellow
Write-Host "  Starting Backend API & Frontend Control Center..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Start Backend Server
Start-Process cmd.exe -ArgumentList '/k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"' -WorkingDirectory $dir

# 2. Start Frontend
Start-Process cmd.exe -ArgumentList '/k "cd frontend && npm run dev"' -WorkingDirectory $dir

# 3. Open Browser
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"
