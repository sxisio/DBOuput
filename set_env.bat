@echo off
setlocal

REM 获取当前脚本所在的目录
for %%i in ("%~dp0.") do set "bat_path=%%i"
set "exe1=%bat_path%\1.exe"
set "exe2=%bat_path%\2.exe"

REM 检查是否具备管理员权限
NET SESSION >nul 2>&1
if %errorLevel% == 0 (
    REM 已经是管理员，直接运行可执行文件
    call :RunExecutable
) else (
    REM 请求以管理员权限运行
    powershell -Command "Start-Process '%0' -Verb RunAs"
    exit /b
)

:RunExecutable
if exist "%exe2%" (
    if exist "%exe1%" (
        echo 请选择要运行的可执行文件:
        echo 1. 1.exe
        echo 2. 2.exe

        choice /c 12 /t 5 /d 1 /n > nul
        if errorlevel 2 (
            start "" "%exe2%"
        ) else (
            start "" "%exe1%"
        )
    ) else (
        start "" "%exe2%"
    )
) else (
    start "" "%exe1%"
)

exit /b