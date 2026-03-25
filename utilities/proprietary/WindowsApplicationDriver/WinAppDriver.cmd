IF [%1] EQU [] for /f "usebackq tokens=2 delims=:" %%f in (`ipconfig ^| findstr /c:"IPv4 Address"`) do set dut_ip=%%f
IF [%2] EQU [] set dut_port=4723

IF [%1] NEQ [] set dut_ip=%1
IF [%2] NEQ [] set dut_port=%2

%~dp0\WinAppDriver.exe %dut_ip% %dut_port%