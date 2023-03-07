@echo off

rem This will execute install.cmd if it exists
if exist "install.cmd" (
    install.cmd
) else (
    exit /b
)
