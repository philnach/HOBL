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
# Prep for Netflix app
#
# Setup instructions:
#   Install Netflix app from the store.
##
import builtins
import logging
import os
import time
import appium.common.exceptions as exceptions
from appium import webdriver
import core.app_scenario
import selenium.common.exceptions as exceptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from core.parameters import Params
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class Netflixapp_Prep(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
   
    # Set default parameters 
    # Params.setOverride("global", "collection_enabled", "0")
    Params.setDefault(module, 'netflix_username', '')
    Params.setDefault(module, 'netflix_password', '')
    Params.setDefault(module, 'netflix_user', '')

    # Get parameters
    netflix_username = Params.get('netflix', 'netflix_username')
    netflix_password = Params.get('netflix', 'netflix_password')
    netflix_user = Params.get('netflix', 'netflix_user')
    is_prep = True

    def runTest(self):
        logging.info("Launching WinappDriver.exe on DUT.")
        self._call([(self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"), (self.dut_resolved_ip + " " + self.app_port)], blocking=False)
        time.sleep(1)
        desired_caps = {}
        desired_caps["app"] = "Root"
        driver = self._launchApp(desired_caps)
        start_elem = self._get_search_button(driver)
        start_elem.click()
        time.sleep(5)
        start_elem.send_keys("app:Netflix")
        time.sleep(3)

        # Install Netflix app from store
        try:
            driver.find_element_by_xpath("//*[contains(@Name, 'Netflix, Install app')]").click()
            logging.info("Netflix is not installed")
            time.sleep(5)

            # Look for get button and click
            try:
                driver.find_element_by_name('Get').click()
                logging.info("Getting Netflix app")
                time.sleep(20)
            except:
                logging.info("Get not found")
                pass

                 # Look for install button and click
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'Install'))).click()
                    logging.info("Installing Netflix app")
                    time.sleep(20)
                except:
                    logging.info("Install not found")
            
        except:
            # Open Netflix app
            driver.find_element_by_xpath("//*[contains(@Name, 'Netflix')]").click()
            logging.info("Netflix is installed")
            time.sleep(5)
            pass

        # Look for launch button and click
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'Launch'))).click()
            logging.info("Launching Netflix app")
            time.sleep(20)
        except:
            logging.info("Launch not found")
            
        # Sign into the Netflix app
        try:
            sign = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'Sign in')))
            sign.click()
            time.sleep(2)
            username = driver.find_element_by_name("Email")
            username.click()
            username.send_keys(self.netflix_username)
            time.sleep(2)
            password = driver.find_element_by_name("Password")
            password.click()
            password.send_keys(self.netflix_password + Keys.RETURN)
            time.sleep(5)
            logging.info("Logging in.")
        except:
            logging.info("Account is already logged in.")
            pass

        # Click on user
        try: 
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, (self.netflix_user)))).click()
            #user.click()
            time.sleep(5)
        except:
            logging.info("User is already selected.")
            pass

        # Close Netflix
        try:
            netflix_driver = self.getDriverFromWin(driver.find_element_by_name("Netflix"))
            netflix_driver.close()
            time.sleep(5)
        except:
            logging.info("Netflix not found")
            pass
       
        # Close Store
        try:
            store_driver = self.getDriverFromWin(driver.find_element_by_name("Microsoft Store"))
            store_driver.close()
            time.sleep(5)
        except:
            logging.info("Microsoft Store not found")
            pass
  
    def getWindowHandle(self, win):
        win_handle = int(win.get_attribute("NativeWindowHandle"))
        win_handle = format(win_handle, 'x') # convert to hex string
        return win_handle

    def getDriverFromWin(self, win):
        win_handle = self.getWindowHandle(win)
        # Launch new session attached to the window
        desired_caps = {}
        desired_caps["appTopLevelWindow"] = win_handle
        logging.info("Connecting to window.")      
        driver = self._launchApp(desired_caps, track_driver = False)
        logging.info("Connected to window.")
        time.sleep(1)  
        driver.switch_to_window(win_handle)
        driver.maximize_window()
        return driver

    def tearDown(self):
        logging.info("Performing teardown.")
        core.app_scenario.Scenario.tearDown(self)
        time.sleep(2)
        self._kill("WinAppDriver.exe")
        self.createPrepStatusControlFile()    