@echo off
REM Complete Hita Setup - All Systems

title Hita - Complete Setup
color 0B

echo.
echo ============================================
echo  🪷 HITA - Complete System Setup
echo ============================================
echo.

cd /d f:\Freelance\Hita_App

REM Check PostgreSQL
echo Checking PostgreSQL...
psql -U postgres -c "SELECT version();" >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL is running
) else (
    color 0C
    echo ❌ PostgreSQL is NOT running!
    echo.
    echo Solution: Start PostgreSQL service
    echo   Services ^> PostgreSQL ^> Start
    echo.
    echo Or use pgAdmin to start it
    pause
    exit /b 1
)
echo.

REM Setup Database
echo Setting up database...
psql -U postgres -c "CREATE DATABASE hita;" 2>nul
psql -U postgres -c "CREATE USER hita WITH PASSWORD 'hita123';" 2>nul
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE hita TO hita;" 2>nul
psql -U postgres -d hita -c "CREATE EXTENSION IF NOT EXISTS pgvector;" 2>nul
echo ✅ Database configured
echo.

REM Run migrations
echo Running Django migrations...
cd backend
call venv\Scripts\activate.bat
python manage.py migrate
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Migrations failed
    pause
    exit /b 1
)
echo ✅ Migrations complete
echo.

color 0B
echo ============================================
echo  ✅ All Setup Complete!
echo ============================================
echo.
echo ✅ PostgreSQL - Running
echo ✅ Backend - Ready (venv activated)
echo ✅ Database - Migrated
echo.
echo Next: Start all services
echo.
echo Terminal 1: redis-server
echo Terminal 2: python manage.py runserver 0.0.0.0:8000
echo Terminal 3: (frontend already running)
echo.
echo Then go to http://localhost:3000 and test!
echo.
pause
