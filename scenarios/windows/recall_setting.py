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
# Disable adaptive color
##

import time
import logging
from core.parameters import Params


import core.app_scenario


class AdaptiveColorDisable(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    # Parameter for enable or disable recall
    Params.setDefault(module, 'recall_mode', '1')


    # Get Parameter
    recall_mode = Params.get(module, 'recall_mode')

    is_prep = True


    def runTest(self):
        logging.info("Launching WinAppDriver.exe on DUT")

        self._call([
            (self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"),
            (self.dut_resolved_ip + " " + self.app_port)],
            blocking=False
        )

        desired_caps = {}
        desired_caps["app"] = "Root"

        self.driver = self._launchApp(desired_caps)

        self._call(["cmd.exe", '/C start ms-settings:privacy'])
        time.sleep(1)

        # Go to recall & snapshots setting
        try:
            logging.info("trying to open recall settings")
            self.driver.find_element_by_xpath('//*[contains(@Name, "Recall & snapshots")]').click()
            time.sleep(3)
        except:
            logging.error("Couldn't find recall settings")
            self.driver.close()
            self.fail("Couldn't find recall settings. Ignore if recall is not supported on this device")

        toggle_switch = self.driver.find_element_by_xpath('//Button[contains(@Name, "Save snapshots")]')
        if self.recall_mode == "1":
            if not toggle_switch.is_selected():
                toggle_switch.click()
                logging.info("Recall enabled")
            else:
                logging.info("Recall already turned on")

        elif self.recall_mode == "0":
            if toggle_switch.is_selected():
                toggle_switch.click()
                logging.info("Recall disabled")
            else:
                logging.info("Recall already turned off")
        # self._page_source(self.driver)
        # try:
        #     toggle_switch = self.driver.find_element_by_xpath("//*[@Name = 'Adaptive color' and @ClassName = 'ToggleSwitch']")
        # except:
        #     logging.info("Adaptive color setting not found, exiting.")
        #     self.driver.close()
        #     time.sleep(1)
        #     self.createPrepStatusControlFile()
        #     return

        # if toggle_switch.is_selected():
        #     toggle_switch.click()
        #     logging.info(f"Adaptive color disabled")
        # else:
        #     logging.info(f"Adaptive color already disabled")

        time.sleep(1)

        self.driver.close()
        time.sleep(3)
        # self.createPrepStatusControlFile()


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
