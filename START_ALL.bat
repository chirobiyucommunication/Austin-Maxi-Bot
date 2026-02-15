@echo off
REM Austin Maxi Bot - Windows Startup Script
REM Run all services in separate windows

echo.
echo ========================================
echo  Austin Maxi Bot - Starting Services
echo ========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
    playwright install chromium
)

REM Activate venv
call venv\Scripts\activate.bat

echo.
echo Starting License Server (Port 5000)...
start "License Server" cmd /k "python server.py"

timeout /t 2

echo Starting Signal Server (Port 5001)...
start "Signal Server" cmd /k "python signal_bot.py"

timeout /t 2

echo Starting Admin Bot...
start "Admin Bot" cmd /k "python admin_bot.py"

timeout /t 2

echo Starting Client Bot...
start "Client Bot" cmd /k "python client_bot.py"

timeout /t 2

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo License Server: http://localhost:5000
echo Signal Server:  http://localhost:5001
echo.
echo Telegram Bots are running in separate windows.
echo.
pause
