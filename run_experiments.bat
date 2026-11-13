@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run run_windows.bat first to create the Python environment.
  pause
  exit /b 1
)
set "PY=.venv\Scripts\python.exe"
%PY% -m unittest discover -s tests -v
if errorlevel 1 goto fail
%PY% benchmark.py --all
if errorlevel 1 goto fail
%PY% benchmark.py --tactical
if errorlevel 1 goto fail
%PY% benchmark.py --tournament
if errorlevel 1 goto fail
echo.
echo ALL TESTS AND EXPERIMENTS COMPLETED.
pause
exit /b 0
:fail
echo.
echo An experiment failed. Review the error above.
pause
exit /b 1
