@echo off
setlocal
cd /d %~dp0
set whl_file=%cd%\PyMySQL-1.1.0-py3-none-any.whl
pip install %whl_file%
endlocal