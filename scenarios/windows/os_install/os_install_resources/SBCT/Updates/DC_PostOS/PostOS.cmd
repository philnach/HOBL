cd /d c:\DC_PostOS

@REM Restore previous name of device
call RenamePC.cmd

@REM Enable Remote Desktop
netsh firewall set portopening TCP 3389 "Remote Desktop" enable

@REM set up DUT for DUTLab framework
cd /d d:\dut_setup_files
md c:\hobl_bin
call dut_setup.cmd 2>&1 | dut_setup\tee.exe c:\hobl_bin\dut_setup.log

echo ... OS INSTALL COMPLETE !!! :)


