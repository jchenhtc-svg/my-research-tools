@echo off
REM Swim Stroke Analyzer - one-time build script (run on Windows, by a
REM technical helper only). End users never need to run this - they just
REM get the resulting folder and double-click the .exe inside it.
REM
REM Requirements to RUN THIS SCRIPT (not needed by end users afterwards):
REM   - Python 3.10+ on PATH
REM   - Node.js + npm on PATH
REM
REM Output: dist\SwimStrokeAnalyzer\  (zip this whole folder to share it -
REM the .exe alone will not work, it needs the files next to it)

cd /d "%~dp0"

echo ======================================
echo  Building Swim Stroke Analyzer.exe
echo ======================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found on PATH. Install Python 3.10+ first.
    pause
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] npm not found on PATH. Install Node.js first.
    pause
    exit /b 1
)

echo [1/4] Building frontend...
pushd frontend
set REACT_APP_API_URL=/api
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] npm install failed.
    popd
    pause
    exit /b 1
)
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] npm run build failed.
    popd
    pause
    exit /b 1
)
popd
echo.

echo [2/4] Setting up Python build environment...
python -m venv .build-venv
call .build-venv\Scripts\activate.bat
pip install --upgrade pip >nul
pip install -r requirements.txt
pip install waitress pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)
echo.

echo [3/4] Running PyInstaller (this takes a few minutes)...
pyinstaller --noconfirm --clean ^
    --name SwimStrokeAnalyzer ^
    --add-data "backend;backend" ^
    --add-data "src;src" ^
    --add-data "frontend\build;frontend\build" ^
    --collect-data mediapipe ^
    --collect-all cv2 ^
    desktop_app.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PyInstaller build failed. See error above.
    echo Common fix: if it complains about a missing module, add
    echo   --hidden-import ^<module name^>
    echo to the pyinstaller command above and re-run this script.
    pause
    exit /b 1
)
echo.

echo [4/4] Done!
echo.
echo Output folder: dist\SwimStrokeAnalyzer\
echo Zip that whole folder and share it. End users just double-click
echo SwimStrokeAnalyzer.exe inside it - no Python/Node/Docker needed.
echo.
pause
