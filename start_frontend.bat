@echo off
REM Start Frontend Next.js Server
title Hita - Frontend (Port 3000)
color 0A

cd /d f:\Freelance\Hita_App\frontend

echo.
echo ============================================
echo  🪷 HITA - Frontend (Next.js)
echo ============================================
echo.

REM Check if node_modules exists
if not exist node_modules (
    color 0C
    echo ❌ Dependencies not installed!
    echo Running: npm install
    call npm install
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if .env.local exists
if not exist .env.local (
    echo Creating .env.local from template...
    copy .env.local.example .env.local
)

echo ✅ Dependencies ready
echo.
echo Starting Next.js development server...
echo.
echo 🌐 Frontend: http://localhost:3000
echo 📡 API URL: http://localhost:8000/api
echo.
echo 📝 Keep this terminal open
echo 🛑 Press Ctrl+C to stop
echo.

call npm run dev
