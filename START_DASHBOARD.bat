@echo off
REM Airline Tech Ops SPC Dashboard Launcher
REM This script starts the Python server and opens the dashboard
REM NO WEB SERVER INSTALLATION NEEDED - Uses Python's built-in server

echo.
echo ========================================================
echo   Airline Tech Ops SPC Dashboard
echo ========================================================
echo.
echo Checking Python...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

REM Start the server
echo Starting built-in Python web server...
echo Server will start on http://localhost:8000
echo.
echo IMPORTANT: Keep this window open while using the dashboard!
echo Press Ctrl+C to stop the server when done.
echo.
timeout /t 2 /nobreak >nul

REM Open the dashboard in default browser
echo Opening dashboard in your browser...
start http://localhost:8000

REM Start Python server (this will keep running)
python server.py

pause
