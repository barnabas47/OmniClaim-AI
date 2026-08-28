# OmniClaim AI Launcher Script
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  OmniClaim AI - Autonomous Passenger Rights Advocate" -ForegroundColor Cyan
Write-Host "  Starting Backend API & Frontend Control Center..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$env:PATH = "C:\Users\Barnas\AppData\Local\Programs\Python\Python312;C:\Users\Barnas\AppData\Local\Programs\Python\Python312\Scripts;C:\Program Files\nodejs;" + $env:PATH

# Start Backend Server
Start-Process cmd -ArgumentList "/k python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000" -WorkingDirectory $PSScriptRoot

# Start Frontend UI
Start-Process cmd -ArgumentList "/k cd frontend && npm run dev" -WorkingDirectory $PSScriptRoot

Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"

Write-Host "OmniClaim AI is running at http://localhost:3000" -ForegroundColor Green
