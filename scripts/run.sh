#!/bin/bash
# MIT License
# Copyright (c) 2026 Manes2008/didicrew

echo "[VideoCrew] Dang kiem tra moi truong python..."

if [ ! -d "venv" ]; then
    echo "[VideoCrew] Khong tim thay venv. Dang tao moi truong ao venv..."
    python3 -m venv venv
fi

echo "[VideoCrew] Dang kich hoat moi truong ao venv..."
source venv/bin/activate

echo "[VideoCrew] Dang cai dat/cap nhat thu vien phu thuoc Backend..."
pip install -r requirements.txt

echo "[VideoCrew] Dang khoi chay FastAPI Backend tai http://127.0.0.1:8000 ..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

if [ -d "../videocrew-ui" ]; then
    echo "[VideoCrew] Dang khoi chay Next.js Frontend..."
    cd ../videocrew-ui && npm run dev &
    cd ..
fi

echo "====================================================="
echo "  [VideoCrew Studio] HE THONG DA SAN SANG:"
echo "  - Backend API : http://127.0.0.1:8000 (Swagger: /docs)"
echo "  - Frontend    : http://localhost:3000"
echo "====================================================="

wait $BACKEND_PID
