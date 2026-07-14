@echo off
rem MIT License
rem Copyright (c) 2026 Manes2008/didicrew

echo [VideoCrew] Dang kiem tra moi truong python...

if not exist venv (
    echo [VideoCrew] Khong tim thay venv. Dang tao moi truong ao venv...
    py -3.13 -m venv venv
)

echo [VideoCrew] Dang kich hoat moi truong ao venv...
call venv\Scripts\activate.bat

echo [VideoCrew] Dang cai dat/cap nhat thu vien phu thuoc...
pip install -r requirements.txt

echo [VideoCrew] Dang khoi chay Streamlit App...
streamlit run app.py

pause
