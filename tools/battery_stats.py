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
# Tool wrapper for audio control

from builtins import str
from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import os
import decimal
import time


class Tool(Scenario):
    '''
    Deprecated.
    '''
    module = __module__.split('.')[-1]

    # Set default parameters
    #Params.setDefault(module, 'mute', "False")

    # Get parameters
    platform = Params.get('global', 'platform')
    result_dir = Params.get('global', 'result_dir')
    dut_ip = Params.get('global', 'dut_ip')
    #mute = Params.get(module, 'mute')

    def initCallback(self, scenario):

        # Enable full wake history

        if self.platform.lower() == "android":

            logging.info("Enable wake history and reset battery stats")

            self._host_call("adb -s " + self.dut_ip + ":5555 shell dumpsys batterystats --enable full-wake-history", expected_exit_code="")
            time.sleep(5)

            # Reset battery statistics

            self._host_call("adb -s " + self.dut_ip + ":5555 shell dumpsys batterystats --reset", expected_exit_code="")
            time.sleep(5)

        return

    def testBeginCallback(self):
        pass

    def testEndCallback(self):
        pass

    def dataReadyCallback(self):

        
        if self.platform.lower() == "android":
            
            # Use adb command to fetch batery stats
            
            logging.info("Saving battery stats to: " + self.result_dir)

            # Dump battery stats

            self._host_call("adb -s " + self.dut_ip + ":5555 shell dumpsys batterystats > " + self.result_dir + "\\batterystats.txt", expected_exit_code="")
            time.sleep(5)

        return




