@echo off
REM PostgreSQL 16 Installation Guide - Interactive

title PostgreSQL 16 Installation Helper
color 0B

echo.
echo ============================================
echo  🪷 PostgreSQL 16 Installation Helper
echo ============================================
echo.
echo psql command NOT FOUND - PostgreSQL is not installed
echo.
echo This script will guide you through installation
echo.

echo Step 1: Download PostgreSQL 16
echo ================================
echo.
echo Open this link in your browser:
echo https://www.postgresql.org/download/windows/
echo.
echo Then:
echo 1. Click "Download the installer"
echo 2. Download "PostgreSQL 16" (latest stable)
echo 3. Run the downloaded .exe file
echo.

echo Step 2: Installation Wizard
echo ===========================
echo.
echo When the installer opens:
echo - Installation directory: C:\Program Files\PostgreSQL\16 (default - OK)
echo - Port: 5432 (default - OK)
echo - Locale: English, United States (default - OK)
echo.
echo IMPORTANT - Superuser Password:
echo   Password: qwerty123
echo   Confirm:  qwerty123
echo.
echo Click "Next" through all screens, then "Install"
echo.

echo Step 3: Verify Installation
echo ===========================
echo.
echo After installation, open Command Prompt and run:
echo   psql --version
echo.
echo Should show: psql (PostgreSQL) 16.x
echo.

echo ============================================
echo.
pause /prompt "Press any key to continue after PostgreSQL is installed..."

echo.
echo Checking PostgreSQL installation...
echo.

psql --version >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL found!
    psql --version
    echo.
    echo Next steps:
    echo 1. Run these commands to setup database:
    echo.
    echo    psql -U postgres -c "CREATE DATABASE hita;"
    echo    psql -U postgres -c "CREATE USER hita WITH PASSWORD 'hita123';"
    echo    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE hita TO hita;"
    echo    psql -U postgres -d hita -c "CREATE EXTENSION pgvector;"
    echo.
) else (
    color 0C
    echo ❌ PostgreSQL still not found!
    echo.
    echo Possible reasons:
    echo 1. Installation not complete - restart computer?
    echo 2. Not in PATH - add C:\Program Files\PostgreSQL\16\bin to PATH
    echo 3. Different installation location
    echo.
    echo Try running:
    echo   "C:\Program Files\PostgreSQL\16\bin\psql" --version
    echo.
)

pause
