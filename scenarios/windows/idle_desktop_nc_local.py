"""
//--------------------------------------------------------------
//
// HOBL
// Copyright(c) Microsoft Corporation
// All rights reserved.
//
// MIT License
//
// Permission is hereby granted, free of charge, to any person obtaining
// a copy of this software and associated documentation files(the ""Software""),
// to deal in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies
// of the Software, and to permit persons to whom the Software is furnished to do so,
// subject to the following conditions :
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
// FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS
// OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
// OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//
//--------------------------------------------------------------
"""

##
# Idle at the Desktop with wifi not connected
#
# Setup instructions:
#   None
##

from builtins import str
import builtins
import logging
import time, os
import core.app_scenario
from core.parameters import Params
import unittest


class IdleDesktopNcLocal(core.app_scenario.Scenario):

    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'duration', '300')  # Seconds
    Params.setDefault(module, 'button_sleep_callback', '')
    Params.setDefault(module, 'button_wake_callback', '')
    Params.setDefault(module, 'wifi_off_duration', '300') # Seconds
    Params.setDefault("global", 'dut_wifi_name', '') # Seconds

    # Get parameters
    duration = Params.get(module, 'duration')
    wifi_off_duration = Params.get(module, 'wifi_off_duration')
    platform = Params.get('global', 'platform')
    dut_wifi_name = Params.get('global', 'dut_wifi_name')
    wifi_off_duration = str((int(duration)) + 15)
    logging.info("Wi_Fi OFF Duration: " + wifi_off_duration)
 
    # Local parameters
    prep_scenarios = ["daily_prep"]

    def setUp(self):
        # minimize any windows
        if self.platform == 'Windows':
            self._call(["powershell.exe", '-command "$x = New-Object -ComObject Shell.Application; $x.minimizeall()"'])


        # Call base setUp() which runs config_check and starts ETL tracing.
        # Prevent callback_test_begin from executing at this time
        core.app_scenario.Scenario.setUp(self, callback_test_begin="")
        
        # set up dut to disable wifi for wifi_off_duration
        logging.info("Wifi Off Duration:" + self.wifi_off_duration)

        if self.dut_wifi_name != "":
            # Disconnect wi-fi
            self._call(["cmd.exe", "/C  netsh wlan set profileparameter name=" + self.dut_wifi_name + " connectionmode=manual"]) 
            time.sleep(1)
            self._call(["cmd.exe", "/C  netsh wlan disconnect"]) 
            time.sleep(2)

       # Perform config_check post to get wi-fi status during test
        logging.info("Performing additional prerun config_check.")
        override_str = '[{\'Scenario\': \'' + self.module + '\'}]'
        print('override string used for triage the configcheck scenario issue:   ' + override_str)
        cmd = '-ExecutionPolicy Unrestricted -Command "' + os.path.join(self.dut_exec_path, "config_check.ps1 -Prerun -LogFile " + self.dut_data_path, self.testname + "_ConfigPre") + " -OverrideString " + '\\\"' + override_str + '\\\""'
        result = self._call(["powershell.exe", cmd])
        time.sleep (2)

        # Start recording power
        self._callback(Params.get('global', 'callback_test_begin'))
    
    def runTest(self):
        # Sleep for specified duration
        logging.info("Sleeping for " + self.wifi_off_duration)
        time.sleep(float(self.wifi_off_duration))


        # Stop recording power
        self._callback(Params.get('global', 'callback_test_end'))

        # Give time for Stop command to propagate
        time.sleep(5)
        if self.platform == 'Windows':
            self._call(["powershell.exe", '-command "$x = New-Object -ComObject Shell.Application; $x.undominimizeall()"'])

        if self.dut_wifi_name != "":
            # Connect wi-fi
            self._call(["cmd.exe", "/C netsh wlan connect name=" + self.dut_wifi_name]) 
            self._call(["cmd.exe", "/C netsh wlan set profileparameter name=" + self.dut_wifi_name + " connectionmode=auto nonBroadcast=yes"]) 

    def tearDown(self):
        # Prevent callback_test_end from executing in base tearDown() method
        core.app_scenario.Scenario.tearDown(self, callback_test_end="")


