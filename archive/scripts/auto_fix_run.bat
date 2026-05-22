@echo off
echo === START AUTO FIX & RUN PROJECT ===

echo Installing dependencies...
call npm install

echo Starting dev server...
start cmd /k npm run dev

timeout /t 5

echo Opening browser...
start http://localhost:5180

echo === DONE ===