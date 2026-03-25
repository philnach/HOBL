schtasks /create /sc ONLOGON /tn StartHostPrograms /tr c:\hobl\setup\src\host_start.cmd /f
powershell.exe Set-ExecutionPolicy Unrestricted -Force