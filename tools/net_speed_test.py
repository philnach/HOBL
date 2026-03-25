# Take screenshots during scenario, where pause = the number of seconds between screenshots.
# Set pause = 0 (default) to only take screenshots at the beginning and end of the scenario.
#
# To use, add "global:tools=screenshot" and optionally "screenshot:pause=<number of seconds>"
# to the hobl command.
# 
# Need this in hobl_bin on DUT: \\ntwdata\powtel\CTF\ClientPower\Tests\x64\ScreenCapture.exe

from builtins import str
from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import os
import time


class Tool(Scenario):
    '''
    Run speedtest.exe to gauge internet bandwidth.
    '''
    module = __module__.split('.')[-1]

    dut_architecture = Params.get('global', 'dut_architecture')
    
    def initCallback(self, scenario):
        if self.dut_architecture == "x64":
            logging.info("Executing speedtest.exe to measure network bandwidth.")
            speedtest_path = os.path.join(self.dut_exec_path,"speedtest.exe")
            select_str = "Select-String -Pattern '(?=Upload|Download)(.*)(?=\\sMbps)' -AllMatches | %{$_.Matches} | "
            select_obj = "Select-Object @{ Name='Name'; Expression={$_.Value.split(' ')[0].replace(':',' (Mbps)')} }, @{ Name='Value'; Expression={$_.Value.split(' ')[-1]} } | "
            convert_csv = "ConvertTo-Csv -NoTypeInformation | Select-Object -Skip 1 | Set-Content -Path " + os.path.join(self.dut_data_path, "net_speed_test.csv")

            if self._check_remote_file_exists("speedtest.exe"):
                self._call(["powershell.exe", speedtest_path + " --accept-license -u Mbps | " + select_str + select_obj + convert_csv])
            else:
                self._upload("utilities\\x64\\SpeedTest\\speedtest.exe", self.dut_exec_path)
                self._call(["powershell.exe", speedtest_path + " --accept-license -u Mbps | " + select_str + select_obj + convert_csv])
        else:
            logging.info("The speedtest.exe is not supported on this platform.")
        
    def testBeginCallback(self):
        return
        
    def testEndCallback(self):
        return
        
    def dataReadyCallback(self):
        return
