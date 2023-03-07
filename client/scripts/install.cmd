@echo off
color 06
echo Caladium Setup

rem Exit if not running as administrator
net session >nul 2>&1
if %errorlevel% == 0 (
    call :admin
) else (
    echo Caladium installer must be run as administrator
    pause
    exit /b
)
:admin

rem Delete files of last caladium installation
rd /s /q "%ProgramFiles%\Caladium" 2>nul

rem Create the directory if it doesn't exist
mkdir "%ProgramFiles%\Caladium" 2>nul

rem Copy all in the current directory to the installation directory
tar -xzvf caladium.tar.gz -C "%ProgramFiles%\Caladium"

rem Create a shortcut on the desktop
cscript /Nologo gen_shortcut.vbs

echo Attempt Auto Provisioning
"%ProgramFiles%\Caladium\caladium.exe" {0}

del install.cmd
