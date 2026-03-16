@echo off
REM Troubleshoot Hita services

title Hita - Service Troubleshooting
color 0A

echo.
echo ============================================
echo  🪷 HITA - Service Troubleshooting
echo ============================================
echo.

echo Checking services...
echo.

REM Check Redis
echo Checking Redis (Port 6379)...
netstat -ano | findstr ":6379" >nul
if %errorlevel% equ 0 (
    echo ✅ Redis is running on port 6379
) else (
    echo ❌ Redis is NOT running
    echo    Solution: Start Redis manually
    echo    Command: redis-server
)
echo.

REM Check Django
echo Checking Django Backend (Port 8000)...
netstat -ano | findstr ":8000" >nul
if %errorlevel% equ 0 (
    echo ✅ Django is running on port 8000
) else (
    echo ❌ Django is NOT running on port 8000
    echo    Solution: Start Django manually
    echo    Command: cd backend ^&^& python manage.py runserver 0.0.0.0:8000
)
echo.

REM Check Frontend
echo Checking Next.js Frontend (Port 3000)...
netstat -ano | findstr ":3000" >nul
if %errorlevel% equ 0 (
    echo ✅ Next.js is running on port 3000
) else (
    echo ❌ Next.js is NOT running
    echo    Solution: Start Frontend manually
    echo    Command: cd frontend ^&^& npm run dev
)
echo.

echo ============================================
echo.
echo 🔧 To Fix Network Error:
echo.
echo 1. Open 3 NEW command prompts
echo.
echo 2. In Terminal 1 (Redis):
echo    redis-server
echo.
echo 3. In Terminal 2 (Django Backend):
echo    cd f:\Freelance\Hita_App\backend
echo    python manage.py runserver 0.0.0.0:8000
echo.
echo 4. In Terminal 3 (Frontend):
echo    cd f:\Freelance\Hita_App\frontend
echo    npm run dev
echo.
echo 5. Refresh browser at http://localhost:3000
echo.
echo ============================================
echo.
pause
