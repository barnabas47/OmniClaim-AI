@echo off
title OmniClaim Mobile App Launcher
echo ========================================================
echo   OmniClaim AI - Mobile Phone App Launcher
echo   Keep PC App Running + Enable Mobile Phone Access
echo ========================================================

cd /d "%~dp0"

REM Ensure Python 3.12 and Node.js are in PATH
set PATH=C:\Users\Barnas\AppData\Local\Programs\Python\Python312;C:\Users\Barnas\AppData\Local\Programs\Python\Python312\Scripts;C:\Program Files\nodejs;%PATH%

echo [1/3] Launching Python Backend API (Network Access Enabled)...
start "OmniClaim Mobile Backend" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

echo [2/3] Launching React Mobile App Server (Network Access Enabled)...
start "OmniClaim Mobile Frontend" cmd /k "cd frontend && npm run dev -- --host 0.0.0.0"

echo [3/3] Fetching Local Network IP Address...
timeout /t 3 /nobreak >nul

echo.
echo ========================================================
echo   OMNICLAIM MOBILE APP IS LIVE!
echo.
echo   Open your mobile phone browser and visit:
echo.
for /f "tokens=14" %%i in ('ipconfig ^| findstr /i "IPv4"') do (
    echo   👉 http://%%i:5173
)
echo.
echo   PC Browser URL: http://localhost:5173
echo ========================================================
