@ECHO OFF
pushd "%~dp0"
setlocal

set program_name=%~dpn0
set args=
:loop
if "%~1"=="" goto run
echo "Processing argument: %~1"
@REM set arg=%~1
rem Check if argument starts with -
if not "%~1:~0,1%"=="-" (
    set args=%args% "%~1"
) else (
    set args=%args% %~1
)
shift
goto loop

:run
echo "Running setup script with args: %args%"
powershell -ExecutionPolicy bypass -command "& { %program_name%.ps1 %args% ; exit $LASTEXITCODE }"

echo "Reboot to start setup"
timeout 60
