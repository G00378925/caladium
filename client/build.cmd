@echo off
pyinstaller --noconfirm caladium.spec
copy src\bootstrap.cmd build\caladium\bootstrap.cmd
copy src\install.cmd build\caladium\install.cmd
tar -zcvf build\caladium\caladium.tar.gz -C dist\caladium .
iexpress /N caladium.sed
