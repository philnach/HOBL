@echo off
set testname=%1

Powershell.exe -ExecutionPolicy Unrestricted -Command "C:\\hobl_bin\\config_check.ps1 -PostRun -LogFile 'C:\hobl_data\%testname%_ConfigPost' -PreRunFile 'C:\hobl_data\%testname%_ConfigPre.csv'" >> C:\hobl_data\battery_level.txt

wpr.exe -marker 'test_end' >> C:\hobl_data\battery_level.txt
wpr.exe -stop C:\hobl_data\%testname%.etl 

echo "stopped etl trace and saved as %testname%.etl">> C:\hobl_data\battery_level.txt