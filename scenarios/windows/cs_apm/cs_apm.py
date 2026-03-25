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

##
# Cs with airplane mode enabled
#
##

from builtins import str
import builtins
import logging
import time, os
import core.app_scenario
from core.parameters import Params
from appium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
 
class CsApm(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'cs_duration', '1200')  # Seconds
    Params.setDefault(module, 'button_to_record_delay', '300')  # Seconds
    Params.setDefault(module, 'button_sleep_callback', '')
    Params.setDefault(module, 'button_wake_callback', '')
    Params.setDefault(module, 'airplane_mode', '1')
    Params.setDefault(module, 'radio_enable', '1')
    Params.setDefault(module, 'local_button', '1') # 0 = host, 1 = DUT
    Params.setDefault(module, 'sleep_mode', '') # Blank = connected standby, "S3" for S3.

    

    # Get parameters
    cs_duration = Params.get(module, 'cs_duration')
    button_to_record_delay = Params.get(module, 'button_to_record_delay')
    button_sleep = Params.get(module, 'button_sleep_callback')
    button_wake = Params.get(module, 'button_wake_callback')
    airplane_mode = Params.get(module, 'airplane_mode')
    radio_enable = Params.get(module, 'radio_enable')
    local_button = Params.get(module, 'local_button')
    local_execution = Params.get('global', 'local_execution')
    sleep_mode = Params.get(module, 'sleep_mode')
    dut_architecture = Params.get('global', 'dut_architecture')

    # Local parameters
    prep_scenarios = ["button_install"]

    # Add 15s to give us time to stop recording before DUT wakes up
    airplane_enabled_duration = str((int(cs_duration)) + (int(button_to_record_delay)) + 15)

    def setUp(self):
        self._upload('scenarios\\windows\\cs_apm\\cs_apm_wrapper.cmd', self.dut_exec_path + '\\cs_floor_resources', check_modified=True)
        self._upload("utilities\\proprietary\\sleep\\sleep.exe", os.path.join(self.dut_exec_path, "sleep"))
        self._upload("utilities\\proprietary\\radio\\" + self.dut_architecture + "\\RadioEnable.exe", os.path.join(self.dut_exec_path, "radio"))
        self._upload("utilities\\proprietary\\radio\\" + self.dut_architecture + "\\AirplaneMode.exe", os.path.join(self.dut_exec_path, "radio"))

        core.app_scenario.Scenario.setUp(self, callback_test_begin="")

        if self.button_sleep == "":
            button_type = "SW"
        else:
            button_type = "HW"

        # Set airplane mode enable
        if self.airplane_mode == '1':
            try:
                logging.info("Enabling airplane mode for " + str(self.airplane_enabled_duration) + " seconds.")
                if self.radio_enable == '0':
                    logging.info("cmd.exe /C " + os.path.join(self.dut_exec_path + "cs_floor_resources" + "cs_apm_wrapper.cmd") + ' ' + self.airplane_enabled_duration + ' ' + self.dut_exec_path + ' ' + "APM " + button_type)
                    self._call(["cmd.exe", "/C " + os.path.join(self.dut_exec_path, "cs_floor_resources", "cs_apm_wrapper.cmd") + ' ' + self.airplane_enabled_duration + ' ' + self.dut_exec_path + ' ' + "APM " + button_type], blocking = False) 
                else:
                    logging.info("cmd.exe /C " + os.path.join(self.dut_exec_path + "cs_floor_resources" + "cs_apm_wrapper.cmd") + ' ' + self.airplane_enabled_duration + ' ' + self.dut_exec_path + ' ' + "RadioEnable " + button_type)
                    self._call(["cmd.exe", "/C " + os.path.join(self.dut_exec_path, "cs_floor_resources", "cs_apm_wrapper.cmd") + ' ' + self.airplane_enabled_duration + ' ' + self.dut_exec_path + ' ' + "RadioEnable " + button_type], blocking = False) 
            except:
                pass
       
        # Delay to let airplane mode enable (5s hardcoded in cs_apm_wrapper.cmd)
        time.sleep(5)        

       # Put Device to Sleep
        print("Device sleep now.")
        logging.info("Device sleep now.")
       
        if self.button_sleep != '':
            logging.info("Sleep button:" + self.button_sleep)
            logging.info("Calling local Button Script")
            self._host_call("powershell " + self.button_sleep)

        logging.info("Delaying for " + self.button_to_record_delay + " seconds before starting power measurement.")
        
        if self.local_execution == '0':
            time.sleep(float(self.button_to_record_delay))

        # Start recording power
        self._callback(Params.get('global', 'callback_test_begin'))


    def runTest(self):
         # Sleep for specified duration
        
        if self.local_execution == '0':
            logging.info("Measuring Standby for " + self.cs_duration + " seconds")        
            time.sleep(float(self.cs_duration))
        
        # Stop recording power
        self._callback(Params.get('global', 'callback_test_end'))

        # Dut will wake up and enable wifi 15s from now (+15 at end of airplane_enabled_duration calc)

        # Give time for Stop command to propagate
        time.sleep(5)

        # Wake Up Device
        if self.button_wake != '':
            logging.info("Calling local Button Script")
            self._host_call("powershell " + self.button_wake)

        time.sleep(10)
        logging.info("Device wake now.")
        logging.info("Delaying for 30 seconds to make sure WiFi is back up.")
        time.sleep(30)
        if self.enable_screenshot == '1':
            self._screenshot(name="end_screen.png")

    def tearDown(self):
        logging.info("Performing teardown.")
        # Prevent callback_test_end from executing in base tearDown() method
        core.app_scenario.Scenario.tearDown(self, callback_test_end="")
        
    
