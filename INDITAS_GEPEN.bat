@echo off
title OmniClaim AI - PC Launcher
echo ========================================================
echo   OmniClaim AI - PC/Desktop Launching System
echo ========================================================

cd /d "%~dp0"

REM Add Python and Node.js to PATH
set PATH=C:\Users\Barnas\AppData\Local\Programs\Python\Python312;C:\Users\Barnas\AppData\Local\Programs\Python\Python312\Scripts;C:\Program Files\nodejs;%PATH%

echo [1/3] Starting Python AI Backend (Port 8000)...
start "OmniClaim Backend" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

echo [2/3] Starting Desktop Control Center (Port 3000)...
start "OmniClaim Frontend" cmd /k "cd frontend && npx vite --port 3000 --host"

echo [3/3] Opening browser at http://localhost:3000...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================================
echo   OmniClaim AI Desktop version is running!
echo   Browser URL: http://localhost:3000
echo ========================================================
