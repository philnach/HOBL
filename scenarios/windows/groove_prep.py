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
# Prep for playing music with Groove
#
# Setup instructions:
#   copy music file and setup groove app.
##
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
from selenium.webdriver.common.keys import Keys


class Groove_Prep(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'title', 'Groove')  # Just has to be unique substring of title
    Params.setDefault(module, 'music_file', 'power_dve_audio.wav')
    # Get parameters
    title = Params.get(module, 'title')
    music_file = Params.get(module, 'music_file')

    # Override collection of config data, traces, and execution of callbacks 
    # Params.setOverride("global", "collection_enabled", "0")
    is_prep = True


    def runTest(self):
        source = os.path.join("scenarios", "groove_resources", self.music_file)
        dest = os.path.join("C:\\", "Users", self.user, "Music")
        dest_file = os.path.join(dest, self.music_file)
        # Check if music file already exists on DUT
        if self._check_remote_file_exists(dest_file, False):
            logging.info("Music file " + self.music_file + " already found on DUT.  Skipping upload")
        else:
            logging.info("Uploading music file " + self.music_file + " to " + dest)
            self._upload(source, dest)

        logging.info("Launching WinappDriver.exe on DUT.")
        self._call([(self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"), (self.dut_resolved_ip + " " + self.app_port)], blocking=False)
        time.sleep(1)

        desired_caps = {}
        desired_caps["app"] = "Microsoft.ZuneMusic_8wekyb3d8bbwe!microsoft.ZuneMusic"
        groove_driver = self._launchApp(desired_caps)
        time.sleep(1)
        logging.info("Waiting for " + self.title + "app to setup")
        time.sleep(20)
        try:
            groove_driver.find_element_by_name("Got it").click()
            time.sleep(2)
        except NoSuchElementException as EX:
            logging.info("Got it pop-up not found")
            pass
        groove_driver.close()
        time.sleep(3)

        desired_caps = {}
        desired_caps["app"] = "Microsoft.ZuneMusic_8wekyb3d8bbwe!microsoft.ZuneMusic"
        groove_driver = self._launchApp(desired_caps)
        time.sleep(5)
        try:
            groove_driver.find_element_by_name("Got it").click()
            time.sleep(2)
        except NoSuchElementException as EX:
            logging.info("Got it pop-up not found")
            pass
        groove_driver.close()
        time.sleep(1)

    def tearDown(self):
        self.createPrepStatusControlFile()
        logging.info("Performing teardown.")
        core.app_scenario.Scenario.tearDown(self)
        time.sleep(2)
        self._kill("WinAppDriver.exe")