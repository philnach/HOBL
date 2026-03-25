@echo off
setlocal enabledelayedexpansion

:: Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR - This script must be run as Administrator.
    exit /b 1
)

:: Validate argument
if "%~1"=="" (
    echo Usage: configure_ram.cmd ^<RAM_SIZE_MB^>
    echo.
    echo   RAM_SIZE_MB  - Desired RAM size in megabytes ^(e.g., 4096 for 4 GB^)
    echo                  Use 0 to remove the RAM limit and restore full memory.
    echo.
    echo Examples:
    echo   configure_ram.cmd 4096    - Limit RAM to 4 GB
    echo   configure_ram.cmd 8192    - Limit RAM to 8 GB
    echo   configure_ram.cmd 0       - Remove RAM limit
    exit /b 1
)

set "RAM_MB=%~1"

:: Validate that the argument is a non-negative integer
for /f "delims=0123456789" %%a in ("%RAM_MB%") do (
    echo  ERROR - Invalid RAM size "%RAM_MB%". Please provide a non-negative integer in MB.
    exit /b 1
)

if "%RAM_MB%"=="0" (
    echo Removing RAM limit...
    bcdedit /deletevalue {current} truncatememory >nul 2>&1
    if !errorlevel! neq 0 (
        echo No RAM limit was set. Nothing to remove.
    ) else (
        echo RAM limit removed. Full memory will be available after reboot.
    )
) else (
    :: Convert MB to bytes using PowerShell for 64-bit arithmetic
    for /f %%v in ('powershell -NoProfile -Command "[uint64]%RAM_MB% * 1048576"') do set "RAM_BYTES=%%v"
    if not defined RAM_BYTES (
        echo  ERROR - Failed to compute byte value for %RAM_MB% MB.
        exit /b 1
    )
    echo Configuring RAM limit to %RAM_MB% MB ^(!RAM_BYTES! bytes^)...
    bcdedit /set {current} truncatememory !RAM_BYTES!
    if !errorlevel! neq 0 (
        echo  ERROR - bcdedit command failed.
        exit /b 1
    )
    echo RAM limit set to %RAM_MB% MB successfully.
)

echo.
echo A reboot is required for the change to take effect.
set /p "REBOOT=Do you want to reboot now? (Y/N): "
if /i "!REBOOT!"=="Y" (
    shutdown /r /t 0
)
endlocal
exit /b 0
