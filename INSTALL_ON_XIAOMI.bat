@echo off
title OmniClaim Xiaomi 11T Pro App Installer
color 0B
cls
echo ========================================================
echo   OmniClaim AI - Xiaomi 11T Pro App Installer
echo   Target Device: Xiaomi 11T Pro (IP: 192.168.1.189)
echo ========================================================
echo.

set ADB=C:\Users\Barnas\AppData\Local\Android\Sdk\platform-tools\adb.exe

echo [*] Attempting automatic connection to Xiaomi 11T Pro (192.168.1.189)...
"%ADB%" connect 192.168.1.189:5555

echo.
echo [*] Checking connected devices...
"%ADB%" devices -l

echo.
echo ========================================================
echo   IF YOUR XIAOMI IS NOT CONNECTED YET:
echo.
echo   On your Xiaomi 11T Pro:
echo   1. Go to Settings - Developer Options (Fejlesztoi beallitasok)
echo   2. Turn ON "Wireless Debugging" (Vezetek nekuli hibakereses)
echo   3. Look at the port number shown under "IP address & Port"
echo   (e.g., 192.168.1.189:42135)
echo ========================================================
echo.

set /p PORT=Enter the 5-digit port number from your Xiaomi screen (or press ENTER to try 5555): 

if not "%PORT%"=="" (
    echo Connecting ADB to 192.168.1.189:%PORT%...
    "%ADB%" connect 192.168.1.189:%PORT%
)

echo.
echo [*] Installing OmniClaim-Xiaomi11TPro.apk on Xiaomi 11T Pro...
"%ADB%" install -r "OmniClaim-Xiaomi11TPro.apk"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   SUCCESS! OmniClaim Mobile App is installed on Xiaomi 11T Pro!
    echo   Launching app on phone screen now...
    echo ========================================================
    "%ADB%" shell am start -n com.omniclaim.app/.MainActivity
) else (
    echo.
    echo ========================================================
    echo   EASY ALTERNATIVE INSTALL:
    echo   Simply copy 'OmniClaim-Xiaomi11TPro.apk' to your phone
    echo   via Bluetooth or USB cable, and tap to install!
    echo ========================================================
)

echo.
echo Press any key to exit...
pause >nul
