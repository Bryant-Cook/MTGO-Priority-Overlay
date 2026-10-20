@echo off
title MTGO Priority Overlay - Installer

echo.
echo  MTGO Priority Overlay
echo  =====================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python is not installed.
    echo.
    echo  Please download and install Python from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: On the installer screen, check the box that says
    echo  "Add Python to PATH" before clicking Install Now.
    echo.
    echo  After installing Python, run this installer again.
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Locate pythonw.exe (runs without a terminal window)
for /f "tokens=*" %%i in ('where pythonw 2^>nul') do (
    if not defined PYTHONW set "PYTHONW=%%i"
)
if not defined PYTHONW (
    echo  Could not find pythonw.exe. Make sure Python is added to PATH.
    pause
    exit /b 1
)

echo  Installing dependencies...
python -m pip install mss --quiet
if %errorlevel% neq 0 (
    echo.
    echo  Failed to install dependencies. Check your internet connection
    echo  and run this installer again.
    pause
    exit /b 1
)

echo  Setting up auto-start...
set "SCRIPT=%~dp0mtgo_priority.py"

:: Remove any previous task before creating a fresh one
schtasks /Delete /TN "MTGOPriorityOverlay" /F >nul 2>&1

schtasks /Create /TN "MTGOPriorityOverlay" /TR "\"%PYTHONW%\" \"%SCRIPT%\"" /SC ONLOGON /RU "%USERNAME%" /RL HIGHEST /F >nul
if %errorlevel% neq 0 (
    echo.
    echo  Failed to create the startup task. Try running this installer
    echo  as Administrator (right-click install.bat, Run as administrator).
    pause
    exit /b 1
)

echo.
echo  Done! The overlay will start automatically every time Windows starts.
echo.
echo  Starting the overlay now...
start "" "%PYTHONW%" "%SCRIPT%"

echo.
echo  Setup complete. You can close this window.
echo.
pause
