@echo off
setlocal

cd /d "%~dp0"

set "APPNAME=PRRI-Game"

echo ========================================
echo   PyInstaller Windows Build Script
echo ========================================
echo.

echo Checking PyInstaller...
pyinstaller.exe --version >nul 2>nul
if errorlevel 1 (
    echo PyInstaller is not installed or not available on PATH.
    choice /c YN /m "Install PyInstaller now?"
    if errorlevel 2 (
        echo.
        echo Installation declined. Exiting.
        pause
        goto :eof
    )

    echo.
    echo Installing PyInstaller with pip...
    py -m pip install -U pyinstaller
    if errorlevel 1 (
        echo.
        echo Failed to install PyInstaller.
        pause
        goto :eof
    )
)

echo.
echo Project folder:
echo %cd%
echo.

set /p DISTPATH=Enter output folder for the build: 
if "%DISTPATH%"=="" (
    echo.
    echo No path entered.
    pause
    goto :eof
)

if not exist "%DISTPATH%" mkdir "%DISTPATH%"

dir /b "%DISTPATH%" >nul 2>nul
if not errorlevel 1 (
    echo.
    choice /c YN /m "The folder is not empty. Remove all contents first?"
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

echo.
echo Running PyInstaller...
pyinstaller.exe --name "%APPNAME%" --onedir --windowed --distpath "%DISTPATH%" --add-data "assets;assets" --add-data "resources;resources" main.py

if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    goto :eof
)

echo.
echo Build finished successfully.
echo Opening built folder...
start "" "%DISTPATH%\%APPNAME%"
pause