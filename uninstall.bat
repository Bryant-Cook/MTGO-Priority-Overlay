@echo off
title MTGO Priority Overlay - Uninstaller

echo.
echo  MTGO Priority Overlay - Uninstaller
echo  =====================================
echo.

:: Stop the running overlay
taskkill /F /IM pythonw.exe >nul 2>&1

:: Remove the scheduled task
schtasks /End /TN "MTGOPriorityOverlay" >nul 2>&1
schtasks /Delete /TN "MTGOPriorityOverlay" /F >nul 2>&1
echo  Removed auto-start entry.

echo.
echo  Uninstall complete. The overlay will no longer start with Windows.
echo.
pause
