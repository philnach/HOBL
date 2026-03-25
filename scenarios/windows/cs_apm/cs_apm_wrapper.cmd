@echo off
setlocal enabledelayedexpansion
cls

rem %1 is the time to be in airplane mode
rem %2 is the path to executables on the DUT
rem %3 is whether to use RadioEnable.exe or airplanemode.exe
rem %4 is whether to use button.exe or external button pusher

set wifi_off_duration=%1
set dut_exec_path=%2
set /a button_delay=%wifi_off_duration% * 1000

echo Wifi off time (sec): %wifi_off_duration%
echo DUT Path: %dut_exec_path%
echo Button Delay: %button_delay%

if %3 == RadioEnable ( %dut_exec_path%\radio\RadioEnable.exe -Disable ) else ( %dut_exec_path%\radio\airplanemode.exe -Enable )
timeout 5 /nobreak

if %4 == SW ( %dut_exec_path%\button\button.exe -s %button_delay% ) else (%dut_exec_path%\sleep\sleep.exe %wifi_off_duration%)

if %3 == RadioEnable ( %dut_exec_path%\radio\RadioEnable.exe -Enable ) else ( %dut_exec_path%\radio\airplanemode.exe -Disable )


