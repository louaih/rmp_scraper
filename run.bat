@echo off
REM RMP Analyzer Web App - Local Startup Script (Windows)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please create a .env file with your OPENAI_API_KEY:
    echo.
    echo   copy .env.example .env
    echo   REM Edit .env and add your key
    echo.
    pause
    exit /b 1
)

REM Create data directories if they don't exist
if not exist "data\input" mkdir data\input
if not exist "data\output" mkdir data\output
if not exist "logs" mkdir logs

REM Start the Flask app
echo.
echo Starting RMP Analyzer Web App...
echo Access at: http://localhost:5000
echo.
echo Press Ctrl+C to stop
echo.

python app.py
pause
