@echo off
setlocal

cd /d "%~dp0"

set "APPNAME=PRRI-Game"

for /f "tokens=2,*" %%A in (
    'reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop 2^>nul ^| find /i "Desktop"'
) do set "DESKTOP_RAW=%%B"

call set "DESKTOP_PATH=%DESKTOP_RAW%"
if not defined DESKTOP_PATH set "DESKTOP_PATH=%USERPROFILE%\Desktop"

set "DISTPATH=%DESKTOP_PATH%\%APPNAME%-Build"
set "PROJECT_ROOT=%cd%"
set "TEMP_WORK=%TEMP%\%APPNAME%_build"
set "TEMP_SPEC=%TEMP%\%APPNAME%_spec"

echo ========================================
echo   PyInstaller Windows Build Script
echo ========================================
echo.
echo Project folder:
echo %PROJECT_ROOT%
echo Output folder:
echo %DISTPATH%
echo.

echo Checking Python...
python --version >nul 2>nul
if errorlevel 1 (
    echo Python is not available on PATH.
    pause
    goto :eof
)

echo Checking required modules...
python -c "import pygame, PyInstaller; print('OK')" >nul 2>nul
if errorlevel 1 (
    echo.
    echo Installing/updating pygame and pyinstaller...
    python -m pip install --upgrade pip
    python -m pip install --upgrade pygame pyinstaller
    if errorlevel 1 (
        echo.
        echo Failed to install required modules.
        pause
        goto :eof
    )
)

if not exist "%DISTPATH%" mkdir "%DISTPATH%"

dir /b "%DISTPATH%" >nul 2>nul
if not errorlevel 1 (
    echo.
    choice /c YN /m "The build folder already contains files. Remove all contents first?"
    if errorlevel 2 (
        echo.
        echo Build cancelled.
        pause
        goto :eof
    )

    echo Clearing folder...
    del /f /q "%DISTPATH%\*" >nul 2>nul
    for /d %%D in ("%DISTPATH%\*") do rmdir /s /q "%%D"
)

if exist "%TEMP_WORK%" rmdir /s /q "%TEMP_WORK%"
if exist "%TEMP_SPEC%" rmdir /s /q "%TEMP_SPEC%"

echo.
echo Running PyInstaller...
python -m PyInstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "%APPNAME%" ^
    --distpath "%DISTPATH%" ^
    --workpath "%TEMP_WORK%" ^
    --specpath "%TEMP_SPEC%" ^
    --contents-directory "." ^
    --add-data "%PROJECT_ROOT%\assets;assets" ^
    --add-data "%PROJECT_ROOT%\resources;resources" ^
    "%PROJECT_ROOT%\main.py"

if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    goto :eof
)

echo.
echo Build finished successfully.
echo Zip and send this folder:
echo "%DISTPATH%\%APPNAME%"
echo.
start "" "%DISTPATH%\%APPNAME%"
pause