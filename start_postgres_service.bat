@echo off
REM Start PostgreSQL Service

title Starting PostgreSQL
color 0B

echo.
echo ============================================
echo  🪷 Starting PostgreSQL Service
echo ============================================
echo.

REM Try to start PostgreSQL service
echo Attempting to start PostgreSQL service...
echo.

REM Method 1: Using net start (most common)
net start postgresql-x64-16 2>nul
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL started successfully
    goto :verify
)

REM Method 2: Try alternate service name
net start "postgresql-x64-16" 2>nul
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL started successfully
    goto :verify
)

REM Method 3: Try generic postgresql name
net start postgresql 2>nul
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL started successfully
    goto :verify
)

REM If all methods failed
color 0C
echo ❌ Could not start PostgreSQL service
echo.
echo Possible solutions:
echo.
echo 1. Check Windows Services (services.msc)
echo    Find: postgresql-x64-16
echo    Right-click ^> Start
echo.
echo 2. PostgreSQL not installed
echo    Download: https://www.postgresql.org/download/windows/
echo.
echo 3. Service has different name
echo    Run "services.msc" and look for PostgreSQL
echo.
pause
exit /b 1

:verify
echo.
echo Waiting for PostgreSQL to initialize...
timeout /t 3
echo.
echo Verifying connection...
psql -U postgres -c "SELECT version();" >nul 2>nul
if %errorlevel% equ 0 (
    color 0B
    echo ✅ PostgreSQL is running and responding!
    echo.
    echo Ready to setup database.
    echo.
    echo Next: Run complete_setup.bat
) else (
    color 0E
    echo ⚠️  PostgreSQL started but not responding yet
    echo.
    echo Wait 10 seconds and try again:
    echo   psql -U postgres -c "SELECT version();"
)
echo.
pause
