#!/usr/bin/env bash
# MIT License
# Copyright (c) 2026 Manes2008/didicrew

echo "[VideoCrew Docker] Dang kiem tra Docker service..."

if ! docker info >/dev/null 2>&1; then
    echo "[ERROR] Docker chua duoc cai dat hoac service Docker chua khoi chay."
    exit 1
fi

if [ ! -f .env ]; then
    echo "[WARN] Khong tim thay file .env. Vui long kiem tra lai cau hinh."
fi

echo "[VideoCrew Docker] Dang dung va don dep container cu de tranh xung dot..."
docker-compose down
echo "[VideoCrew Docker] Dang build va khoi chay cac container moi (Streamlit + PostgreSQL)..."
docker-compose up -d --build --force-recreate

if [ $? -eq 0 ]; then
    echo "[VideoCrew Docker] Khoi chay thanh cong!"
    echo "[VideoCrew Docker] Ung dung Streamlit dang chay tai: http://localhost:8501"
    echo "[VideoCrew Docker] PostgreSQL dang chay tai port 5432"
    echo "[VideoCrew Docker] Xem log: docker-compose logs -f videocrew"
else
    echo "[ERROR] Co loi xay ra khi khoi chay Docker Compose."
fi
