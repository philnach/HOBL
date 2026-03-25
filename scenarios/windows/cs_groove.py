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
# Prep for playing music with Groove during cs
#
# Setup instructions:
#   copy music file and setup groove app.
##
from builtins import str
import builtins
import logging
import os
import time
import appium.common.exceptions as exceptions
import core.app_scenario
import selenium.common.exceptions as exceptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from core.parameters import Params
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException


class CsGroove(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'title', 'Groove')  # Just has to be unique substring of title
    Params.setDefault(module, 'music_file', 'power_dve_audio.wav')
    Params.setDefault(module, 'duration', '590')
    Params.setDefault(module, 'button_to_record_delay', '0')  # Seconds
    Params.setDefault(module, 'button_sleep_callback', 'python msft_skt_client.py -port 4770 Sleep_Toggle')
    Params.setDefault(module, 'button_wake_callback', 'python msft_skt_client.py -port 4770 Sleep_Toggle')
    Params.setDefault(module, 'paused', '')

    # Get parameters
    title = Params.get(module, 'title')
    music_file = Params.get(module, 'music_file')
    duration = Params.get(module, 'duration')
    button_to_record_delay = Params.get(module, 'button_to_record_delay')
    button_sleep = Params.get(module, 'button_sleep_callback')
    button_wake = Params.get(module, 'button_wake_callback')
    paused = Params.get(module, 'paused')

    # Local parameters
    prep_scenarios = ["groove_prep"]


    def setUp(self):
        logging.info("Launching WinappDriver.exe on DUT.")
        self._call([(self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"), (self.dut_resolved_ip + " " + self.app_port)], blocking=False)
        time.sleep(1)
        desired_caps = {}
        desired_caps["app"] = "Microsoft.ZuneMusic_8wekyb3d8bbwe!microsoft.ZuneMusic"
        self.groove_driver = self._launchApp(desired_caps)
        time.sleep(2)    
        logging.info("Select My music")
        self.groove_driver.find_element_by_name("My music").click()
        time.sleep(2)
        self.groove_driver.find_element_by_xpath('//*[contains(@Name,"Surface Power,")]').click()
        time.sleep(2)
        self.groove_driver.find_element_by_name("Play all").click()

        logging.info(self.paused)

        if self.paused == "1":
            time.sleep(5)
            self.groove_driver.find_element_by_name("Pause").click()

        core.app_scenario.Scenario.setUp(self, callback_test_begin="")

        # Put Device to Sleep
        logging.info("Device sleep now.")
        if self.button_sleep != '':
            logging.info("Calling local Button Script.")
            self._host_call("powershell " + self.button_sleep)
        else:
            logging.info("Calling Button.exe on DUT.")
            result = self._call([os.path.join(self.dut_exec_path, "button.exe"), " -s " + str(int(self.duration) * 1000)], blocking = False)
            print(result)
            if 'error' in result :
                raise Exception("Button.exe could not found!")

        logging.info("Delaying for " + self.button_to_record_delay + " seconds before starting power measurement.")
        time.sleep(float(self.button_to_record_delay))

        # Start recording power
        self._callback(Params.get('global', 'callback_test_begin'))

    def runTest(self):
        logging.info("Sleeping for " + self.duration)
        time.sleep(float(self.duration))

        # Trigger endTest callback to stop recording before we wake back up
        logging.info("Device wake now.")
        # Stop recording power
        self._callback(Params.get('global', 'callback_test_end'))

        # Give time for Stop command to propagate
        time.sleep(2)

        # Wake Up Device
        if self.button_wake != '':
            logging.info("Calling local Button Script.")
            self._host_call("powershell " + self.button_wake)

        # Give time for system to wake up before tear down
        time.sleep(10)
        if self.enable_screenshot == '1':
            self._screenshot(name="end_screen.png")

    def tearDown(self):
        self.groove_driver.find_element_by_name("Close Groove Music").click()
        time.sleep(2)

        logging.info("Performing teardown.")
        # Prevent callback_test_end from executing in base tearDown() method
        core.app_scenario.Scenario.tearDown(self, callback_test_end="")
        
        time.sleep(2)
        self._kill("WinAppDriver.exe")

    def kill(self):
        try:
            logging.debug("Killing Music.UI.exe")
            self._kill("Music.UI.exe")
        except:
            pass