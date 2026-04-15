@echo off
REM SavySoil Backend - Local Development Setup Script (Windows)
REM ============================================================
REM This script sets up your local development environment for the SavySoil backend

setlocal enabledelayedexpansion

echo 🌱 SavySoil Backend - Local Setup (Windows)
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ !PYTHON_VERSION! found
echo.

REM Get the directory where this script is located
set BACKEND_DIR=%~dp0
cd /d "%BACKEND_DIR%"

echo 📂 Working directory: %BACKEND_DIR%
echo.

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

echo.

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

echo.

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt --quiet
echo ✅ Dependencies installed

echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 🔐 Creating .env file...
    copy .env.example .env >nul
    echo ✅ .env file created
    echo.
    echo ⚠️  UPDATE .env WITH YOUR SETTINGS:
    echo    - GEMMA_API_KEY: Your LLM provider API key
    echo    - GEMMA_ENDPOINT: Your LLM endpoint URL
    echo    - GITHUB_PAGES_ORIGIN: http://localhost:3000 (for testing)
    echo.
) else (
    echo ✅ .env file already exists
)

echo.
echo ✨ Setup complete!
echo.
echo To start the development server, run:
echo   cd backend
echo   venv\Scripts\activate
echo   uvicorn main:app --reload
echo.
echo Then visit: http://localhost:8000/docs
echo.
pause
