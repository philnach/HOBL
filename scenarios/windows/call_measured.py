
'''
//--------------------------------------------------------------
//
// HOBL
// Copyright(c) Microsoft Corporation
// All rights reserved.
//
// MIT License
//
// Permission is hereby granted, free of charge, to any person obtaining
// a copy of this software and associated documentation files(the 'Software'),
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
'''

##
# Calls executables on the DUT, either blocking or non-blocking. This Version also measures power and video record
#
# Setup instructions:
##

import builtins
import logging
import core.app_scenario
from core.parameters import Params
import os
import core.call_rpc as rpc

class CallMeasured(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'executable', '') # Specify full path on DUT to file to be executed
    Params.setDefault(module, 'arguments', '')
    Params.setDefault(module, 'source_path', '') # Will be copied to c:\hobl_bin befor test
    Params.setDefault(module, 'results_path', '') # Will be copied to c:\hobl_data after test
    Params.setDefault(module, 'blocking', '1')
    Params.setDefault(module, 'log_output', '1')
    Params.setDefault(module, 'expected_exit_code', '') # Expected exit code of the executable, if not 0, an error will be raised

    # Get parameters
    executable = Params.get(module, 'executable')
    arguments = Params.get(module, 'arguments')
    source_path = Params.get(module, 'source_path')
    results_path = Params.get(module, 'results_path')
    blocking = Params.get(module, 'blocking')
    log_output = Params.get(module, 'log_output')
    expected_exit_code = Params.get(module, 'expected_exit_code')

    # Override collection of config data, traces, and execution of callbacks 
    Params.setOverride("global", "collection_enabled", "1")

    # Local parameters
    prep_scenarios = []

    def setUp(self):
        core.app_scenario.Scenario.setUp(self)
        # if Params.get('global', 'local_execution') != '1':
        #     source_path = "C:\\simple_remote_*.log"
        #     self._call(["cmd.exe", '/c del ' + source_path], expected_exit_code="")
        #     self.dut_data_path = Params.getCalculated("dut_data_path")
        #     self._remote_make_dir(self.dut_data_path, True)


    def runTest(self):
        # Copy over any source file/folder
        if self.source_path != "":
            self._upload(self.source_path, self.dut_exec_path)

        # Make call to DUT
        logging.info("Executing call: " + self.executable + " " + self.arguments)
        output = self._call([self.executable, self.arguments], timeout=3600, blocking = (self.blocking == "1"), log_output = (self.log_output == "1"), expected_exit_code = self.expected_exit_code)
        if self.log_output == "1":
            logging.info("Output:")
            lines = output.split('\n')
            for line in lines:
                logging.info(line.strip("\r\n"))

        # Copy back specified results
        if Params.get('global', 'local_execution') !='1':
            
            logging.debug("Copying results from " + self.results_path + " to " + self.result_dir)
            if self.platform.lower() == "android":
                self._host_call("adb -s " + str(self.dut_ip) + ":5555 pull " + self.dut_data_path + " " + self.result_dir, expected_exit_code="")
            else:
                if self._check_remote_file_exists(self.dut_data_path):
                    if self.results_path != "" and self._check_remote_file_exists(self.results_path):
                        logging.info("Copying results to " + self.dut_data_path)
                        self._call(["cmd.exe", '/c copy ' + self.results_path + ' ' + self.dut_data_path], expected_exit_code="")

                    logging.debug("Copying SimpleRemote log file to " + self.dut_data_path)
                    log_path = "C:\\simple_remote_*.log"
                    self._call(["cmd.exe", '/c copy ' + log_path + ' ' + self.dut_data_path], expected_exit_code="")

                    rpc.download(self.dut_ip, self.rpc_port, self.dut_data_path, self.result_dir)

    def tearDown(self):
        core.app_scenario.Scenario.tearDown(self)
        return

