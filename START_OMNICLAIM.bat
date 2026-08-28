@echo off
title OmniClaim AI Launcher
echo ========================================================
echo   OmniClaim AI - Autonomous Passenger Rights Advocate
echo   Starting Backend API & Frontend Control Center...
echo ========================================================

cd /d "%~dp0"

REM Ensure Python 3.12 and Node.js are in PATH
set PATH=C:\Users\Barnas\AppData\Local\Programs\Python\Python312;C:\Users\Barnas\AppData\Local\Programs\Python\Python312\Scripts;C:\Program Files\nodejs;%PATH%

echo [1/3] Launching Python FastAPI Backend Server (Port 8000)...
start "OmniClaim Backend Server" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

echo [2/3] Launching React Frontend UI (Port 5173)...
start "OmniClaim Frontend UI" cmd /k "cd frontend && npm run dev"

echo [3/3] Opening browser at http://localhost:5173...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ========================================================
echo   OmniClaim AI is running! Check your browser window.
echo ========================================================
