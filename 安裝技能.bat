@echo off
REM Install the wrap-up skill globally (Windows)
REM Double-click this file to install.
REM After installing, the "shou-gong" skill works in ALL projects,
REM not just this repo.

cd /d "%~dp0"

echo ======================================
echo  Install wrap-up skill (global)
echo ======================================
echo.

set "SRC=%~dp0.claude\skills\wrap-up"
set "DEST=%USERPROFILE%\.claude\skills\wrap-up"

if not exist "%SRC%\SKILL.md" (
    echo [ERROR] Source not found:
    echo    %SRC%
    echo.
    echo Please run "git pull" first, then try again.
    echo.
    pause
    exit /b 1
)

echo Source: %SRC%
echo Target: %DEST%
echo.

if exist "%DEST%\SKILL.md" (
    echo [INFO] An older version is already installed. It will be overwritten.
    echo.
)

if not exist "%USERPROFILE%\.claude\skills" mkdir "%USERPROFILE%\.claude\skills"

xcopy /E /I /Y "%SRC%" "%DEST%" >nul
if %errorlevel% neq 0 (
    echo [ERROR] Copy failed.
    echo.
    pause
    exit /b 1
)

echo [OK] Installed.
echo.
echo Restart Claude Code. The wrap-up skill now works in every
echo project, not just this one.
echo.
pause
