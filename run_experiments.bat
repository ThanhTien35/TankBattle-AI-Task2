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
%PY% -m benchmarks.compare --suite maps --depths 2 3 4 --repeats 5 --output results/maps_depths234.csv
if errorlevel 1 goto fail
%PY% -m benchmarks.compare --suite tactical --depth 3 --repeats 5 --output results/tactical_depth3.csv
if errorlevel 1 goto fail
%PY% -m benchmarks.tournament --suite maps --depth 2 --rounds 2 --max-plies 60 --output results/tournament.csv --summary-output results/tournament_summary.csv
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
