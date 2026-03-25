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
# Stream a DRM movie
#
# Setup instructions:
#   Purchase "Halo 2" from the store, do not download.
##

import logging
import os
import core.app_scenario
from core.parameters import Params
# from appium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as exceptions
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

class Photos(core.app_scenario.Scenario):

    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'folder', 'photos_resources')
    Params.setDefault(module, 'number', '10')
    Params.setDefault(module, 'delay', '10')
    
    # Get parameters
    folder = Params.get(module, 'folder')
    number = Params.get(module, 'number')
    delay = Params.get(module, 'delay')
    platform = Params.get('global', 'platform')
    training_mode = Params.get('global', 'training_mode')


    def setUp(self):
        logging.info("Performing setup: Launching WinAppDriver.exe on DUT.")
        self._call([(self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"), (self.dut_resolved_ip + " " + self.app_port)], blocking=False)
        time.sleep(1)

        # Copy images to DUT
        if Params.get("global", "local_execution") == "0":
            self.userprofile = self._call(["cmd.exe", "/C echo %USERPROFILE%"])
        else:
            self.userprofile = os.environ['USERPROFILE']
        self._upload(os.path.join("scenarios", "windows", "photos", self.folder), self.userprofile + "\\Pictures")

        # Launch Photos app
        desired_caps = {}
        desired_caps["app"] = "Microsoft.Windows.Photos_8wekyb3d8bbwe!App"
        self.driver = self._launchApp(desired_caps)
        time.sleep(5)
        self.driver.maximize_window()
        time.sleep(2)

        # Search for "photos_resources"
        self.driver.find_element_by_name("Search in All Photos").click()
        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
        ActionChains(self.driver).send_keys(self.folder).perform()
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        time.sleep(2)

        # Click on first container and press Enter to open image
        self.driver.find_element_by_accessibility_id("Container").click()
        time.sleep(1)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        time.sleep(3)

        core.app_scenario.Scenario.setUp(self)


    def runTest(self):
        # Enter full screen with F11
        ActionChains(self.driver).send_keys(Keys.F11).perform()

        # Cycle through all the pictures
        for i in range(int(self.number) - 1):
            time.sleep(float(self.delay))
            ActionChains(self.driver).send_keys(Keys.ARROW_RIGHT).perform()
        for i in range(2):
            time.sleep(float(self.delay))
            ActionChains(self.driver).send_keys(Keys.ARROW_LEFT).perform()
        time.sleep(float(self.delay))


    def tearDown(self):
        core.app_scenario.Scenario.tearDown(self)
        logging.info("Performing teardown.")
        logging.debug("Killing Photos App")
        self._kill("PhotosApp.exe")


    def kill(self):
        try:
            logging.debug("Killing Photos App")
            self._kill("PhotosApp.exe")
        except:
            pass
        
