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
# mlperf building Workload
##

import logging
import os
import core.app_scenario
from core.parameters import Params
import time

class mlperf(core.app_scenario.Scenario):

    module = __module__.split('.')[-1]
    prep_version = "6"
    resources = module + "_resources"


    # Set default parameters
    # config_file is set to Phi3.5 WindowsML QNN NPU by default, which, is the config file for Qualcomm.  
    # Running mlperf script on any other Windows device will fail.
    Params.setDefault(module, 'loops', '1')
    Params.setDefault(module, 'config_file', 'Config_Phi3.5_WindowsML_QNN_NPU.json')

    def setUp(self):
        # Get parameters
        self.platform = Params.get('global', 'platform')
        self.loops = Params.get(self.module, 'loops')
        self.config_file = Params.get(self.module, 'config_file')
        self.dut_architecture = Params.get('global', 'dut_architecture')

        self.mlperf_client_zip_path = ''
        self.mlperf_client_path = ''
        if self.dut_architecture == 'arm64':
            # Arm64 device is assumed to be a Qualcomm device and Qualcomm version of MLPerf client.
            self.artifact_name = 'mlperf-arm'
            self.mlperf_client_package = 'mlperf-client-offline-arm64.zip'
            self.mlperf_client_zip_path = f'C:\\hobl_bin\\mlperf\\{self.mlperf_client_package}'
            self.mlperf_client_path = 'C:\\hobl_bin\\mlperf\\phi3.5'
        else:
            logging.error(f"mlperf scenario not supported for CPU architecture {self.dut_architecture}")
            self.fail(f"mlperf scenario not supported for architecture {self.dut_architecture}")

        self.target = f"{self.dut_exec_path}\\{self.resources}"

        # Test if already set up
        if self.checkPrepStatus([self.module + self.prep_version]):
            logging.info("Preparing for first use.")

            # Download offline package
            logging.info("Downloading offline package to Host.")
            self._check_and_download(f"{self.artifact_name}", path = f"scenarios\\windows\\{self.module}")
            logging.info("Uploading offline package to DUT.")
            self._upload(f"scenarios\\windows\\{self.module}\\{self.artifact_name}\\{self.mlperf_client_package}", f"{self.dut_exec_path}\\{self.module}")

            # Download QNNEP package for Qualcomm devices
            if self.dut_architecture == 'arm64':
                self.qnnep_package = 'qnnep_arm'
                logging.info("Downloading QNNEP package to Host.")
                self._check_and_download(f"{self.qnnep_package}", path = f"scenarios\\windows\\{self.module}")
                logging.info("Uploading QNNEP package to DUT.")
                self._upload(f"scenarios\\windows\\{self.module}\\{self.qnnep_package}", f"{self.dut_exec_path}\\{self.module}")

            # Copy over resources to DUT
            logging.info(f"Uploading test files to {self.target}")
            self._upload(f"scenarios\\windows\\{self.module}\\{self.resources}", self.dut_exec_path)

            # Excute prep script
            logging.info("Executing prep, this make take 10-15 minutes...")
            arg = ''
            if self.mlperf_client_zip_path != '':
                arg = f"-mlperfClientPath {self.mlperf_client_zip_path}"
            try:
                self._call(["pwsh", f"{self.target}\\{self.module}_prep.ps1 {arg}"])
            finally:
                self._copy_data_from_remote(self.result_dir)
            self.createPrepStatusControlFile(self.prep_version)

        # Call base class setUp() to dump config, call tool callbacks, and start measurment
        core.app_scenario.Scenario.setUp(self)


    def runTest(self):
        for i in range(int(self.loops)):
            logging.info(f"Running loop {i + 1}")
            self._call(["pwsh", f"{self.target}\\{self.module}_run.ps1 -mlperfConfigFile {self.mlperf_client_path}\\{self.config_file}"], timeout=7200)


    def tearDown(self):
        logging.info("Performing teardown.")
        # Call base class tearDown() to stop measurment, copy back data from DUT, and call tool callbacks
        core.app_scenario.Scenario.tearDown(self)

        # logging.info("Executing teardown script.")
        # self._call(["pwsh", f"{self.target}\\{self.module}_teardown.ps1"])


    def kill(self):
        try:
            logging.debug("Killing powershell shell")
            self._kill("pwsh.exe")
        except:
            pass

