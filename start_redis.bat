@echo off
REM Start Redis - with fallback options for Windows

title Hita - Redis Cache (Port 6379)
color 0A

echo.
echo ============================================
echo  🪷 HITA - Redis Cache
echo ============================================
echo.

REM Try common Redis installations
if exist "C:\Program Files\Redis\redis-server.exe" (
    echo ✅ Found Redis at: C:\Program Files\Redis
    "C:\Program Files\Redis\redis-server.exe"
    exit /b 0
)

if exist "C:\Redis\redis-server.exe" (
    echo ✅ Found Redis at: C:\Redis
    "C:\Redis\redis-server.exe"
    exit /b 0
)

if exist "%CHOCOLATEYINSTALL%\bin\redis-server.exe" (
    echo ✅ Found Redis at: %CHOCOLATEYINSTALL%\bin
    "%CHOCOLATEYINSTALL%\bin\redis-server.exe"
    exit /b 0
)

REM Try to find redis-server in PATH
where redis-server >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Found Redis in PATH
    redis-server
    exit /b 0
)

REM Redis not found - show installation options
color 0C
echo.
echo ❌ Redis not found!
echo.
echo ==================== INSTALL REDIS ====================
echo.
echo Option 1: Using Chocolatey (Easiest)
echo   Run in PowerShell as Administrator:
echo   choco install redis-64 -y
echo.
echo Option 2: Manual Installation
echo   1. Visit: https://github.com/microsoftarchive/redis/releases
echo   2. Download: Redis-x64-latest.zip or msi installer
echo   3. Extract or Install to: C:\Redis or C:\Program Files\Redis
echo   4. Add to PATH
echo.
echo Option 3: Use Docker (if Docker is installed)
echo   docker run -d -p 6379:6379 redis
echo.
echo =========================================================
echo.
echo Once Redis is installed, run this script again:
echo   start_redis.bat
echo.
pause
exit /b 1
