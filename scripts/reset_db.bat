@echo off
echo [VideoCrew] Dang kiem tra moi truong ao (virtual environment)...

set VENV_PATH=

if exist venv (
    set VENV_PATH=venv
) else if exist .venv (
    set VENV_PATH=.venv
) else if exist env (
    set VENV_PATH=env
)

if "%VENV_PATH%"=="" (
    echo [ERROR] Khong tim thay thu muc moi truong ao (venv, .venv, env).
    echo Vui long kiem tra lai moi truong tren server.
    pause
    exit /b
)

echo [VideoCrew] Kich hoat moi truong ao tu: %VENV_PATH%...
call %VENV_PATH%\Scripts\activate.bat

echo [VideoCrew] Dang dong bo hoa cac Sequence Database...
set PYTHONPATH=.
python scratch/reset_db.py

echo [VideoCrew] Hoan tat!
pause
