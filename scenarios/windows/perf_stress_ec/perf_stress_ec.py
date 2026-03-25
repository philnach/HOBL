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

import scenarios.app_scenario
from parameters import Params
import logging
import os
import subprocess
from . import default_params

# Description:
#   Automatically generated standard scenario.

class PerfStressEc(scenarios.app_scenario.Scenario):
    # Set default parameters:
    default_params.run()

    module = __module__.split('.')[-1]

    logging.info("Adding perf_utc tool for parsing perf metrics")
    # Use override so this still works when user passes global:tools on CLI.
    Params.setOverride("global", "tools", "+perf_utc")
    Params.setOverride("perf_utc", "provider", Params.get(module, "provider"))

    if Params.get(module, "stress_run") == "1":
        logging.info("Applying stress_run parameter profile")
        cpu_param = Params.get(module, "stress_cpu_target")
        if cpu_param not in ["25", "50", "75"]:
            cpu_param = "75"
            Params.setParam(module, "stress_cpu_target", cpu_param)
            logging.info("stress_run=1 and stress_cpu_target not provided; defaulting to 75 (high cpu load)")

        cpu_load_label = {
            "25": "low",
            "50": "medium",
            "75": "high",
        }.get(cpu_param, "high")
        logging.info(f"stress_cpu_target={cpu_param}% ({cpu_load_label} cpu load)")

    actions = None

    def setUp(self):
        # Load actions JSON.
        actions_json = os.path.join(os.path.dirname(__file__), "perf_stress_ec.json")
        self.actions = self.load_action_json(actions_json)

        # Execute Setup actions, if they exist
        setup_action = self._find_next_type("Setup", json=self.actions)
        if setup_action is not None:
            self.run_actions(setup_action["children"])

        # Call base class setUp() to dump config, call tool callbacks, and start measurment
        scenarios.app_scenario.Scenario.setUp(self)


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
        scenarios.app_scenario.Scenario.tearDown(self)

        # Execute Teardown actions, if they exist
        teardown_action = self._find_next_type("Teardown", json=self.actions)
        if teardown_action is not None:
            self.run_actions(teardown_action["children"])


    def kill(self):
        # In case of scenario failure or termination, force-stop background stress tasks.
        try:
            stop_script = os.path.join(self.dut_exec_path, "Stop_PerfStress_Background.ps1")
            self._call([
                "cmd.exe",
                f"/C powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"{stop_script}\""
            ], expected_exit_code="")
        except Exception as ex:
            logging.warning(f"Failed to execute Stop_PerfStress_Background.ps1 during kill(): {ex}")

        # Fallback kill list in case script execution is interrupted.
        for proc_name in ["python.exe", "py.exe", "pwsh.exe", "powershell.exe"]:
            try:
                self._kill(proc_name, force=True)
            except subprocess.TimeoutExpired:
                logging.warning(f"Timed out killing {proc_name} in kill()")
            except Exception:
                pass

        return
