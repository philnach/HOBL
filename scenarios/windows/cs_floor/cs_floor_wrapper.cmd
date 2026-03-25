@echo off
setlocal enabledelayedexpansion
cls
set wifi_off_duration=%1
echo Wifi off time (sec): %wifi_off_duration%

rem if dut_exec_path is not empty, call button.exe on dut and multiply button_delay by 1000
if [%2] NEQ [] set dut_exec_path=%2
if [%2] NEQ [] echo DUT Path: %dut_exec_path%
if [%2] NEQ [] set /a button_delay=%wifi_off_duration% * 1000
if [%2] NEQ [] echo Button Delay: %button_delay%

for /f "delims=: tokens=2" %%n in ('netsh wlan show interface name="Wi-Fi" ^| findstr ^/R "\<SSID"') do set "this_ssid=%%n"
set "this_ssid=%this_ssid:~1%"
echo %this_ssid%

rem disconnect from wlan
netsh wlan set profileparameter name="%this_ssid%" connectionmode=manual
netsh wlan disconnect
rem if [%2] EQU [] timeout /t %1
if [%2] EQU [] c:\hobl_bin\sleep\sleep.exe %1

if [%2] NEQ [] %dut_exec_path%\button\button.exe -s %button_delay%
netsh wlan set profileparameter name="%this_ssid%" connectionmode=auto nonBroadcast=yes
netsh wlan connect name="%this_ssid%"

