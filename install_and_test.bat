@echo off
setlocal ENABLEDELAYEDEXPANSION

echo ============================================================
echo   ZipAndHash - Installation and Test Script (Windows)
echo ============================================================

REM ----------------------------------------------------------------
REM 1) Check Python availability
REM ----------------------------------------------------------------
python --version >nul 2>&1
if errorlevel 1 goto no_python

REM ----------------------------------------------------------------
REM 2) Create venv if missing
REM ----------------------------------------------------------------
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 goto error
)

REM ----------------------------------------------------------------
REM 3) Activate venv
REM ----------------------------------------------------------------
call venv\Scripts\activate.bat
if errorlevel 1 goto error

REM ----------------------------------------------------------------
REM 4) Upgrade pip
REM ----------------------------------------------------------------
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 goto error

REM ----------------------------------------------------------------
REM 5) Install project with test extras
REM     (change [test] if your extra has a different name)
REM ----------------------------------------------------------------
echo Installing project with test extras...
pip install .[test]
if errorlevel 1 goto error

REM ----------------------------------------------------------------
REM 6) Run tests with coverage
REM ----------------------------------------------------------------
echo Running tests with coverage...
pytest --cov=zah --cov-report=term-missing --cov-fail-under=100
if errorlevel 1 goto error

echo ------------------------------------------------------------
echo Installation and tests completed successfully.
echo ------------------------------------------------------------
call zah -h
goto end

:no_python
echo [ERROR] Python is not installed or not in PATH.
goto end

:error
echo.
echo [ERROR] Something went wrong during install or tests.
echo Check the messages above for details.

:end
echo.
pause
endlocal
