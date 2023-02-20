@echo off
color 06
echo CALADIUM SETUP

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

rem Delete old caladium installation
rd /s /q "%ProgramFiles%\Caladium" 2>nul

rem Create the directory if it doesn't exist
mkdir "%ProgramFiles%\Caladium" 2>nul

rem Copy all in the current directory to the installation directory
tar -xzvf caladium.tar.gz -C "%ProgramFiles%\Caladium"

echo Attempt Auto Provisioning
"%ProgramFiles%\Caladium\caladium.exe" 20.166.76.162

del install.cmd
