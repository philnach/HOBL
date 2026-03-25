@echo off
cls
echo Airplane Mode Enabled time (sec): %1
echo Arg1: %1
echo Arg2: %2
echo Arg3: %3
echo Arg4: %4
echo Arg5: %5
echo Arg6: %6
echo Arg7: %7
echo Arg8: %8
echo Arg9: %9

set config_str=%4 %5 %6 %7 %8 %9
rem set config_str=%config_str:~1,-1%
echo %config_str%

rem Enable airplane mode
rem %2\lvp_resources\airplanemode.exe -Enable
if %3 == RadioEnable ( %2\lvp_resources\RadioEnable.exe -Disable ) else ( %2\lvp_resources\airplanemode.exe -Enable )
timeout 3 /nobreak

rem UPDATE: Commenting the following out because it was causing Powershell to be a top process in scenario runs
rem Perform config_check post to get wi-fi status during test
rem echo Calling 2nd config_check -prerun to verify radio is disabled...
rem start /wait /min powershell.exe %config_str%
rem timeout 2 /nobreak

rem Wait for desired time
%2\lvp_resources\sleep.exe %1

rem Disable airplane mode
rem %2\lvp_resources\airplanemode.exe -Disable
if %3 == RadioEnable ( %2\lvp_resources\RadioEnable.exe -Enable ) else ( %2\lvp_resources\airplanemode.exe -Disable )
rem %2\lvp_resources\sleep.exe 5
rem if %3 == RadioEnable ( %2\lvp_resources\RadioEnable.exe -Enable )