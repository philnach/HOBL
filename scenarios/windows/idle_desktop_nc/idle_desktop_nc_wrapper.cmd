@echo off
setlocal enabledelayedexpansion
cls
set wifi_off_duration=%1
echo Wifi off time (sec): %wifi_off_duration%
if [%2] NEQ [] set dut_exec_path=%2

set wlan='netsh wlan show interfaces'
rem echo %wlan%

for /f "delims=" %%i in (%wlan%) do set "target=!target! %%i"
echo Target: %target%
rem set this_ssid=%target%

for /f "tokens=12-15 delims=:" %%a in ("%target%") do (set start=%%a&set this_ssid=%%b&set the_rest=%%c)
rem remove 'BSSID' from string
set this_ssid=%this_ssid:BSSID =%

rem trim spaces from start of line
for /f "tokens=* delims= " %%a in ("%this_ssid%") do set this_ssid=%%a
rem remove spaces from string
set this_ssid=%this_ssid: =%
echo %this_ssid%
rem disconnect from wlan
netsh wlan set profileparameter name="%this_ssid%" connectionmode=manual
netsh wlan disconnect
rem if [%2] EQU [] timeout /t %1
if [%2] EQU [] c:\hobl_bin\sleep\sleep.exe %1

netsh wlan set profileparameter name="%this_ssid%" connectionmode=auto nonBroadcast=yes
netsh wlan connect name="%this_ssid%"

