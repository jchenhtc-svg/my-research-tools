@echo off
REM Install this repo's skills globally (Windows)
REM Double-click this file to install.
REM After installing, the skills work in ALL projects, not just this repo.
REM
REM Skills installed:
REM   wrap-up              say "shou-gong" to sync all three homes
REM   baseline-ui          /baseline-ui <file> to review UI quality
REM   fixing-accessibility /fixing-accessibility <file> to review a11y

cd /d "%~dp0"

set "SKILLS=wrap-up baseline-ui fixing-accessibility"
set "SRC_DIR=%~dp0.claude\skills"
set "DEST_DIR=%USERPROFILE%\.claude\skills"

echo ======================================
echo  Install skills (global)
echo ======================================
echo.

REM Check every source first, so we never install only half of them.
set "MISSING="
for %%S in (%SKILLS%) do (
    if not exist "%SRC_DIR%\%%S\SKILL.md" (
        echo [ERROR] Source not found: %SRC_DIR%\%%S\SKILL.md
        set "MISSING=1"
    )
)

if defined MISSING (
    echo.
    echo Please run "git pull" first, then try again.
    echo.
    pause
    exit /b 1
)

echo Source: %SRC_DIR%
echo Target: %DEST_DIR%
echo.

if not exist "%DEST_DIR%" mkdir "%DEST_DIR%"

for %%S in (%SKILLS%) do (
    if exist "%DEST_DIR%\%%S\SKILL.md" (
        echo   %%S [older version found, overwriting]
    ) else (
        echo   %%S
    )
    xcopy /E /I /Y "%SRC_DIR%\%%S" "%DEST_DIR%\%%S" >nul
    if errorlevel 1 (
        echo [ERROR] Copy failed for %%S.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo [OK] Installed.
echo.
echo Restart Claude Code. In every project you can now:
echo   - say "shou-gong" to sync all three homes
echo   - /baseline-ui ^<file^>          review UI quality
echo   - /fixing-accessibility ^<file^> review accessibility
echo.
pause
