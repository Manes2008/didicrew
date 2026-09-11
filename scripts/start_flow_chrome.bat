@echo off
title VideoCrew - Google Flow Dedicated Browser
echo [INFO] Dang khoi dong Google Chrome cho Google Flow...
echo [INFO] Profile duoc luu tru tai thu muc .chrome_profile

start "" chrome.exe --remote-debugging-port=9222 --user-data-dir="%~dp0..\.chrome_profile" "https://flow.google.com"

if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Khong tim thay chrome.exe mac dinh trong PATH. Thu khoi chay Chromium qua Python venv...
    cd /d "%~dp0.."
    venv\Scripts\python.exe -m playwright open --user-data-dir=".chrome_profile" "https://flow.google.com"
)
