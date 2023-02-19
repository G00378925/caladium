@echo off
color 06
echo CALADIUM SETUP

rem Create the directory if it doesn't exist
mkdir "%ProgramFiles%\Caladium" 2>nul

rem Copy all in the current directory to the installation directory
tar -xzvf caladium.tar.gz -C "%ProgramFiles%\Caladium"

echo Attempt Auto Provisioning
"%ProgramFiles%\Caladium\caladium.exe" 20.166.76.162

pause