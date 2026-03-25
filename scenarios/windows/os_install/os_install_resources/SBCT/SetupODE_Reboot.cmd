@ECHO OFF
pushd "%~dp0"

powershell -ExecutionPolicy bypass -command "& { .\setupODE.ps1 %* ; exit $LASTEXITCODE }" 

set BANGERROR=%ERRORLEVEL%
echo %bangerror%

if %bangerror% EQU 0 (shutdown /r /t 5)
