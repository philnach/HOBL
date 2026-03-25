@echo off
SetLocal EnableDelayedExpansion

REM Build host_installer.exe with InnoSetup
REM Requirements: InnoSetup installed.
REM dut_setup.exe built previously.
REM web_replay downloaded previously (by running web scenario).

set RUNTIME_VERSION=10.0.2
set RUNTIME_X64_DOWNLOAD_URL="https://builds.dotnet.microsoft.com/dotnet/WindowsDesktop/%RUNTIME_VERSION%/windowsdesktop-runtime-%RUNTIME_VERSION%-win-x86.exe"

set VC_REDIST_URL="https://aka.ms/vs/17/release/vc_redist.x86.exe"

REM Download .NET Windows Desktop Runtime installers
set FILEPATH="setup\src_host\windowsdesktop-runtime-%RUNTIME_VERSION%-win-x86.exe"
if not exist %FILEPATH% (
    echo Downloading %FILEPATH%
    curl -L --output %FILEPATH% %RUNTIME_X64_DOWNLOAD_URL%
    if %errorlevel% neq 0 goto ERROR
) else (
    echo %FILEPATH% already exists, skipping download
)

REM Download Visual C++ Redistributable
if not exist "setup\src_host\vc_redist.x86.exe" (  
    echo Downloading vc_redist.x86.exe
    curl -L --output "setup\src_host\vc_redist.x86.exe" %VC_REDIST_URL%
    if %errorlevel% neq 0 goto ERROR
) else (
    echo vc_redist.x86.exe already exists, skipping download
)

REM Update hobl_version.txt with git describe info
for /f "delims=" %%i in ('git describe --tags --always') do set GIT_DESCRIBE=%%i
echo %GIT_DESCRIBE% > hobl_version.txt

REM Build the installer using InnoSetup
echo Building host_installer.exe with InnoSetup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" build_host_installer.iss
if %errorlevel% neq 0 goto ERROR

goto END

:ERROR
echo Error occurred, please check the output for details
exit /b 1

:END
exit /b 0
