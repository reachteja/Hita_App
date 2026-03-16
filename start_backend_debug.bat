@echo off
REM Quick start Django backend with error visibility

title Hita - Django Backend (Port 8000)
color 0A

cd /d f:\Freelance\Hita_App\backend

echo.
echo ============================================
echo  🪷 HITA - Django Backend Server
echo ============================================
echo.

if not exist venv (
    color 0C
    echo ❌ Virtual environment not found!
    echo.
    echo Solution: Run setup.bat first
    echo.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if not exist .env (
    color 0C
    echo ❌ .env file not found!
    echo.
    echo Solution: Create .env file with:
    echo    GEMINI_API_KEY=your_key_here
    echo.
    pause
    exit /b 1
)

echo ✅ Environment ready
echo.
echo Starting Django...
echo.
echo 🌐 Backend API will be at: http://localhost:8000
echo 🌐 API endpoints will be at: http://localhost:8000/api
echo.
echo Press Ctrl+C to stop
echo.

python manage.py runserver 0.0.0.0:8000
