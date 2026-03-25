REM Copyright (c) Microsoft. All rights reserved.
REM Licensed under the MIT license. See LICENSE file in the project root for full license information.

@echo off
setlocal

set CONFIGURATION=Release
set PLATFORM=x64

:: Locate vswhere
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (
    echo ERROR: vswhere.exe not found. Is Visual Studio installed?
    exit /b 1
)

:: Find the latest VS installation with the C++ build tools
for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -requires Microsoft.Component.MSBuild -find MSBuild\**\Bin\MSBuild.exe`) do (
    set "MSBUILD=%%i"
)

if not defined MSBUILD (
    echo ERROR: MSBuild not found. Ensure Visual Studio with C++ workload is installed.
    exit /b 1
)

echo Using MSBuild: %MSBUILD%
echo Building %CONFIGURATION%^|%PLATFORM% ...

"%MSBUILD%" "%~dp0SimpleTimer.sln" /p:Configuration=%CONFIGURATION% /p:Platform=%PLATFORM% /m /nologo
if %ERRORLEVEL% neq 0 (
    echo BUILD FAILED.
    exit /b %ERRORLEVEL%
)

echo BUILD SUCCEEDED. Output: %~dp0%PLATFORM%\%CONFIGURATION%\SimpleTimer.exe
