@echo off
rem VideoCrew DB Restore Script
rem Copyright (c) 2026 Manes2008/didicrew

echo [VideoCrew Restore] Dang kiem tra Docker Desktop...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker hien tai chua chay. Vui long khoi dong Docker Desktop va thu lai.
    pause
    exit /b 1
)

rem Kiem tra container database co dang chay khong
docker ps --filter "name=videocrew-db" --filter "status=running" | findstr "videocrew-db" >nul
if %errorlevel% neq 0 (
    echo [ERROR] Container database "videocrew-db" hien khong chay. Vui long chay run.bat/deploy.bat truoc.
    pause
    exit /b 1
)

if not exist backups (
    echo [WARN] Thu muc backups chua ton tai. Khong co ban backup nao de khoi phuc.
    pause
    exit /b 0
)

echo [VideoCrew Restore] Danh sach cac ban backup hien co:
echo ----------------------------------------------------
dir backups\*.sql /b
echo ----------------------------------------------------
echo.

set /p FILE_NAME="Nhap ten file backup can restore (vi du: didicrew_backup_20260731_1540.sql): "

if not exist backups\%FILE_NAME% (
    echo [ERROR] File backup "backups\%FILE_NAME%" khong ton tai. Vui long kiem tra lai.
    pause
    exit /b 1
)

echo.
echo [WARNING] QUY TRINH KHOI PHUC SE GHI DE TOAN BO DU LIEU DANG CO CUA DATABASE HIEN TAI!
set /p CONFIRM="Ban co chac chan muon tiep tuc? (Y/N): "

if /i "%CONFIRM%" neq "Y" (
    echo [VideoCrew Restore] Da huy bo qua trinh khoi phuc.
    pause
    exit /b 0
)

echo [VideoCrew Restore] Dang khoi phuc database tu backups\%FILE_NAME%...
docker exec -i videocrew-db psql -U postgres -d didicrew < backups\%FILE_NAME%

if %errorlevel% == 0 (
    echo.
    echo [OK] Khoi phuc database thanh cong!
    echo [OK] Du lieu da duoc dong bo lai vao container.
) else (
    echo [ERROR] Co loi xay ra trong qua trinh khoi phuc DB.
)

pause
