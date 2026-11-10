@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 (
    python -m venv .venv
    if errorlevel 1 exit /b 1
  )
)
.venv\Scripts\python.exe -c "import pygame" >nul 2>&1
if errorlevel 1 (
  .venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
  if errorlevel 1 (
    echo Pygame install failed. Check Python version and network.
    pause
    exit /b 1
  )
)
.venv\Scripts\python.exe main.py
if errorlevel 1 pause
