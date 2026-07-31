@echo off
REM Swim Stroke Analyzer - local start script (Windows)
REM Double-click this file to start.

cd /d "%~dp0"

echo ======================================
echo  Swim Stroke Analyzer - starting...
echo ======================================
echo.

where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker not found. Please install Docker Desktop first:
    echo    https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

echo Checking if Docker Desktop is running...
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Docker command found, but Docker Desktop app is not running yet.
    echo Please open Docker Desktop manually and wait until the whale icon in the
    echo taskbar shows "Running" ^(usually 10-30 seconds^), then double-click this
    echo file again.
    echo.
    pause
    exit /b 1
)

echo Docker is ready. Building now ^(first run takes a few minutes, please wait^)...
echo.

docker compose up --build -d
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Startup failed. Please screenshot the error above and send it back.
    echo.
    pause
    exit /b 1
)

echo.
echo Done! Startup complete.
echo.
echo Open your browser and go to:
echo    http://localhost:8080
echo.

timeout /t 2 >nul
start http://localhost:8080

echo To stop the service, double-click the other .bat file in this folder.
echo.
pause
