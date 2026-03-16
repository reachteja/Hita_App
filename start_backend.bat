@echo off
REM Start Backend Django Server
title Hita - Django Backend (Port 8000)
color 0A

cd /d f:\Freelance\Hita_App\backend

echo.
echo ============================================
echo  🪷 HITA - Django Backend Server
echo ============================================
echo.

REM Check if venv exists
if not exist venv (
    color 0C
    echo ❌ Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    color 0C
    echo ❌ .env file not found!
    echo Please create .env from .env.example and add GEMINI_API_KEY
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo.
echo Starting Django development server...
echo.
echo 🌐 Backend API: http://localhost:8000/api
echo 🔧 Django Admin: http://localhost:8000/admin
echo.
echo 📝 Keep this terminal open
echo 🛑 Press Ctrl+C to stop
echo.

python manage.py runserver
