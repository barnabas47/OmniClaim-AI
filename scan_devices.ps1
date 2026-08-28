Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Clear-Host

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  OmniClaim AI - Bluetooth & Network Device Scanner" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== 1. BLUETOOTH CONNECTED & PAIRED DEVICES ===" -ForegroundColor Cyan
Get-PnpDevice -Class Bluetooth | Where-Object { $_.Status -eq "OK" } | Select-Object FriendlyName, Status, Class, InstanceId | Format-Table -AutoSize

Write-Host "=== 2. LOCAL WI-FI NETWORK DEVICES ===" -ForegroundColor Yellow
Get-NetNeighbor | Where-Object { $_.State -ne "Unreachable" -and $_.IPAddress -like "192.168.*" } | Select-Object IPAddress, LinkLayerAddress, State | Format-Table -AutoSize

Write-Host "=== 3. ADB CONNECTED ANDROID DEVICES ===" -ForegroundColor Green
& "C:\Users\Barnas\AppData\Local\Android\Sdk\platform-tools\adb.exe" devices -l

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Press ENTER to exit..." -ForegroundColor White
Read-Host
