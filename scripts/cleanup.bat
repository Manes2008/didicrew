@echo off
rem MIT License
rem Copyright (c) 2026 Manes2008/didicrew

echo ===================================================
echo [VideoCrew Studio] Dang don sach toan bo cong mang va tien trinh ngam...
echo ===================================================

rem 1. Giai phong cac cong 8000, 3000, 3001, 8080
powershell -Command "Get-NetTCPConnection -LocalPort 8000, 3000, 3001, 8080 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1

rem 2. Tat cac tien trinh node, python, cargo, tauri neu con chay ngam
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python3.13.exe >nul 2>&1
taskkill /F /IM cargo.exe >nul 2>&1
taskkill /F /IM tauri.exe >nul 2>&1

echo [VideoCrew] Da giai phong toan bo cong (8000, 3000, 3001) va tien trinh ngam thanh cong!
echo ===================================================
timeout /t 2 /nobreak >nul
