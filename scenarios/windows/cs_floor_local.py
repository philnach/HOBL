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
# Connected Standby
#
# Setup instructions:
#   Run Rundaily Prep Script
#   Have script for triggering a button press on the device 
##

from builtins import str
import builtins
import unittest
import logging
import time
import core.app_scenario
from core.parameters import Params
import os

class CSFloorLocal(core.app_scenario.Scenario):

    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'duration', '1200')  # Seconds 1200
    Params.setDefault(module, 'button_to_record_delay', '900')  # Seconds 900
    Params.setDefault(module, 'button_sleep_callback', '')
    Params.setDefault(module, 'button_wake_callback', '')
    Params.setDefault(module, 'wifi_off_duration', '300') # Seconds
    Params.setDefault(module, 'local_button', '1') # 0 = host, 1 = DUT
    Params.setDefault("gloabl", 'dut_wifi_name', '') # Seconds

    # Get parameters
    duration = Params.get(module, 'duration')
    button_to_record_delay = Params.get(module, 'button_to_record_delay')
    button_sleep = Params.get(module, 'button_sleep_callback')
    button_wake = Params.get(module, 'button_wake_callback')
    wifi_off_duration = Params.get(module, 'wifi_off_duration')
    local_button = Params.get(module, 'local_button')
    local_execution = Params.get('global', 'local_execution')
    dut_wifi_name = Params.get('global', 'dut_wifi_name')

    wifi_off_duration = str((int(duration)) + (int(button_to_record_delay)) + 15)
    logging.info("WiFo Off Duration: " + str(wifi_off_duration))
    #wifi_off_duration = str(15)

    # Local parameters
    prep_scenarios = ["daily_prep", "button_install"]


    def setUp(self):
        # Call base setUp() which runs config_check and starts ETL tracing.
        # Prevent callback_test_begin from executing at this time
        core.app_scenario.Scenario.setUp(self, callback_test_begin='')
        
        # set up dut to disable wifi for wifi_off_duration
        logging.info("Setting DUT to wake on exiting standby")
        logging.info("Wifi Off Duration:" + self.wifi_off_duration)

        # Disconnect wi-fi
        #netsh wlan set profileparameter name="%this_ssid%" connectionmode=manual
        if self.dut_wifi_name!="":
            self._call(["cmd.exe", "/C  netsh wlan set profileparameter name=" + self.dut_wifi_name + " connectionmode=manual"]) 
            time.sleep(1)
            self._call(["cmd.exe", "/C  netsh wlan disconnect"]) 
            time.sleep(2)

        logging.info("Performing additional -prerun config_check for wi-fi disconnected verification.")
        override_str = '[{\'Scenario\': \'' + self.module + '\'}]'
        print('override string used for traige the configcheck scenario issue:   ' + override_str)
        cmd = '-ExecutionPolicy Unrestricted -Command "' + os.path.join(self.dut_exec_path, "config_check.ps1 -Prerun -LogFile " + self.dut_data_path, self.testname + "_ConfigPre") + " -OverrideString " + '\\\"' + override_str + '\\\""'
        result = self._call(["powershell.exe", cmd])
       
        # Start recording power
        time.sleep(int(self.button_to_record_delay))
        self._callback(Params.get('global', 'callback_test_begin'))


    def runTest(self):
        # Put Device to Sleep
        print("Device sleep now.")
        logging.info("Device sleep now.")
        logging.info("Calling local Button Script")
        button_off_duration = int(self.wifi_off_duration) * 1000
        logging.info("Delaying for " + self.button_to_record_delay + " seconds before starting power measurement.")
        logging.info("Starting CS sleep for " + self.wifi_off_duration + " seconds")        
        try:
            logging.info("Button_off_duration: " + str(button_off_duration))
            logging.info("cmd.exe" + "/C " + self.dut_exec_path + "\\button\\" + "button.exe -s " + str(button_off_duration))
            self._call(["cmd.exe", "/C " + os.path.join(self.dut_exec_path, "button", "button.exe -s " + str(button_off_duration))], blocking = False) 
            time.sleep(2)
        except:
            logging.error("button.exe not found on DUT")
        
        # Stop recording power
        self._callback(Params.get('global', 'callback_test_end'))

        # Give time for Stop command to propagate
        time.sleep(5)

        # Wake Up Device
        if self.button_wake != '':
            logging.info("Calling local Button Script")
            self._host_call("powershell " + self.button_wake)
        
        if self.dut_wifi_name!="":
            # Connect wi-fi
            logging.info("Connecting to Wi-Fi.")
            self._call(["cmd.exe", "/C netsh wlan connect name=" + self.dut_wifi_name]) 
            self._call(["cmd.exe", "/C netsh wlan set profileparameter name=" + self.dut_wifi_name + " connectionmode=auto nonBroadcast=yes"]) 
            logging.info("Delaying for 20 seconds to make sure WiFi is back up.")
            time.sleep(20)

    def tearDown(self):
        # Prevent callback_test_end from executing in base tearDown() method
        core.app_scenario.Scenario.tearDown(self, callback_test_end="")
    
