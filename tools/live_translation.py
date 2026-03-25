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
# Tool wrapper for audio control

from builtins import str
from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import os
import decimal
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class Tool(Scenario):

    module = __module__.split('.')[-1]

    def initCallback(self, scenario):

        self.scenario = scenario
        self._call([(self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"), (self.dut_resolved_ip + " " + self.app_port + " /forcequit")], expected_exit_code="", blocking=False)
        time.sleep(1)

        # Connect to desktop to be able to launch apps with Start menu
        desired_caps = {}
        desired_caps["app"] = "Root"
        self.desktop = self._launchApp(desired_caps)
        self.desktop.implicitly_wait(0)

        logging.info("Starting Live Translation Ribbon")

        ActionChains(self.desktop).key_down(Keys.CONTROL).key_down(Keys.META).send_keys("l").key_up(Keys.META).key_up(Keys.CONTROL).perform()
        time.sleep(3)
        # Try to look for downloading of model
        try:
            self.desktop.find_element_by_name("Yes, continue").click()
            time.sleep(180)
        except:
            pass

        try:
            self.desktop.find_element_by_name("Continue").click()
            time.sleep(3)
        except:
            pass

        #live_caption = self.desktop.find_element_by_name("Live Captions")
        self.desktop.find_element_by_name("Settings").click()
        time.sleep(3)
        #self._page_source(self.desktop)
        #self.desktop.find_element_by_name("Postion").click()
        live_caption = self.desktop.find_element_by_name("Live Captions")
        #self.desktop.find_element_by_accessibility_id("DockPositionButton").click()
        live_caption.find_element_by_accessibility_id("DockPositionButton").click()
        time.sleep(3)
        self.desktop.find_element_by_name("Above screen").click()
        time.sleep(3)

        if scenario.training_mode == "0":
            self._kill("WinAppDriver.exe")
        return

    def testBeginCallback(self):
        pass

    def testEndCallback(self):
        self._kill("LiveCaptions.exe")
        return

    def dataReadyCallback(self):
        pass

    def testScenarioFailed(self):
        self.testEndCallback()

    def testTimeoutCallback(self):
        self.testEndCallback()
        self.conn_timeout = True
        
    def cleanup(self):
        self.testEndCallback()


