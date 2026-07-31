@echo off
chcp 65001 >nul
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
    echo.
    pause
    exit /b 1
)

echo 檢查 Docker Desktop 是否已啟動...
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [錯誤] Docker 指令找得到，但 Docker Desktop 應用程式還沒開啟或還在初始化。
    echo 請先手動打開 Docker Desktop，等到左下角/工作列的鯨魚圖示變成「Running」
    echo （通常要等10-30秒），再重新雙擊這個檔案一次。
    echo.
    pause
    exit /b 1
)

echo Docker 已就緒，開始建置（第一次會花幾分鐘，請耐心等待）...
echo.

docker compose up --build -d
if %errorlevel% neq 0 (
    echo.
    echo [錯誤] 啟動失敗，請把上面的錯誤訊息截圖回報。
    echo.
    pause
    exit /b 1
)

echo.
echo 啟動完成！
echo.
echo 請打開瀏覽器輸入以下網址開始使用：
echo    http://localhost:8080
echo.

timeout /t 2 >nul
start http://localhost:8080

echo 要關閉服務，請執行同目錄下的「關閉.bat」
echo.
pause
