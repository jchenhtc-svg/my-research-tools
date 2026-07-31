@echo off
REM Swim Stroke Analyzer - stop service (Windows)
cd /d "%~dp0"
docker compose down
echo.
echo Stopped.
pause
