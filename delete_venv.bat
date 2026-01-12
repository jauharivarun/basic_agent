@echo off
REM This script will delete .venv on the next system reboot
echo Adding .venv to deletion queue for next reboot...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager" /v PendingFileRenameOperations /t REG_MULTI_SZ /d "\??\C:\Users\vnjau\my_first_project\.venv" /f >nul 2>&1
if %errorlevel% equ 0 (
    echo .venv will be deleted on next reboot.
    echo You can restart your computer now, or try manual deletion.
) else (
    echo Failed to add to deletion queue. Try manual deletion instead.
)
pause
