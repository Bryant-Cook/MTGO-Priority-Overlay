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

echo  Installing dependencies...
python -m pip install pynput --quiet
if %errorlevel% neq 0 (
    echo.
    echo  Failed to install dependencies. Check your internet connection
    echo  and run this installer again.
    pause
    exit /b 1
)

echo  Setting up auto-start...

:: Write a VBScript launcher so the overlay runs silently with no terminal window
set "SCRIPT=%~dp0mtgo_priority.py"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\mtgo_priority_overlay.vbs"

(
    echo Set sh = CreateObject^("WScript.Shell"^)
    echo sh.Run "pythonw """ ^& "%SCRIPT%" ^& """", 0, False
) > "%STARTUP%"

echo.
echo  Done! The overlay will now start automatically every time
echo  Windows starts.
echo.
echo  Starting the overlay now...
echo.
echo  The first time it runs, a setup window will appear.
echo  Follow the instructions to calibrate it for your screen.
echo.

start "" pythonw "%SCRIPT%"

echo  Setup complete. You can close this window.
echo.
pause
