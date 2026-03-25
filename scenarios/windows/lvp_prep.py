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
# Prep for Local Video Playback
# 
# Setup instructions:
##

import builtins
import os
import logging
import sys
import core.app_scenario
from core.parameters import Params
import time
from appium import webdriver
from selenium.common.exceptions import NoSuchElementException


class LvpPrep(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'video_file', 'ToS-4k-1920.mov')
    Params.setDefault(module, 'video_url', 'http://ftp.nluug.nl/pub/graphics/blender/demo/movies/ToS/ToS-4k-1920.mov')
    # default time to wait for application to populate its video library
    Params.setDefault(module, 'duration', '15')  # Seconds

    # Get parameters
    video_file = Params.get(module, 'video_file')
    video_url = Params.get(module, 'video_url')
    dut_architecture = Params.get('global', 'dut_architecture')
    # wait time for application to populate its video library
    duration = Params.get(module, 'duration')

    is_prep = True


    def runTest(self):
        if Params.get("global", "local_execution") == "0":
            self.userprofile = self._call(["cmd.exe", "/C echo %USERPROFILE%"])
        else:
            self.userprofile = os.environ['USERPROFILE']


        source = os.path.join("downloads", self.video_file)
        dest = os.path.join(self.userprofile, "Videos")
        dest_file = os.path.join(dest, self.video_file)

        # Download video if not already present
        self._check_and_download(self.video_file, "downloads", url=self.video_url)

        # Check if video file already exists on DUT and upload if not.
        self._upload(source, dest, check_modified=True)

        # Copy over resources to DUT
        logging.info("Uploading additional test files")
        self._upload("scenarios\\windows\\lvp\\lvp_wrapper.cmd", os.path.join(self.dut_exec_path, "lvp_resources"))
        self._upload("utilities\\proprietary\\radio\\" + self.dut_architecture + "\\RadioEnable.exe", os.path.join(self.dut_exec_path, "radio"))
        self._upload("utilities\\proprietary\\radio\\" + self.dut_architecture + "\\AirplaneMode.exe", os.path.join(self.dut_exec_path, "radio"))
        self._upload("utilities\\proprietary\\sleep\\sleep.exe", os.path.join(self.dut_exec_path, "sleep"))

        # Code added to launch video player software in order to give it time to populate its video library.
        # Avoids an issue experienced by some devices where LVP will fail to find the video file before failing the test
        logging.info("Launching WinAppDriver.exe on DUT.")

        self._call([(self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"), (self.dut_resolved_ip + " " + self.app_port)], blocking=False)
        time.sleep(1)

        logging.info("Launching LVP")
        desired_caps = {}

        # try:
        desired_caps["app"] = "Microsoft.ZuneMusic_8wekyb3d8bbwe!microsoft.ZuneMusic"
        driver = self._launchApp(desired_caps)

        # Waiting for a specified period of time to allow the software to update their video library
        logging.info(f"Waiting for {self.duration} seconds to allow the video library to populate.")
        time.sleep(float(self.duration))

        logging.info("Checking the Video library tab to make sure the video is available.")
        driver.find_element_by_name("Video library").click()
        time.sleep(5)
        # except:
        #     desired_caps["app"] = "Microsoft.ZuneVideo_8wekyb3d8bbwe!microsoft.ZuneVideo"
        #     driver = self._launchApp(desired_caps)

        #     # Waiting for a specified period of time to allow the software to update their video library
        #     logging.info(f"Waiting for {self.duration} seconds to allow the video library to populate.")
        #     time.sleep(float(self.duration))

        #     logging.info("Checking the Personal tab to make sure the video is available.")
        #     driver.find_element_by_name("Personal").click()
        #     time.sleep(5)

        #     # Look to see if 'What's New' pop-up exists
        #     try:
        #         logging.info("Checking for What's New pop-up.")
        #         driver.find_element_by_name("What's new popup got it").click()

        #         logging.info("Pop-up dismissed.")
        #         time.sleep(2)
        #     except NoSuchElementException:
        #         logging.info("Pop-up not found.")
        self.createPrepStatusControlFile()


    def tearDown(self):
        core.app_scenario.Scenario.tearDown(self)

        self._kill("WinAppDriver.exe")


    def kill(self):
        try:
            logging.debug("Killing Music.UI.exe")
            self._kill("Music.UI.exe")
        except:
            pass

        try:
            logging.debug("Killing Video.UI.exe")
            self._kill("Video.UI.exe")
        except:
            pass
