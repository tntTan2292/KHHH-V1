@echo off
setlocal
echo ===================================================
echo KHOI DONG HE THONG QL KHHH - BUU DIEN TP HUE
echo ===================================================

cd /d "%~dp0"

echo [1] Kiem tra trang thai dich vu...
:: Them duong dan Node.js portable neu co
set "PATH=%PATH%;C:\Users\Admin\nodejs_portable_v22\node-v22.12.0-win-x64"

echo [1.5] Kiem tra dong bo du lieu (V1 Startup Sync)...
:: backend\venv\Scripts\python backend\scripts\check_sync_on_startup.py

echo [2] Khoi dong Backend (Port 8080)...
cd backend
start "KHHH_BACKEND" /B venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

echo [3] Khoi dong Frontend (Port 5180)...
cd ..
:: Check if npm.cmd exists before running
where npm.cmd >nul 2>&1
if %ERRORLEVEL% equ 0 (
    start "KHHH_FRONTEND" /B npm.cmd run dev -- --port 5180 --host
) else (
    echo [LOI] Khong tim thay Node.js/NPM. Vui long cai dat de chay Frontend.
)

:: Su dung ping thay the timeout de hoat dong dung trong cua so an (background)
ping 127.0.0.1 -n 6 >nul
start http://localhost:5180


echo ---------------------------------------------------
echo He thong dang chay ngam. Vui long kiem tra trinh duyet.
echo ---------------------------------------------------
exit
