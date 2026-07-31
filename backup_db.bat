@echo off
rem VideoCrew DB Backup Script
rem Copyright (c) 2026 Manes2008/didicrew

echo [VideoCrew Backup] Dang kiem tra Docker Desktop...
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

rem Tao thu muc backups neu chua co
if not exist backups mkdir backups

rem Lay thoi gian hien tai lam timestamp (YYYYMMDD_HHMM)
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,4%
set BACKUP_FILE=backups\didicrew_backup_%TIMESTAMP%.sql

echo [VideoCrew Backup] Dang backup database ra file %BACKUP_FILE%...
docker exec -t videocrew-db pg_dump -U postgres -d didicrew > "%BACKUP_FILE%"

if %errorlevel% == 0 (
    echo.
    echo [OK] Backup database thanh cong!
    echo [OK] Du lieu duoc luu an toan tai: %BACKUP_FILE%
) else (
    echo [ERROR] Co loi xay ra trong qua trinh backup.
)

pause
