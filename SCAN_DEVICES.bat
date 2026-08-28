@echo off
title OmniClaim Device Scanner - Bluetooth and WiFi
color 0A
cls
echo ========================================================
echo   OmniClaim AI - Bluetooth and WiFi Device Scanner
echo ========================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host '=== 1. BLUETOOTH CONNECTED & PAIRED DEVICES ===' -ForegroundColor Cyan; Get-PnpDevice -Class Bluetooth | Where-Object { $_.Status -eq 'OK' } | Select-Object FriendlyName, Status, Class, InstanceId | Format-Table -AutoSize; Write-Host '=== 2. LOCAL NETWORK & WIFI DEVICES ===' -ForegroundColor Yellow; Get-NetNeighbor | Where-Object { $_.State -ne 'Unreachable' -and $_.IPAddress -like '192.168.*' } | Select-Object IPAddress, LinkLayerAddress, State | Format-Table -AutoSize; Write-Host '=== 3. ADB ANDROID DEVICES ===' -ForegroundColor Green; & 'C:\Users\Barnas\AppData\Local\Android\Sdk\platform-tools\adb.exe' devices -l"

echo.
echo ========================================================
echo   Scan complete! Window will stay open.
echo   Press any key to exit.
echo ========================================================
pause
