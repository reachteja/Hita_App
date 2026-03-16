@echo off
REM Hita - Windows Setup Automation Script
REM This script helps automate the first-time setup

cls
color 0A
echo.
echo ============================================
echo  🪷 HITA - Windows Setup Script
echo ============================================
echo.
echo This script will help you set up Hita locally
echo Prerequisites needed before running:
echo  ✓ Python 3.12+
echo  ✓ PostgreSQL 16
echo  ✓ Redis
echo  ✓ Tesseract OCR
echo  ✓ Node.js 18+
echo.
pause

echo.
echo Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Python not found. Please install Python 3.12+ and add to PATH
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Check PostgreSQL
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ PostgreSQL not found. Please install PostgreSQL 16
    pause
    exit /b 1
)
echo ✅ PostgreSQL found

REM Check Redis
redis-cli --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Redis not found. Please install Redis
    pause
    exit /b 1
)
echo ✅ Redis found

REM Check Tesseract
tesseract --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Tesseract not found. Please install Tesseract OCR
    pause
    exit /b 1
)
echo ✅ Tesseract OCR found

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js %NODE_VERSION% found

color 0A
echo.
echo ============================================
echo ✅ All prerequisites found!
echo ============================================
echo.
pause

REM Setup Backend
echo.
echo ============================================
echo STEP 1: Backend Setup
echo ============================================
echo.

cd /d f:\Freelance\Hita_App\backend

if exist venv (
    echo Virtual environment already exists
) else (
    echo Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        color 0C
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

echo.
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
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Python dependencies installed

echo.
echo Checking .env file...
if exist .env (
    echo ✅ .env file already exists
    echo.
    echo 📝 IMPORTANT: Please verify these settings in .env:
    echo    - GEMINI_API_KEY (get from https://aistudio.google.com/)
    echo    - DB_USER and DB_PASSWORD match PostgreSQL setup
) else (
    echo Creating .env from template...
    copy .env.example .env
    echo ✅ .env created from template
    echo.
    echo 📝 IMPORTANT: Edit .env and add:
    echo    - GEMINI_API_KEY (get from https://aistudio.google.com/)
    echo    - Verify DB credentials
)

pause

echo.
echo ============================================
echo STEP 2: Database Setup
echo ============================================
echo.

echo Checking if PostgreSQL is running...
psql -U postgres -c "SELECT 1;" >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ PostgreSQL not running
    echo Please start PostgreSQL from Windows Services
    pause
    exit /b 1
)
echo ✅ PostgreSQL is running

echo.
echo Checking if 'hita' database exists...
psql -U postgres -lqt | findstr /C:" hita " >nul 2>&1
if %errorlevel% neq 0 (
    echo Creating 'hita' database...
    psql -U postgres -c "CREATE DATABASE hita;" >nul 2>&1
    if %errorlevel% neq 0 (
        color 0C
        echo ❌ Failed to create database
        pause
        exit /b 1
    )
    echo ✅ Database 'hita' created
) else (
    echo ✅ Database 'hita' already exists
)

echo.
echo Running migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Failed to run migrations
    pause
    exit /b 1
)
echo ✅ Migrations completed

pause

REM Setup Frontend
echo.
echo ============================================
echo STEP 3: Frontend Setup
echo ============================================
echo.

cd /d f:\Freelance\Hita_App\frontend

if exist node_modules (
    echo ✅ node_modules already exists
) else (
    echo Installing Node dependencies...
    call npm install
    if %errorlevel% neq 0 (
        color 0C
        echo ❌ Failed to install npm dependencies
        pause
        exit /b 1
    )
    echo ✅ npm dependencies installed
)

echo.
echo Checking .env.local file...
if exist .env.local (
    echo ✅ .env.local file already exists
) else (
    echo Creating .env.local from template...
    copy .env.local.example .env.local
    echo ✅ .env.local created
)

pause

REM Done
color 0A
cls
echo.
echo ============================================
echo ✅ SETUP COMPLETE!
echo ============================================
echo.
echo Now you need to start 4 services:
echo.
echo 📍 Terminal 1 - Backend:
echo    cd f:\Freelance\Hita_App\backend
echo    venv\Scripts\activate
echo    python manage.py runserver
echo.
echo 📍 Terminal 2 - Redis:
echo    redis-server
echo.
echo 📍 Terminal 3 - Celery Worker:
echo    cd f:\Freelance\Hita_App\backend
echo    venv\Scripts\activate
echo    celery -A hita_project worker --loglevel=info --pool=solo
echo.
echo 📍 Terminal 4 - Frontend:
echo    cd f:\Freelance\Hita_App\frontend
echo    npm run dev
echo.
echo 🌐 Then open: http://localhost:3000
echo.
echo 📚 For more info, see MANUAL_SETUP_WINDOWS.md
echo.
pause
