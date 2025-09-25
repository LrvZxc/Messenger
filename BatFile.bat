@echo off
REM Открываем сервер
start cmd /k "python mserver.py"

REM Немного ждём, чтобы сервер успел стартовать
timeout /t 2 /nobreak >nul

REM Открываем первого клиента
start cmd /k "python mclient.py"

REM Открываем второго клиента
start cmd /k "python mclient.py"

echo Все программы запущены.
pause