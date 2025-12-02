@echo off
setlocal ENABLEDELAYEDEXPANSION

echo ============================================================
echo   ZipAndHash - Installation Script  (Windows)
echo ============================================================

REM Check Python availability
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Optional: create venv
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing project...
pip install .

if errorlevel 1 (
    echo [ERROR] Installation failed.
    pause
    exit /b 1
)

echo ------------------------------------------------------------
echo Installation completed successfully.
echo ------------------------------------------------------------

call zah -h

pause
endlocal
