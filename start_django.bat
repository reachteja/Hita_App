@echo off
REM Start Django Backend - All Dependencies Installed

title Hita - Django Backend (Port 8000)
color 0B

cd /d f:\Freelance\Hita_App\backend

echo.
echo ============================================
echo  🪷 HITA - Django Backend Server
echo ============================================
echo.
echo ✅ All dependencies installed
echo.

REM Activate venv
call venv\Scripts\activate.bat

echo Starting Django development server...
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📊 API Endpoints: http://localhost:8000/api/
echo 🗄️  Admin: http://localhost:8000/admin
echo.
echo 📝 Keep this window open
echo 🛑 Press Ctrl+C to stop
echo.

python manage.py runserver 0.0.0.0:8000
