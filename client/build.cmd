@echo off
python scripts/create_install_cmd.py
pyinstaller --noconfirm caladium.spec

copy scripts\bootstrap.cmd build\caladium\bootstrap.cmd
copy scripts\gen_shortcut.vbs build\caladium\gen_shortcut.vbs
rem copy scripts\install.cmd build\caladium\install.cmd

tar -zcvf build\caladium\caladium.tar.gz -C dist\caladium .
iexpress /N caladium.sed
