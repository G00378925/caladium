@echo off
pyinstaller --noconfirm caladium.spec
copy src\install.cmd build\caladium\install.cmd
cmd /C tar -zcvf build\caladium\caladium.tar.gz -C dist\caladium .
iexpress /N caladium.sed
