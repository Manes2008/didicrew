@echo off
rem MIT License
rem Copyright (c) 2026 Manes2008/didicrew

echo [VideoCrew Docker] Dang kiem tra Docker service...

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker chinh can phai dang chay hoac chua duoc cai dat. Vui long bat Docker Desktop truoc.
    pause
    exit /b 1
)

if not exist .env (
    echo [WARN] Khong tim thay file .env. Vui long kiem tra lai cau hinh moi truong.
)

echo [VideoCrew Docker] Dang dung va don dep container cu de tranh xung dot...
docker compose down
echo [VideoCrew Docker] Dang build va khoi chay cac container moi (Streamlit + PostgreSQL)...
docker compose up -d --build --force-recreate

if %errorlevel% eq 0 (
    echo [VideoCrew Docker] Khoi chay thanh cong!
    echo [VideoCrew Docker] Ung dung Streamlit dang chay tai: http://localhost:8501
    echo [VideoCrew Docker] PostgreSQL dang chay tai port 5432
    echo [VideoCrew Docker] Kiem tra log ung dung bang lenh: docker compose logs -f videocrew
) else (
    echo [ERROR] Co loi xay ra khi khoi chay Docker Compose.
)

pause
