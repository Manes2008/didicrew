@echo off
rem MIT License
rem Copyright (c) 2026 Manes2008/didicrew

echo [VideoCrew Redeploy] Dang kiem tra Docker Desktop...

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker hien tai chua chay. Vui long khoi dong Docker Desktop va thu lai.
    pause
    exit /b 1
)

echo [VideoCrew Redeploy] Dang keo ma nguon moi nhat tu Git...
git pull

if %errorlevel% neq 0 (
    echo [WARN] Co loi khi pull code tu Git. Dang tiep tuc qua trinh build local...
)

echo [VideoCrew Redeploy] Dang khoi dong lai container va bao ton database...
docker compose up -d --build --no-deps videocrew

if %errorlevel% == 0 (
    echo [VideoCrew Redeploy] Cap nhat code va khoi chay thanh cong!
    echo [VideoCrew Redeploy] Du lieu Database duoc giu nguyen an toan.
    echo [VideoCrew Redeploy] Ung dung Streamlit dang chay tai: http://localhost:8501
) else (
    echo [ERROR] Co loi xay ra trong qua trinh redeploy.
)

pause
