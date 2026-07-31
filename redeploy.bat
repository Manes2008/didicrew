@echo off
rem VideoCrew Redeploy - Giu nguyen Database, xoa sach image/container cu
rem Copyright (c) 2026 Manes2008/didicrew

echo [VideoCrew Redeploy] Dang kiem tra Docker Desktop...

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker chua chay. Vui long khoi dong Docker Desktop va thu lai.
    pause
    exit /b 1
)

echo [VideoCrew Redeploy] Dang keo ma nguon moi nhat tu Git...
git pull
if %errorlevel% neq 0 (
    echo [WARN] Co loi khi pull Git. Tiep tuc voi code hien tai...
)

echo [VideoCrew Redeploy] Dang dung container - GIU NGUYEN VOLUME DATABASE...
rem Khong dung "-v" nen tat ca volume (bao gom DB) duoc bao toan
docker compose down

echo [VideoCrew Redeploy] Dang xoa image app cu (tranh cache code cu)...
rem Chi xoa image cua app videocrew, khong dung den postgres/redis
for /f "tokens=*" %%i in ('docker images --filter "reference=videocrew*" -q 2^>nul') do (
    docker image rm -f %%i >nul 2>&1
)
rem Xoa dangling images (anh bi thay the, khong co tag)
docker image prune -f >nul 2>&1

echo [VideoCrew Redeploy] Dang build lai va khoi dong container moi...
docker compose up -d --build --force-recreate

if %errorlevel% == 0 (
    echo.
    echo [OK] Redeploy thanh cong!
    echo [OK] Code moi da duoc ap dung - Database giu nguyen an toan.
    echo [OK] Ung dung chay tai: http://localhost:8501
    echo [OK] Xem log: docker compose logs -f videocrew
) else (
    echo [ERROR] Co loi trong qua trinh redeploy. Xem chi tiet: docker compose logs videocrew
)

pause
