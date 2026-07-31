@echo off
REM 自由式划水分析 - 現地啟動腳本（Windows）
REM 雙擊這個檔案即可啟動

cd /d "%~dp0"

echo ======================================
echo  自由式划水分析 - 正在啟動...
echo ======================================
echo.

where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Docker，請先安裝 Docker Desktop：
    echo    https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

docker compose up --build -d

echo.
echo 啟動完成！
echo.
echo 請打開瀏覽器輸入以下網址開始使用：
echo    http://localhost:8080
echo.
echo （第一次啟動需要幾分鐘下載/建置，之後會快很多）
echo.

timeout /t 2 >nul
start http://localhost:8080

echo 要關閉服務，請執行同目錄下的「關閉.bat」
pause
