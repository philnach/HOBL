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

class Read4krand(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'block', '4')  # Block size in (K/M/G)bytes
    Params.setDefault(module, 'duration', '300')  # Seconds
    Params.setDefault(module, 'threads', '4')
    Params.setDefault(module, 'delay', '0')  # Seconds
    Params.setDefault(module, 'write', '0')  # Percentage
        
    # Get parameters
    block = Params.get(module, 'block')
    duration = Params.get(module, 'duration')
    threads = Params.get(module, 'threads')
    delay = Params.get(module, 'delay')
    write = Params.get(module, 'write')

    # Local parameters
    prep_scenarios = ["diskspd_prep"]
    
    def setUp(self):
        #Set test tool and file
        self.diskspd_tool = self.dut_exec_path + "\\diskspeed_resources\\diskspd.exe"
        self.dut_test_rand = self.dut_exec_path + "\\diskspeed_resources\\1Grand.tmp"
        core.app_scenario.Scenario.setUp(self)
        
    def runTest(self):
        # Performing sequential write test for 5 min
        logging.info("Performing " + self.block + "K block random read test for " + self.duration + " seconds")
        diskspd_data = self._call(["cmd.exe", "/C " + self.diskspd_tool + " -b" + self.block + "K -d" + self.duration + " -t" + self.threads + " -W" + self.delay + " -w" + self.write + " -o32 -r -S " + self.dut_test_rand])
