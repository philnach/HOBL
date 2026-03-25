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
import builtins
import logging
import core.app_scenario
import time, os
from core.parameters import Params

class Transfer8g(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    # Set default parameters

    # Local parameters
    prep_scenarios = ["diskspd_prep"]

        
    def setUp(self):
        #Set test tool and file
        self.diskspd_tool = self.dut_exec_path + "\\diskspeed_resources\\diskspd.exe"
        self.dut_test_file1 = self.dut_exec_path + "\\diskspeed_resources\\8G.tmp"
        self.dut_local_copy_path = "c:\\temp\\copy_test"

        # Deleting test file from test dir and purging from the recycle bin
        logging.info("Deleting previous test files from DUT.")
        self._call(["cmd.exe", "/C rmdir /s /q " + self.dut_local_copy_path + " >nul 2>&1"])
        logging.info("Creating copy_test directory.")
        self._call(["cmd.exe", "/C mkdir " + self.dut_local_copy_path])
        core.app_scenario.Scenario.setUp(self)
        
    def runTest(self):
        # Copying Test file to test directory
        logging.info("Copying 8G.tmp file to \\copy_test directory.")
        self._call(["cmd.exe", "/C copy " + self.dut_test_file1 + " " + self.dut_local_copy_path + "\\8G.tmp"])
