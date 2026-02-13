@echo off
setlocal

REM --------------------------------------------------------------
REM Copy and edit this file to make your own executable
REM --------------------------------------------------------------

echo ============================================================
echo   ZipAndHash - Runner (Windows)
echo ============================================================

REM Activate the virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Could not activate venv.
    pause
    exit /b 1
)

REM --------------------------------------------------------------
REM Modify parameters below as needed
REM --------------------------------------------------------------

set SRC=J:\Laboratorio-1
set DST=K:\
set CPY=G:\Drive condivisi\Archivio Verifiche e Griglie - Dipartimento di Informatica

REM Optional parameters (modify or delete if unused)
set OPTIONS=--mv --sub --cpy "%CPY%" --fzip --fcpy

echo Running:
echo     zah %SRC% %DST% %OPTIONS%
echo --------------------------------------------------------------

zah "%SRC%" "%DST%" %OPTIONS%

echo --------------------------------------------------------------
echo Execution finished.
pause
endlocal
