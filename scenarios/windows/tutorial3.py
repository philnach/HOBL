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

import core.app_scenario
from core.parameters import Params
import logging
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
 
# Tutorial for creating a scenario:
#   - Launch Notepad, type, and exit
#   - Kill routine to clean up after failure or termination

class HelloWorld(core.app_scenario.Scenario):
    # Set default parameters
    Params.setDefault('tutorial3', 'duration', '3')  # Seconds

    # Get parameter values
    duration = Params.get('tutorial3', 'duration')


    def setUp(self):
        # Start WinAppDriver server
        self._call([(self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"), (self.dut_resolved_ip + " " + self.app_port + " /forcequit")], blocking=False)
        time.sleep(1)
        self.desktop_driver = self._launchDesktop()

        # Call base class setUp() to start power measurment
        core.app_scenario.Scenario.setUp(self)
            # Create hobl_data folder
            # Tool init callback
            # Config_check
            # Tool begin callback
            # Start tracing
            # Test begin callback


    def runTest(self):
        # Launch Notepad
        logging.info("Launching Notepad.")
        self._get_search_button(self.desktop_driver).click()
        ActionChains(self.desktop_driver).send_keys("notepad" + Keys.ENTER).perform()
        time.sleep(6)

        # Find Notepad window and type
        notepad_window = self.desktop_driver.find_element_by_class_name("Notepad")

        # Type Hello World
        logging.info("Typing Hello World.")
        text_editor = notepad_window.find_element_by_name("Text editor")
        text_editor.click()
        text_editor.send_keys("Hello World" + Keys.RETURN)

        # Wait for duration
        logging.info("Waiting for " + self.duration + " seconds")
        time.sleep(int(self.duration))

        # Exit notepad
        self._page_source(self.desktop_driver)
        notepad_window.find_element_by_name("Close").click()


    def tearDown(self):
        # Call base class tearDown() to stop power measurment
        core.app_scenario.Scenario.tearDown(self)
            # Test end callback
            # Tool end callback
            # Stop tracing
            # Post config_check
            # Copy data back from DUT
            # Tool data ready callback
            # Test data ready callback
            # Tool report callback

        # Kill WinAppDriver to make sure it is not running for next scenario
        self._kill("WinAppDriver.exe")

    
    def kill(self):
        # In case of scenario failure or termination, kill any applications left open
        logging.info("Killing open applications")
        self._kill("WinAppDriver.exe")
        self._kill("notepad.exe")
