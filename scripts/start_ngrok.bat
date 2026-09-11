@echo off
rem MIT License
rem Copyright (c) 2026 Manes2008/didicrew

echo =====================================================================
echo  [VideoCrew Ngrok] Khoi dong Ngrok Tunnel cho Backend FastAPI (8000)
echo =====================================================================

set "NGROK_BIN=ngrok"
if exist "D:\Dev\Projects\Server\ngrok.exe" (
    set "NGROK_BIN=D:\Dev\Projects\Server\ngrok.exe"
) else if exist "%~dp0..\ngrok.exe" (
    set "NGROK_BIN=%~dp0..\ngrok.exe"
) else if exist "%~dp0ngrok.exe" (
    set "NGROK_BIN=%~dp0ngrok.exe"
) else (
    where ngrok >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Khong tim thay ngrok.exe trong thu muc du an hoac trong bien moi truong PATH.
        pause
        exit /b 1
    )
)

set DOMAIN=unfrosted-alone-conduit.ngrok-free.dev
set PORT=8000

echo [*] Domain tinh: https://%DOMAIN%
echo [*] Dang tao tunnel toi Backend tai cong: %PORT%
echo [*] Nhan Ctrl+C de dung tunnel.
echo.

"%NGROK_BIN%" http --url=%DOMAIN% %PORT%

pause
