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
# AI Foundry Local Workload
##

import logging
import os
import core.app_scenario
from core.parameters import Params
import time

class Foundrylocal(core.app_scenario.Scenario):

    module = __module__.split('.')[-1]
    prep_version = "6"
    resources = module + "_resources"


    # Set default parameters
    Params.setDefault(module, 'loops', '1')
    Params.setDefault(module, 'model', 'Phi-3.5-mini-instruct-generic-cpu')
    Params.setDefault(module, 'prompt', 'What is the meaning of life?')


    def setUp(self):
        # Get parameters
        self.platform = Params.get('global', 'platform')
        self.loops = Params.get(self.module, 'loops')
        self.model = Params.get(self.module, 'model')
        self.prompt = Params.get(self.module, 'prompt')

        self.target = f"{self.dut_exec_path}\\{self.resources}"

        # Test if already set up
        if self.checkPrepStatus([self.module + self.prep_version]):
            logging.info("Preparing for first use.")

            # Copy over resources to DUT
            logging.info(f"Uploading test files to {self.target}")
            self._upload(f"scenarios\\windows\\{self.module}\\{self.resources}", self.dut_exec_path)

            # Execute prep script (installs Foundry Local via winget)
            logging.info("Executing prep, this may take a few minutes...")
            try:
                self._call(["pwsh", f"{self.target}\\{self.module}_prep.ps1"], timeout=1800)
            finally:
                self._copy_data_from_remote(self.result_dir)
            self.createPrepStatusControlFile(self.prep_version)

        # Execute setup script (downloads the model)
        logging.info(f"Setting up model: {self.model}")
        try:
            self._call(["pwsh", f"{self.target}\\{self.module}_setup.ps1 -model {self.model}"], timeout=3600)
        finally:
            self._copy_data_from_remote(self.result_dir)

        # Call base class setUp() to dump config, call tool callbacks, and start measurement
        core.app_scenario.Scenario.setUp(self)


    def runTest(self):
        for i in range(int(self.loops)):
            logging.info(f"Running loop {i + 1}")
            self._call(["pwsh", f"{self.target}\\{self.module}_run.ps1 -model {self.model} -prompt \"{self.prompt}\""], timeout=600)


    def tearDown(self):
        logging.info("Performing teardown.")
        # Call base class tearDown() to stop measurement, copy back data from DUT, and call tool callbacks
        core.app_scenario.Scenario.tearDown(self)

        # Remove the model from cache
        logging.info(f"Removing model from cache: {self.model}")
        self._call(["pwsh", f"{self.target}\\{self.module}_teardown.ps1 -model {self.model}"])


    def kill(self):
        try:
            logging.debug("Killing powershell and foundry processes")
            self._kill("pwsh.exe")
            self._kill("foundry.exe")
        except:
            pass
