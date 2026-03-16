@echo off
REM Install Redis for Windows

echo.
echo ============================================
echo  Installing Redis for Windows
echo ============================================
echo.

REM Check if chocolatey is installed
where choco >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Chocolatey (Windows package manager)...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.ServicePointManager).SecurityProtocol = 3072; iex(New-Object Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
    if %errorlevel% neq 0 (
        echo.
        echo ❌ Failed to install Chocolatey
        echo.
        echo Manual Installation:
        echo 1. Visit: https://github.com/microsoftarchive/redis/releases
        echo 2. Download: Redis-x64-latest.zip
        echo 3. Extract to: C:\Redis
        echo 4. Run: C:\Redis\redis-server.exe
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Installing Redis via Chocolatey...
choco install redis-64 -y

echo.
echo ✅ Redis installed!
echo.
echo Starting Redis...
redis-server

pause
