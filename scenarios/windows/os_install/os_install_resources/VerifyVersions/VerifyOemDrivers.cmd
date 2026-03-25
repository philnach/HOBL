@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

@REM Run Verify Versions
pushd "%~dp0"
powershell -ExecutionPolicy bypass -command "& { .\VerifyOemDrivers.ps1 -Exclude_File:C:\tools\ple\TOAST\Misc\Setup\TrainInformation.xml; exit $LASTEXITCODE }" 

set BANGERROR=!ERRORLEVEL!
echo %bangerror%

@REM Show results
@REM results_drivers1.html

@REM if %bangerror% EQU 1 (
@REM     copy c:\tools\ple\toast\verifyversions\results_drivers1.xml c:\tools\ple\toast
@REM     copy c:\tools\ple\toast\verifyversions\results_driverVer11.xsl c:\tools\ple\toast
@REM ) else (
@REM     del c:\tools\ple\toast\results_*
@REM )

popd
exit /b !BANGERROR!

