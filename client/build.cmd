@echo off

rem Create build directory if it doesn't already exist
mkdir build  >nul 2>&1
mkdir build\caladium  >nul 2>&1

python scripts/create_install_cmd.py
pyinstaller --noconfirm caladium.spec

rem Copy files into build directory to be bundled
copy scripts\bootstrap.cmd build\caladium\bootstrap.cmd
copy scripts\gen_shortcut.vbs build\caladium\gen_shortcut.vbs

rem Bundle all the files into a tarball for the installation
tar -zcvf build\caladium\caladium.tar.gz -C dist\caladium .

rem Create the installer using iexpress
iexpress /N caladium.sed
