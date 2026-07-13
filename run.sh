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

echo "[VideoCrew] Dang cai dat/cap nhat thu vien phu thuoc..."
pip install -r requirements.txt

echo "[VideoCrew] Dang khoi chay Streamlit App..."
streamlit run app.py
