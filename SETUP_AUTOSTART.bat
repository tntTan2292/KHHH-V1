@echo off
setlocal
echo ===================================================
echo CAI DAT TU DONG KHOI DONG - QL KHHH
echo ===================================================

set "SCRIPT_PATH=%~dp0START_SERVICE.vbs"


echo [1] Dang kiem tra file START_SERVICE.vbs...
if not exist "%SCRIPT_PATH%" (
    echo [LOI] Khong tim thay file %SCRIPT_PATH%
    pause
    exit /b
)

echo [2] Dang dang ky vao Task Scheduler (Khoi dong cung Windows)...
schtasks /create /tn "KHHH_AutoStart" /tr "wscript.exe \"%SCRIPT_PATH%\"" /sc onlogon /f

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo CHUC MUNG! CAI DAT THANH CONG.
    echo.
    echo He thong se tu dong chay moi khi ban bat may tinh.
    echo Bay gio, em se bat dau chay thu ung dung ngay lap tuc...
    echo ===================================================
    start "" "%SCRIPT_PATH%"
) else (
    echo.
    echo [LOI] Khong the dang ky tu dong khoi dong. 
    echo Vui long chuot phai vao file nay va chon 'Run as Administrator'.
)

echo.
pause
