@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul

if not exist "%~dp0venv\Scripts\python.exe" (
    echo [ERROR] venv not found. Please check python environment.
    pause
    exit /b 1
)

"%~dp0venv\Scripts\python.exe" "%~dp0verify_one.py" %*

if "%~1"=="" (
    pause
)
