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
# Prep for Minecraft
#
# Setup instructions:
#   Download Minecraft Trial from the store.
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


class Minecraft_Prep_Store(core.scenarios.app_scenario.Scenario):
    module = __module__.split('.')[-1]
   
    is_prep = True

    def runTest(self):
        logging.info("Launching WinappDriver.exe on DUT.")
        self._call([(self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"), (self.dut_resolved_ip + " " + self.app_port)], blocking=False)
        time.sleep(1)

        # Launch store
        desired_caps = {}
        desired_caps["app"] = "Root"
        driver = self._launchApp(desired_caps)
        # start_elem = self._get_search_button(driver)
        # start_elem.click()
        # time.sleep(5)
        # start_elem.send_keys("app:store")
        # time.sleep(2)
        # start_elem.send_keys(Keys.ENTER)
        # time.sleep(5)

        # # Search for Minecraft
        # # try:
        # #     driver.find_element_by_name("Microsoft Store").find_element_by_name("Search").click()
        # # except:
        # #     driver.find_element_by_name("Microsoft Store").find_element_by_name("Search button").click()
        # # time.sleep(1)
        # search = driver.find_element_by_name("Microsoft Store").find_element_by_name("Search")
        # search.click()
        # search.send_keys("Minecraft for Windows" + Keys.ENTER)
        # time.sleep(10)
        self._call(["cmd.exe", '/C start ms-windows-store://pdp/?ProductId=9NBLGGH2JHXJ'])
        time.sleep(10)

        # Click Minecraft for Windows 10
        try:
            driver.find_element_by_name("Minecraft for Windows").click()
        except:
            driver.find_element_by_name("Minecraft for Windows 10").click()
        time.sleep(8)
        # self._page_source(driver)

        # try:
        #     # Install Minecraft app from store
        #     driver.find_element_by_xpath("//*[contains(@Name, 'Minecraft for Windows 10')]").click()
        #     logging.info("Minecraft is not installed")
        #     time.sleep(10)
        try:
            # If already isntalled, try to play
            ActionChains(driver).move_by_offset(-10, 10).perform()
            time.sleep(2)
            try:
                driver.find_element_by_name("Play").click()
            except:
                driver.find_element_by_name("Open trial").click()
            # Adding sleep to allow Minecraft to open
            time.sleep(15)
        except:
            # Not installed, try to install

            # Look for Minecraft Village & Pillage and click to stabilize location of install trial button
            try:
                driver.find_element_by_accessibility_id("AppIdentityTrialButton").click()
                logging.info("Installing free trial")
                time.sleep(2)
            except:
                logging.info("Free trial button not found")
                pass

                # Look for free trial button and click
                try:
                    driver.find_element_by_accessibility_id("dynamicImage_image_picture").click()
                    logging.info("Clicked Minecraft image")
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'Install Trial'))).click()
                    logging.info("Installing trial")
                    time.sleep(2)
                except:
                    try:
                        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, '//*[@Name="Free Trial" or @Name="Free trial"]'))).click()
                        logging.info("Installing free trial")
                        time.sleep(2)
                    except:
                        logging.info("Free Trial not found")
                        # Look for free trial in more options menu
                        try:
                            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'More options'))).click()
                            logging.info("Clicked More options")
                            time.sleep(2)
                            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'Free Trial'))).click()
                            logging.info("Installing free trial")
                            time.sleep(2)
                        except:
                            logging.info("More options and Free Trial not found")
                            pass

                            # Keeping older method of add to cart
                            try:
                                driver.find_element_by_xpath("//*[contains(@Name,'Add to cart')]").click()
                                logging.info("Free trial added to cart")
                                time.sleep(15)
                                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'Free Trial'))).click()
                                logging.info("Installing free trial after adding to cart")
                            except:
                                logging.info("Add to cart and Installing free trial not found")
                                self.fail("Minecraft installation not completed")
            # Handle installing gaming components popup
            try:
                logging.info("looking for downloading gaming components popup")
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//Button[@Name="Download"]'))).click()
                time.sleep(60)
            except:
                pass
            
            # Handle install popup
            try:
                logging.info("looking for install popup")
                WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, '//Button[@Name="Install"]'))).click()
                try:
                    time.sleep(5)
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    #WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//Button[@Name="Cancel"]'))).click()
                except:
                    pass
            except:
                logging.info("Install popup not found.")

            # Waiting for play button after installing Minecraft, button becomes visible by winappdriver before installation is complete and causes failure.  May need to increase time
            time.sleep(60)
            # WebDriverWait(driver, 600).until(EC.element_to_be_clickable((By.NAME, "Play"))).click()
            # WebDriverWait(driver, 600).until(EC.element_to_be_clickable((By.NAME, "Open trial"))).click()
            play_button = WebDriverWait(driver, 600).until(self.element_clickable_by_names)
            
            # look for Minecraft.Windows.exe by traversing through C:\XboxGames and use that path to unblock firewall
            minecraft_exe_path = '"C:\\XboxGames\\Minecraft for Windows\\Content\\Minecraft.Windows.exe"'
            
            # check if path exists on dut
            if self._call(["cmd.exe", '/c if exist ' + minecraft_exe_path + ' echo exists'], expected_exit_code="") == "exists":
                logging.info("Minecraft.Windows.exe found, adding firewall rules.")
                # Add firewall rules for the found executable
                self._call(["cmd.exe", f'/C netsh.exe advfirewall firewall add rule name="Minecraft for Windows" program={minecraft_exe_path} dir=in action=allow enable=yes localport=any protocol=TCP profile=public,private,domain'])
                self._call(["cmd.exe", f'/C netsh.exe advfirewall firewall add rule name="Minecraft for Windows" program={minecraft_exe_path} dir=in action=allow enable=yes localport=any protocol=UDP profile=public,private,domain'])
                logging.info("Firewall rules added for Minecraft")
            else:
                logging.warning("Minecraft.Windows.exe not found")

            play_button.click()
            # Adding sleep to allow Minecraft to open
            time.sleep(15)
            
        # except:
        #     # TODO: Open minecraft
        #     driver.find_element_by_xpath("//*[contains(@Name, 'Minecraft, App')]").click()
        #     logging.info("Minecraft is installed")
        #     time.sleep(5)
        #     pass

        # Try to handle xbox sign in popup
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,'Continue'))).click()
            time.sleep(5)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,'Save & continue'))).click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,'Only required data'))).click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,'Continue'))).click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,'Let\'s go'))).click()
            time.sleep(10)
        except:
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,'Let\'s go'))).click()
                time.sleep(5)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,'Only required data'))).click()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,'Continue'))).click()
                time.sleep(10)
            except:
                pass

        # Launched minecraft do 1st set up
        try:
            # mc_driver = self.getDriverFromWin(driver.find_element_by_name("Minecraft"))
            mc_driver = self.getDriverFromWin(WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME,'Minecraft'))))
            mc_driver.maximize_window()
            time.sleep(5)
            mc_driver.find_element_by_name("Minecraft").send_keys(Keys.ARROW_DOWN)
            time.sleep(1)
            mc_driver.find_element_by_name("Minecraft").send_keys(Keys.ENTER)
            time.sleep(3)
            mc_driver.find_element_by_name("Minecraft").send_keys(Keys.ESCAPE)
            time.sleep(3)
            mc_driver.close()
        except:
            logging.info("Minecraft not found, searching for Minecraft for Windows 10")
            mcwin_driver = self.getDrivesrFromWin(driver.find_element_by_name("Minecraft for Windows 10"))
            mcwin_driver.find_element_by_name("Minecraft for Windows 10").send_keys(Keys.ESCAPE)
            time.sleep(3)
            mcwin_driver.close()

        # Close Store, keep here so installation is not closed
        try:
            store_driver = self.getDriverFromWin(driver.find_element_by_name("Microsoft Store"))
            store_driver.close()
            time.sleep(5)
        except:
            logging.info("Microsoft Store not found")
  
    def element_clickable_by_names(self, driver):
        # Check for Play or Open trial button
        for name in ["Open trial", "Play"]:
            try:
                element = driver.find_element(By.NAME, name)
                # Check if element is displayed and enabled (clickable)
                if element.is_displayed() and element.is_enabled():
                    return element
            except NoSuchElementException:
                continue
        return False  # When neither element is found/clickable
    
    def getWindowHandle(self, win):
        win_handle = int(win.get_attribute("NativeWindowHandle"))
        win_handle = format(win_handle, 'x') # convert to hex string
        return win_handle

    # def getDriverFromWin(self, win):
    #     win_handle = self.getWindowHandle(win)
    #     # Launch new session attached to the window
    #     desired_caps = {}
    #     desired_caps["appTopLevelWindow"] = win_handle
    #     logging.info("Connecting to window.")      
    #     driver = self._launchApp(desired_caps, track_driver = False)
    #     logging.info("Connected to window.")
    #     time.sleep(1)  
    #     driver.switch_to_window(win_handle)
    #     driver.maximize_window()
    #     return driver

    
    def getDriverFromWin(self, win):
        win_handle = self.getWindowHandle(win)

        # Launch new session attached to the window
        desired_caps = {}
        desired_caps["appTopLevelWindow"] = win_handle
        driver = self._launchApp(desired_caps, track_driver = False)
        time.sleep(2)  
        driver.switch_to_window(win_handle)
        # driver.maximize_window()
        return driver

    def tearDown(self):
        logging.info("Performing teardown.")
        core.app_scenario.Scenario.tearDown(self)
        time.sleep(2)
        self._kill("WinAppDriver.exe")
        self.createPrepStatusControlFile()    

    def kill(self):
        try:
            logging.debug("Killing WinStore.App.exe")
            self._kill("WinStore.App.exe")
        except:
            pass