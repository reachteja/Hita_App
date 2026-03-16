@echo off
REM Master startup script - Launches all 4 Hita services
REM Run this ONE time and it will open 4 new windows

echo.
echo ============================================
echo  🪷 HITA - Master Startup Script
echo ============================================
echo.
echo Launching all services...
echo.

cd /d f:\Freelance\Hita_App

REM Launch each service in a new window
start "HITA - Redis Cache (Port 6379)" cmd /k start_redis.bat
timeout /t 2

start "HITA - Django Backend (Port 8000)" cmd /k start_backend.bat
timeout /t 2

start "HITA - Celery Worker" cmd /k start_celery.bat
timeout /t 2

start "HITA - Frontend (Port 3000)" cmd /k start_frontend.bat

echo.
echo ✅ All services launching...
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000/api
echo 📍 Redis: localhost:6379
echo.
echo 📝 4 new windows have opened
echo 🛑 Keep all windows open to run Hita
echo.
echo Next steps:
echo 1. Wait 30 seconds for all services to initialize
echo 2. Open browser: http://localhost:3000
echo 3. Sign up with email and password
echo 4. Upload a document
echo 5. Ask a question!
echo.
pause
