@echo off
REM Complete Backend Setup Script

title Hita - Backend Setup
color 0A

cd /d f:\Freelance\Hita_App\backend

echo.
echo ============================================
echo  🪷 HITA - Backend Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Python not found!
    echo Please install Python 3.9+
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        color 0C
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo ⚠️  NOTE: .env created. Update GEMINI_API_KEY if needed!
)
echo.

REM Install dependencies
echo Installing dependencies from requirements.txt...
echo This may take 2-3 minutes...
echo.
pip install -r requirements.txt
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo.
echo ✅ Dependencies installed
echo.

REM Run migrations
echo Running database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    color 0C
    echo ⚠️  Migration warning - PostgreSQL may not be set up yet
    echo Check your database configuration in .env
)
echo.

color 0B
echo ============================================
echo  ✅ Backend Setup Complete!
echo ============================================
echo.
echo Next: Start the backend with:
echo   cd f:\Freelance\Hita_App\backend
echo   call venv\Scripts\activate.bat
echo   python manage.py runserver 0.0.0.0:8000
echo.
pause
