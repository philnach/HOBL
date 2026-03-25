#--------------------------------------------------------------
#
# HOBL
# Copyright(c) Microsoft Corporation
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files(the ""Software""),
# to deal in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
# OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#--------------------------------------------------------------

#Scenario for running version report on Surface devices

import builtins
import logging
import core.app_scenario
from core.parameters import Params
import os
import json
from datetime import datetime
import shutil
import getpass

class VersionReport(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    # Set default parameters
    Params.setOverride("global", "trace", "0")
    Params.setOverride("global", "config_check", "0")
    Params.setOverride("global", "callback_test_begin", "")
    Params.setOverride("global", "callback_test_end", "")
    Params.setOverride("global", "callback_data_ready", "")
    Params.setOverride("global", "prep_tools", "")

    local_execution = Params.get('global', 'local_execution')

    is_prep = True

    def runTest(self):
        dut_data_path = Params.getCalculated("dut_data_path")
        dut_architecture = Params.get('global', 'dut_architecture')
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        logging.info("Date-Time: " + timestamp)
        log_path = dut_data_path + "\\versionreport_" + timestamp + ".log"

        version_report_tool = 'c:\\tools\\versionreport\\versionreport.cmd'
        # Check if c:\tools\versionreport\versionreport.cmd exists
        if self._check_remote_file_exists(version_report_tool):
            version_report_tool = "C:\\Tools\\Versionreport\\VersionReport.cmd -Logfile " + log_path
            self._call(["cmd.exe", "/C " + version_report_tool], fail_on_exception=False)   

        else:
            version_report_tool = "C:\\Tools\\VersionReport.cmd -Logfile " + log_path
            try:
                self._call(["cmd.exe", "/C " + version_report_tool], fail_on_exception=False)   
            except:
                logging.info("Version report had errors")
                        
        log_file = dut_data_path + "\\WindowsUpdateLog.log"
        logging.info("Log File Path: " + log_file)
        self._call(["powershell.exe", "Get-WindowsUpdateLog -LogPath " + log_file], expected_exit_code="", fail_on_exception=False)    
        self._call(["cmd.exe", "/c copy c:\\Windows\\INF\\setupapi.setup.log " + dut_data_path], expected_exit_code="")    
        self._call(["cmd.exe", "/c copy c:\\Windows\\INF\\setupapi.dev.log " + dut_data_path], expected_exit_code="")    
        self._call(["cmd.exe", "/c copy c:\\Windows\\INF\\setupapi.offline.log " + dut_data_path], expected_exit_code="")
        self._call(["powershell.exe", r"get-pnpdevice -presentonly | where-object {$_.Instanceid -match '^USB'} | format-table -autosize > c:\hobl_data\usb_devices.txt"], expected_exit_code="", fail_on_exception=False)    

        try:
            self._call(["cmd.exe", "/c copy c:\\tools\\ple\\TOAST\\verifyversions\\results_driver*.html " + dut_data_path], expected_exit_code="")
        except:
            pass
                
         