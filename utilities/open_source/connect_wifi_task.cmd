echo off
rem Get paths

if "%dut_wifi_name%" EQU "" (
    set dut_wifi_name=%1
)
echo MSA account      : %msa_account%
echo DUT name         : %dut_name%
echo DUT password     : %dut_password%
echo DUT wifi name    : %dut_wifi_name%

netsh wlan set profileparameter name=%dut_wifi_name% connectionmode=auto nonBroadcast=yes
netsh wlan connect name=%dut_wifi_name%




