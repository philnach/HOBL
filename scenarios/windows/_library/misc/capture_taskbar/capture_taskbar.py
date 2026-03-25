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
import os
import core.call_rpc as rpc

# Description:
#   Automatically generated standard scenario.

class CaptureTaskbar(core.app_scenario.Scenario):
    # Set default parameters:
    Params.setDefault('capture_taskbar', 'duration', '1')

    # Get parameter values:
    duration = Params.get('capture_taskbar', 'duration')


    def setUp(self):
        result = rpc.plugin_load(self.dut_ip, self.rpc_port, "InputInject", "InputInject.Application", "C:\\hobl_bin\\InputInject\\InputInject.dll")
        # Load actions JSON.
        actions_json = os.path.join(os.path.dirname(__file__), "capture_taskbar.json")
        self.load_action_json(actions_json)

        # Call base class setUp() to dump config, call tool callbacks, and start measurment
        core.app_scenario.Scenario.setUp(self)


    def runTest(self):
        # Loop through actions in JSON file and process:
        while(1):
            result = self.get_next_action()
            if result == 0 or result == 1:
                # Reached end of action list
                break
            logging.info("Performing action: " + str(result["id"]) + " " + str(result["type"]) + " " + str(result["description"]))
            self.process_action(result)


    def tearDown(self):
        # Call base class tearDown() to stop measurment, copy back data from DUT, and call tool callbacks
        core.app_scenario.Scenario.tearDown(self)

        # Add any additional tear down code here:

    
    def kill(self):
        # In case of scenario failure or termination, kill any applications left open here:

        return