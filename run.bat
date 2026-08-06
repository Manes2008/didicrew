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

echo [VideoCrew] Dang cai dat PyTorch phien ban CUDA GPU...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
echo [VideoCrew] Dang cai dat/cap nhat thu vien phu thuoc...
pip install -r requirements.txt

echo [VideoCrew] Dang khoi chay Host Agent...
if not exist host-agent-launcher.exe (
    echo [VideoCrew] Khong tim thay host-agent-launcher.exe o thu muc goc.
    if exist host-agent-launcher\target\release\host-agent-launcher.exe (
        echo [VideoCrew] Phat hien file exe da bien dich. Dang copy ra thu muc goc...
        copy host-agent-launcher\target\release\host-agent-launcher.exe .
    ) else (
        echo [VideoCrew] Dang tu dong bien dich Desktop Launcher bang Cargo Rust...
        cd host-agent-launcher
        cargo build --release
        cd ..
        if exist host-agent-launcher\target\release\host-agent-launcher.exe (
            copy host-agent-launcher\target\release\host-agent-launcher.exe .
        )
    )
)

if exist host-agent-launcher.exe (
    start "" "host-agent-launcher.exe"
) else (
    echo [VideoCrew] Khong the tu dong bien dich launcher, dang tu dong chay host_agent.py truc tiep...
    start "" venv\Scripts\python.exe host_agent.py
)


echo [VideoCrew] Dang khoi chay Streamlit App...
streamlit run app.py

pause
