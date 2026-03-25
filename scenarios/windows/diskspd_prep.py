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
import time
from core.parameters import Params

class DiskspdPrep(core.app_scenario.Scenario):
    
    module = __module__.split('.')[-1]
    # Override collection of config data, traces, and execution of callbacks 
    # Params.setOverride("global", "collection_enabled", "0")
    is_prep = True

    def runTest(self):
        #Set test tool and file
        diskspd_tool = self.dut_exec_path + "\\diskspeed_resources\\diskspd.exe"
        dut_test_file1 = self.dut_exec_path + "\\diskspeed_resources\\8G.tmp"
        #dut_test_file2 = self.dut_exec_path + "\\diskspeed_resources\\1G.tmp"
        dut_test_seq = self.dut_exec_path + "\\diskspeed_resources\\1Gseq.tmp"
        dut_test_rand = self.dut_exec_path + "\\diskspeed_resources\\1Grand.tmp"

        # Copy over resources
        logging.info("Uploading Diskspd tools from hobl_bin\\scenarios\\diskspeed_resources to " + self.dut_exec_path)
        self._upload("utilities\\third_party\\diskspd.exe", self.dut_exec_path + "\\diskspeed_resources")

        # Generating the Test files to copy
        logging.info("Diskspd is generating 8GB test file.")
        self._call(["cmd.exe", "/C " + diskspd_tool + " -c8G " + dut_test_file1])
        logging.info("8G.tmp has been generated.")

        logging.info("Diskspd is generating 1GB sequential test file.")
        self._call(["cmd.exe", "/C " + diskspd_tool + " -b128k -o32 -t1 -W0 -s -S -w100 -c1G " + dut_test_seq])
        logging.info("1Gseq.tmp has been generated.")

        logging.info("Diskspd is generating 1GB random test file.")
        self._call(["cmd.exe", "/C " + diskspd_tool + " -b128k -o32 -t1 -W0 -r -S -w100 -c1G " + dut_test_rand])
        logging.info("1Grand.tmp has been generated.")

    def tearDown(self):
        self.createPrepStatusControlFile()
        logging.info("Performing teardown.")
        core.app_scenario.Scenario.tearDown(self)
        time.sleep(2)
        self._kill("WinAppDriver.exe")