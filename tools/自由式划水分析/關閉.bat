@echo off
chcp 65001 >nul
REM 自由式划水分析 - 關閉服務（Windows）
cd /d "%~dp0"
docker compose down
echo.
echo 已關閉。
pause
