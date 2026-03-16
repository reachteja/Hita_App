@echo off
REM PostgreSQL Database Setup for Hita

title Hita - PostgreSQL Setup
color 0B

echo.
echo ============================================
echo  🪷 HITA - PostgreSQL Database Setup
echo ============================================
echo.

REM Check if psql is available
psql --version >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo ❌ PostgreSQL not found!
    echo.
    echo Install PostgreSQL first:
    echo https://www.postgresql.org/download/windows/
    echo.
    pause
    exit /b 1
)

echo ✅ PostgreSQL found
psql --version
echo.

REM Create database
echo Creating database 'hita'...
psql -U postgres -c "CREATE DATABASE hita;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Database created
) else (
    echo ⚠️  Database may already exist
)
echo.

REM Create user
echo Creating user 'hita'...
psql -U postgres -c "CREATE USER hita WITH PASSWORD 'hita123';" 2>nul
if %errorlevel% equ 0 (
    echo ✅ User created
) else (
    echo ⚠️  User may already exist
)
echo.

REM Grant privileges
echo Granting privileges...
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE hita TO hita;" 2>nul
echo ✅ Privileges granted
echo.

REM Create pgvector extension
echo Installing pgvector extension...
psql -U postgres -d hita -c "CREATE EXTENSION IF NOT EXISTS pgvector;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ pgvector extension created
) else (
    echo ⚠️  pgvector may not be installed
    echo    You may need to install: https://github.com/pgvector/pgvector
)
echo.

echo ============================================
echo  ✅ Database Setup Complete!
echo ============================================
echo.
echo Database: hita
echo User: hita
echo Password: hita123
echo Host: localhost
echo Port: 5432
echo.
echo Next: Run migrations
echo   cd f:\Freelance\Hita_App\backend
echo   call venv\Scripts\activate.bat
echo   python manage.py migrate
echo.
pause
