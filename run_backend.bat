@echo off
REM Start Django Backend

title Hita - Django Backend (Port 8000)
color 0A

cd /d f:\Freelance\Hita_App\backend

echo.
echo ============================================
echo  🪷 HITA - Django Backend
echo ============================================
echo.

REM Check if venv exists
if not exist venv (
    color 0C
    echo ❌ Virtual environment not found!
    echo.
    echo Run setup first:
    echo   backend_setup.bat
    echo.
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    color 0C
    echo ❌ .env file not found!
    echo Please create .env with GEMINI_API_KEY
    pause
    exit /b 1
)

echo ✅ Environment ready
echo.
echo Starting Django server...
echo 🌐 http://localhost:8000
echo 🌐 API: http://localhost:8000/api
echo.
echo Press Ctrl+C to stop
echo.

python manage.py runserver 0.0.0.0:8000
