@echo off
title MTGO Priority Overlay - Uninstaller

echo.
echo  MTGO Priority Overlay - Uninstaller
echo  =====================================
echo.

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\mtgo_priority_overlay.vbs"
set "CONFIG=%USERPROFILE%\.mtgo_priority_config.json"

if exist "%STARTUP%" (
    del "%STARTUP%"
    echo  Removed auto-start entry.
) else (
    echo  No auto-start entry found.
)

if exist "%CONFIG%" (
    del "%CONFIG%"
    echo  Removed saved calibration.
)

echo.
echo  Uninstall complete. The overlay will no longer start with Windows.
echo.
pause
