@echo off
setlocal enabledelayedexpansion
rem MIT License
rem Copyright (c) 2026 Manes2008/didicrew

cd /d "%~dp0.."

echo =====================================================================
echo  [VideoCrew Studio] HE THONG TU DONG KIEM TRA VA CAI DAT ZERO-SETUP
echo =====================================================================

rem 1. Giai phong cac cong mang 8000, 3000, 3001, 8080 va tien trinh ngam
echo [*] Dang giai phong cong mang va tien trinh cu...
powershell -Command "Get-NetTCPConnection -LocalPort 8000, 3000, 3001, 8080 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM python3.13.exe >nul 2>&1
taskkill /F /IM cargo.exe >nul 2>&1
taskkill /F /IM tauri.exe >nul 2>&1

rem 2. Kiem tra va Tu dong cai dat Node.js neu chua co
where node >nul 2>&1
if errorlevel 1 (
    echo [*] Node.js chua duoc cai dat. Dang tu dong cai dat qua Winget...
    winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements --silent
)

rem 3. Kiem tra va Tu dong cai dat Python neu chua co
where python >nul 2>&1
if errorlevel 1 (
    echo [*] Python chua duoc cai dat. Dang tu dong cai dat qua Winget...
    winget install Python.Python.3.13 --accept-source-agreements --accept-package-agreements --silent
)

rem 4. Kiem tra va Tu dong cai dat Rust Toolchain neu chua co
where cargo >nul 2>&1
if errorlevel 1 (
    echo [*] Rust chua duoc cai dat. Dang tu dong cai dat Rustup...
    winget install Rustlang.Rustup --accept-source-agreements --accept-package-agreements --silent
    rustup default stable >nul 2>&1
)

rem 5. Kiem tra Workload C++ Tools (VC\Tools\MSVC)
set "HAS_MSVC=0"
if exist "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC" set "HAS_MSVC=1"
if exist "%ProgramFiles%\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC" set "HAS_MSVC=1"
if exist "%ProgramFiles%\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC" set "HAS_MSVC=1"

if "!HAS_MSVC!"=="0" (
    echo [*] C++ Build Tools chua hoan tat. Dang kich hoat trinh cai dat Microsoft C++ Tools...
    if exist "%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\setup.exe" (
        "%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\setup.exe" modify --installPath "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools" --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --passive --norestart
    ) else (
        winget install Microsoft.VisualStudio.2022.BuildTools --accept-source-agreements --accept-package-agreements --force --override "--passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended" --wait
    )
)

rem Nap moi truong C++ MSVC vao Session
if exist "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
    call "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
)
if exist "%ProgramFiles%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
    call "%ProgramFiles%\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
)

rem 6. Thiet lap Python Virtualenv va Thu vien Backend
if not exist "venv" (
    echo [*] Dang khoi tao moi truong ao Python venv...
    py -3.13 -m venv venv 2>nul || python -m venv venv
)
if exist "requirements.txt" (
    echo [*] Dang kiem tra dong bo thu vien Backend requirements.txt...
    ".\venv\Scripts\python.exe" -m pip install -q -r "requirements.txt"
)

rem 7. Thiet lap Dependencies Frontend
if exist "videocrew-ui" (
    if not exist "videocrew-ui\node_modules" (
        echo [*] Dang cai dat thu vien Frontend npm install...
        cd videocrew-ui
        call npm install
        cd ..
    )
)

rem 8. Khoi dong FastAPI Backend tai Port 8000
echo [*] Dang khoi dong FastAPI Backend tai http://127.0.0.1:8000 ...
start "VideoCrew - FastAPI Backend" cmd /k ".\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

rem 9. Khoi dong Cua so Desktop App bang Rust Tauri
if exist "videocrew-ui" (
    echo [*] Dang khoi dong Cua so Desktop Studio Tauri Rust...
    start "VideoCrew - Tauri Desktop Studio" cmd /k "cd videocrew-ui && npm run tauri:dev"
)

echo =====================================================================
echo  [VideoCrew Studio] HE THONG DA SAN SANG:
echo  - Backend API:    http://127.0.0.1:8000 (Swagger: /docs)
echo  - Desktop Studio: Tauri 2.0 (Rust Native Window 1280x800)
echo =====================================================================
pause
