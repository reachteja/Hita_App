@echo off
REM Start Celery Worker
title Hita - Celery Worker
color 0A

cd /d f:\Freelance\Hita_App\backend

echo.
echo ============================================
echo  🪷 HITA - Celery Worker
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

echo ✅ Virtual environment activated
echo.
echo Starting Celery worker...
echo.
echo 📝 Background task processing
echo ⚙️  Document extraction, embedding, categorization
echo.
echo 📝 Keep this terminal open
echo 🛑 Press Ctrl+C to stop
echo.

celery -A hita_project worker --loglevel=info --pool=solo
