@echo off
setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"

if not exist "%~dp0upload_to_serv00.py" (
  echo ERROR: upload_to_serv00.py was not found next to this BAT file.
  echo Put both files in the same folder, then run this BAT again.
  echo.
  pause
  exit /b 2
)

:RUN_TOOL
where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python was not found in PATH.
  echo Install Python or add python.exe to PATH, then run this BAT again.
  echo.
  pause
  exit /b 2
)

python -u "%~dp0upload_to_serv00.py" %*
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if not "%EXIT_CODE%"=="0" echo ERROR: Sync tool exited with code %EXIT_CODE%.

if not "%~1"=="" (
  pause
  exit /b %EXIT_CODE%
)

echo Press any key to return to the operation menu.
pause >nul
goto RUN_TOOL
