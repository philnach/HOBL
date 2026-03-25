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
from . import default_params

# Description:
#   Automatically generated standard scenario.

class TeamsVerge(core.app_scenario.Scenario):
    # Set default parameters:
    default_params.run()

    prep_scenarios = ["teams_install", "edge_install", "web_prep"]

    actions = None

    def setUp(self):
        # Load actions JSON.
        actions_json = os.path.join(os.path.dirname(__file__), "teams_verge.json")
        self.actions = self.load_action_json(actions_json)

        # Execute Setup actions, if they exist
        setup_action = self._find_next_type("Setup", json=self.actions)
        if setup_action is not None:
            self.run_actions(setup_action["children"])

        # Call base class setUp() to dump config, call tool callbacks, and start measurment
        core.app_scenario.Scenario.setUp(self)


    def runTest(self):
        # Execute Run Test actions, if they exist
        runtest_action = self._find_next_type("Run Test", json=self.actions)
        if runtest_action is not None:
            self.run_actions(runtest_action["children"])
            return
        
        # If no "Run Test", "Setup", or "Teardown" specified, then just execute the whole list
        setup_action = self._find_next_type("Setup", json=self.actions)
        teardown_action = self._find_next_type("Teardown", json=self.actions)
        if runtest_action is None and setup_action is None and teardown_action is None:
            self.run_actions(self.actions)


    def tearDown(self):
        # Call base class tearDown() to stop measurment, copy back data from DUT, and call tool callbacks
        core.app_scenario.Scenario.tearDown(self)

        # Execute Teardown actions, if they exist
        teardown_action = self._find_next_type("Teardown", json=self.actions)
        if teardown_action is not None:
            self.run_actions(teardown_action["children"])


    def kill(self):
        # In case of scenario failure or termination, kill any applications left open here:
        try:
            logging.debug("Killing " + "ms-teams.exe")
            if self.platform.lower() == "w365":
                self._run_with_inputinject("cmd.exe /c tasklist /nh /fo csv /fi \"IMAGENAME eq 'ms-teams.exe'\"")
            else:
                self._kill("ms-teams.exe", force = True)
        except:
            pass

        try:
            # Do it again because some windows can still be left open
            logging.debug("Killing " + "ms-teams.exe")
            if self.platform.lower() == "w365":
                self._run_with_inputinject("cmd.exe /c tasklist /nh /fo csv /fi \"IMAGENAME eq 'ms-teams.exe'\"")
            else:
                self._kill("ms-teams.exe", force = True)
        except:
            pass

        try:
            self._kill("msedge.exe")
        except:
            pass
        try:
            self._kill("chrome.exe")
        except:
            pass
        time.sleep(3)
        self._web_replay_kill()
        return