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
# Set refresh rate
##

import time
import logging

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from core.parameters import Params
import core.app_scenario


class RefreshRate(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    # Set default parameters
    Params.setDefault(module, 'rate', '60') # Number or 'dynamic Number'
    Params.setDefault(module, 'display', 'default') # Number or 'default'

    # Get parameters
    rate = Params.get(module, 'rate')
    display = Params.get(module, 'display')

    is_prep = True

    def runTest(self):
        logging.info("Launching WinAppDriver.exe on DUT")

        self._call([
            (self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"),
            (self.dut_ip + " " + self.app_port)],
            blocking=False
        )

        desired_caps = {}
        desired_caps["app"] = "Root"

        self.driver = self._launchApp(desired_caps)

        self._call(["cmd.exe", '/C start ms-settings:'])
        time.sleep(1)

        self.driver.find_element_by_name("System").click()
        time.sleep(1)

        self.driver.find_element_by_name("Display").click()
        time.sleep(1)

        self.driver.find_element_by_name("Advanced display").click()
        time.sleep(1)

        if self.display != 'default':
            if not self.display.isdigit():
                raise Exception("display parameter is invalid")

            self.driver.find_element_by_xpath('//ComboBox[contains(@Name, "Select a display")]').click()
            time.sleep(1)

            target_display = self.driver.find_element_by_xpath(f'//*[contains(@Name, "Display {self.display}")]')
            time.sleep(1)

            if target_display.is_selected():
                logging.info(f"Target display {self.display} already selected")
            else:
                logging.info(f"Target display set to display {self.display}")

            target_display.click()
            time.sleep(1)

        self.driver.find_element_by_name("Refresh rate").click()
        time.sleep(1)

        if self.rate.isdigit():
            target_rate = self.driver.find_element_by_name(f"{self.rate} Hz")
        else:
            start_dynamic_rate = self.rate.split(" ")[-1]

            if not start_dynamic_rate.isdigit():
                raise Exception("rate parameter is invalid")

            target_rate = self.driver.find_element_by_xpath(
                f"//*[contains(@Name, 'Dynamic') and contains(@Name, {start_dynamic_rate})]"
            )

        time.sleep(1)

        if target_rate.is_selected():
            logging.info(f"Target rate {self.rate} already selected")
        else:
            target_rate.click()
            time.sleep(1)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "Keep changes"))
            ).click()

            time.sleep(2)

            logging.info(f"Successfully set refresh rate to {self.rate}")

        self.driver.close()


    def tearDown(self):
        core.app_scenario.Scenario.tearDown(self)

        logging.debug("Killing SystemSettings.exe")
        self._kill("SystemSettings")

        logging.debug("Killing WinAppDriver.exe")
        self._kill("WinAppDriver")


    def kill(self):
        try:
            logging.debug("Killing SystemSettings.exe")
            self._kill("SystemSettings.exe")
        except:
            pass

        try:
            logging.debug("Killing WinAppDriver.exe")
            self._kill("WinAppDriver.exe")
        except:
            pass
