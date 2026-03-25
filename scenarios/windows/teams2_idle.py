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
# Idle with Teams in the background
#
# Setup instructions:
#   Run teams_install
##

import logging
import time
import os
import core.app_scenario
from selenium.webdriver.common.keys import Keys
from core.parameters import Params
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import json


class Teams2Idle(core.app_scenario.Scenario):
    '''
    Teams is launched and then minimized to run in the background for the duration of the test.
    '''
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'duration', '300')  # Seconds
    Params.setDefault(module, 'minimize_all', '1')
    Params.setDefault(module, 'minimize_teams_only', '0')

    # Get parameters
    duration = Params.get(module, 'duration')
    new_teams = Params.get("teams", 'new_teams')
    new_teams = "1"
    minimize_all = Params.get(module, 'minimize_all')
    minimize_teams_only = Params.get(module, 'minimize_teams_only')


    # Local parameters
    prep_scenarios = [""]

    def prepCheck(self):
        assert_list = ""        
        if assert_list != "":
            self._assert(assert_list)

    def setUp(self):
        self._call([(self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"), (self.dut_resolved_ip + " " + self.app_port)], blocking=False)
        time.sleep(1)
        desired_caps = {}
        desired_caps["app"] = "Root"
        self.desktop = self._launchApp(desired_caps, track_driver = False)
        self.driver = self.desktop

        # Call tool early callbacks, particularly to get video recording of the setup
        self.toolCallBacks("testBeginEarlyCallback")

        # Clear out any previous downloaded logs.
        self._call(['powershell.exe', 'Remove-Item -Force -Recurse -Path "~\Downloads\MSTeams*"'])

        logging.debug("Starting Teams")
        # First launch may only put icon in status bar.
        self._call(["powershell", "start msteams:"])
        time.sleep(5)
        # Second launch opens window in foreground.
        self._call(["powershell", "start msteams:"])
        time.sleep(5)

        try:
            self.desktop.find_element_by_xpath("//*[contains(@Name, 'Got it')]").click()
            time.sleep(5)
        except:
            pass

        # # Switch to new teams if available and prompted
        # try:
        #     WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'Do you want to switch back')]")))
        #     logging.info("Prompted to use new Teams.")
        #     if self.new_teams == '1':
        #         WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'Keep using')]"))).click()
        #         logging.debug("Selecting new Teams")
        #     else:
        #         WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'Yes, switch back')]"))).click()
        #         logging.debug("Selecting old Teams")
        #         time.sleep(10)
        # except:
        #     pass

        # # Second possible prompt to try the new Teams builds
        # try:
        #     WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'Get it now')]"))).click()
        #     logging.info("Prompted in app to try the new Teams. Clicking to try and dismiss.")
        #     time.sleep(10)
        # except:
        #     pass

        # # Third possible switch to new teams if available and prompted
        # try:
        #     WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'use the new Teams')]")))
        #     logging.info("Prompted to use new Teams.")
        #     if self.new_teams == '1':
        #         WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'Yes, use the new Teams')]"))).click()
        #         logging.debug("Selecting new Teams")
        #     else:
        #         WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'Not right now')]"))).click()
        #         logging.debug("Selecting old Teams")
        #         time.sleep(10)
        # except:
        #     pass

        # new_teams_available = False
        # try:
        #     # Look for New Teams toggle
        #     try:
        #         new_teams_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//CheckBox[contains(@Name, 'Try the new Teams')]")))
        #     except:
        #         new_teams_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'New Teams')]")))

        #     logging.debug("New Teams Option Toggle Found")
        #     new_teams_available = True
        # except:
        #     try:
        #         WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.NAME,"Settings and more")))
        #         elmt = self.driver.find_element_by_xpath("//*[contains(@Name, 'Settings and more')]")
        #         self.clickCenter(self.driver, elmt)
        #         time.sleep(2)

        #         # Look for New Teams toggle
        #         try:
        #             new_teams_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//CheckBox[contains(@Name, 'Try the new Teams')]")))
        #         except:
        #             new_teams_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'New Teams')]")))

        #         logging.debug("New Teams Option Toggle Found in Settings")
        #         new_teams_available = True

        #     except:
        #         logging.debug("New Teams Option Toggle Not Found in Settings")

        # if new_teams_available:
        #     if self.new_teams == '1':
        #         if not new_teams_button.is_selected():
        #             logging.info("New Teams not set, changing to New Teams")
        #             new_teams_button.click()
        #             time.sleep(10)
        #             try:
        #                 self.driver.find_element_by_name("Get it now").click()
        #             except:
        #                 pass
        #             time.sleep(15)
        #             WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'Microsoft Teams')]")))
        #             logging.debug("Teams window found")
        #             try:
        #                 WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'Pick an account')]")))
        #                 ActionChains(self.desktop).send_keys(Keys.ENTER).perform()
        #             except:
        #                 pass

        #             try:
        #                 whats_new = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH,"//dialog[contains(@Name, 'What's new in Teams')]")))
        #                 logging.debug("Found What's New dialog, closing prompt")
        #                 whats_new.find_element_by_name("Close").click()
        #             except:
        #                 logging.debug("What's New dialog not found")
        #                 pass
        #     else:
        #         if new_teams_button.is_selected():
        #             logging.info("Found using New Teams build, switching to old Teams")
        #             new_teams_button.click()
        #             time.sleep(5)
        #             WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.XPATH,"//*[contains(@Name, 'Microsoft Teams')]")))
        #             logging.debug("Teams window found")
        # else:
        #     if self.new_teams == '1':
        #         raise Exception('"Try the new Teams" Toggle not found! Is your account enabled for the new Teams experience?')


        if self.minimize_all == '1':
            # Minimize all windows
            self._call(["powershell.exe", '-command "$x = New-Object -ComObject Shell.Application; $x.minimizeall()"'])

        elif self.minimize_teams_only == '1':
            # Minimize Teams window
            ActionChains(self.driver).key_down(Keys.LEFT_ALT).key_down(Keys.SPACE).key_up(Keys.SPACE).key_up(Keys.LEFT_ALT).perform()
            time.sleep(3)
            ActionChains(self.driver).key_down("n").key_up("n").perform()


        # Long sleep to enter teams idle power period (5min + 30s for extra)
        logging.info("Waiting 5.5 minutes for Teams idle state to be achieved")
        time.sleep(330)

        # Base Class Call
        core.app_scenario.Scenario.setUp(self)


    def runTest(self):
        logging.info("Measuring idle for " + str(self.duration) + " seconds")
        time.sleep(float(self.duration))


    def tearDown(self):
        logging.info("Performing teardown.")
        # Call the test end callback to stop power recording.
        self._callback(Params.get('global', 'callback_test_end'))

        # dump call logs
        logging.debug("Dumping call logs before closing Teams")
        # Clean Downloads folder
        self._call(['powershell.exe', 'Remove-Item -Force -Recurse -Path "~\Downloads\MSTeams*"'])
        time.sleep(1)

        # Call base tearDown(), except for the callback_test_end, since that was called above.
        core.app_scenario.Scenario.tearDown(self, callback_test_end="")


    def kill(self):
        logging.debug("Closing Teams")
        try:
            self._kill("Teams.exe")
        except:
            pass
        
        try:
            self._kill("msteams.exe")
        except:
            pass

        try:
            self._kill("ms-teams.exe")
        except:
            pass

        time.sleep(5)

        try:
            self._kill("winappdriver.exe")
        except:
            pass

        try:
            logging.debug("Killing " + "Teams.exe")
            # Do it again because some windows can still be left open
            self._kill("Teams.exe", force = True)
        except:
            pass

        try:
            logging.debug("Killing " + "msteams.exe")
            # Do it again because some windows can still be left open
            self._kill("msteams.exe", force = True)
        except:
            pass

        try:
            logging.debug("Killing " + "ms-teams.exe")
            # Do it again because some windows can still be left open
            self._kill("ms-teams.exe", force = True)
        except:
            pass

        
    def clickCenter(self, driver, elem):
        ActionChains(driver).move_to_element(elem).click().perform()
