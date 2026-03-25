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
import os
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import core.action_list

class recall(core.app_scenario.Scenario):

    module = __module__.split('.')[-1]
    # # Set default parameters
    Params.setDefault(module, 'loops', '1')
    Params.setDefault(module, 'training_module', 'recall')

    
    # Get parameters
    training_mode = Params.get('global', 'training_mode')
    training_module = Params.get(module, 'training_module')
    typing_delay = Params.get('global', 'typing_delay')
    browser = Params.get('global', 'browser')
    loops = Params.get(module, 'loops')
    duration = Params.get(module, 'duration')


    def setUp(self):

        if self.training_mode == "0":
            training_root, self.training_folder = self._find_latest_training_folder(self.training_module)
            if self.training_folder == "":
                self._assert("recall_training folder is missing on the Host.\n")
            local_training = training_root + os.sep + self.training_folder
            self._upload_json(local_training, self.dut_exec_path)
        else:
            logging.info("Training mode enabled")
            # Start WinAppDriver server
            self._call([(self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"), (self.dut_resolved_ip + " " + self.app_port + " /forcequit")], expected_exit_code="", blocking=False)
            time.sleep(1)

            # Connect to desktop to be able to launch apps with Start menu
            desired_caps = {}
            desired_caps["app"] = "Root"
            self.desktop = self._launchApp(desired_caps)
            self.desktop.implicitly_wait(0)

        # Call base class setUp() to start power measurment
        core.app_scenario.Scenario.setUp(self)
            # Create hobl_data folder
            # Tool init callback
            # Pre config_check
            # Tool begin callback
            # Start tracing
            # Test begin callback


    def runTest(self):
        if self.training_mode == "0":
            logging.info("Starting recall")
            #sub_start_time = time.time()
            self._call([os.path.join(self.dut_exec_path, "InputInject", "InputInject.exe"), os.path.join(self.dut_exec_path, self.training_folder, "recall.json")])
            #self._record_phase_time('phase1: short', sub_start_time, (time.time() - sub_start_time))
        else:
            logging.info("Starting training for recall")
            alist = action_list.ActionList(os.path.join(self.result_dir, "recall.json"))
            try:
                self.launchOrSwitchApp(alist, "Recall")
            except:
                self.fail("Recall app not found in taskbar. Recall app may not be supported.")
            alist.recordSleep(2, "sleep")
            self.launchOrSwitchApp(alist, "Start")
            alist.recordSleep(2, "sleep")
            self.launchOrSwitchApp(alist, "Recall")
            alist.recordSleep(5, "wait for recall to fully load")

            timeline_element = self.desktop.find_element_by_accessibility_id("TimelineScrollView")
            #element_location = timeline_element.location
            element_size = timeline_element.size

            logging.info("scrolling through timeline")
            # clicking through timeline
            for x in range(1, 10):
                mult = 0.1 * x
                x_offset = mult * element_size['width']
                y_offset = element_size['height']/2
                alist.recordClick(self.desktop, timeline_element, "click through timeline", x_offset = x_offset, y_offset = y_offset)
                alist.recordSleep(3, "sleep")

            logging.info("scrolling through timeline backwards")
            # clicking through timeline
            for x in range(10, 0, -1):
                mult = 0.08 * x
                x_offset = mult * element_size['width']
                y_offset = element_size['height']/2
                alist.recordClick(self.desktop, timeline_element, "click through timeline", x_offset = x_offset, y_offset = y_offset)
                alist.recordSleep(3, "sleep")    

            logging.info("searching in search bar")
            # Search something in recall
            recall_app = WebDriverWait(self.desktop, 60).until(EC.presence_of_element_located((By.XPATH,'//Window[contains(@Name,"Recall")]')))
            search = recall_app.find_element_by_name("Search")
            alist.recordClick(recall_app, search, "clicking search bar")
            alist.recordSleep(1, "sleep")
            alist.recordTypingElem(search, Keys.CONTROL + "a", "deleting search bar", int(self.typing_delay), perf="1")
            alist.recordTypingElem(search, Keys.DELETE, "delete", int(self.typing_delay), perf="1")
            alist.recordTypingElem(search, "Youtube", "search youtube", int(self.typing_delay), perf="1")
            alist.recordTypingElem(search, Keys.ENTER, "press enter key", int(self.typing_delay), perf="1")
            alist.recordSleep(10)

            # Click first result
            first_card = recall_app.find_element_by_accessibility_id("CardRoot")
            alist.recordClick(recall_app, first_card, "click 1st searched card")
            alist.recordSleep(5, "sleep")

            # toggle screenray
            #self._page_source(self.desktop)
            #screenray = recall_app.find_element_by_name("Screenray")
            screenray = WebDriverWait(recall_app, 30).until(EC.presence_of_element_located((By.XPATH,'//*[@Name="Screenray"]')))
            alist.recordClick(recall_app, screenray, "click screenray button")
            alist.recordSleep(2)
            alist.recordClick(recall_app, screenray, "click screenray button")
            alist.recordSleep(5, "wait for screenray to detect text")

            alist.saveRecording("recall")


    def launchOrSwitchApp(self, alist, app):
        # Check if app is already running
        self.active_driver = self.desktop
        apps_elem = self._get_app_tray(self.desktop)
        # start_button = self._get_start_button(self.desktop)
        if "edge" in app:
            id = None
            if app == "edge":
                id = "MSEdge"
            elif app == "edgedev":
                id = "MSEdgeDev"
            elif app == "edgebeta":
                id = "MSEdgeBeta"
            elif app == "edgecanary":
                id = "MSEdgeCanary"
            else:
                self.fail("Unsuported app name: " + app)
            try:
                app_button = apps_elem.find_element_by_accessibility_id(id)
            except:
                try:
                    app_button = apps_elem.find_element_by_accessibility_id("Appid: " + id)
                except Exception as e:
                    try:
                        app_button = apps_elem.find_element_by_xpath('//Button[contains(@AutomationId,"' + id + '")]')
                    except:
                        self._page_source(self.desktop)
                        raise e
        else:
            try:
                app_button = apps_elem.find_element_by_xpath('//Button[contains(@Name,"' + app + '")]')
            except Exception as e :
                self._page_source(self.desktop)
                raise e        
        #app_button = apps_elem.find_element_by_xpath('//Button[contains(@Name,"' + app + '")]')
        # If this the first call, we don't know if we are already focused on the desired app
        # So do the robust thing and click a known element (Start button) before switching to the desired task
        # Scratch that, we are going to the Start menu every time so that after a full training, you can playback a single phase.
        # if app not in self.open_apps:
        # alist.recordClick(self.desktop, start_button, "Start")
        # alist.recordSleep(1, "Sleep", False)
        alist.recordClick(self.desktop, app_button, "Click " + app + " in task bar")

    def tearDown(self):
        # Call base class tearDown() to stop power measurment
        logging.info("Closing recall App")
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
        try:
            logging.debug("killing winappdriver")
            self._kill("WinAppDriver.exe")
        except:
            pass
        
        try:
            logging.debug("killing recall")
            self._kill("AIXHost.exe")
        except:
            pass
