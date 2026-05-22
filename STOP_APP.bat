@echo off
echo ===================================================
echo DUNG HE THONG QL KHHH - BUU DIEN TP HUE
echo ===================================================

echo [1] Dang dung Backend (Port 8080)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul

echo [2] Dang dung Frontend (Port 5180)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5180 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul

echo ---------------------------------------------------
echo He thong da dung hoan toan.
echo ---------------------------------------------------
pause
