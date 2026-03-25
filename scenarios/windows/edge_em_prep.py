#--------------------------------------------------------------
#
# HOBL
# Copyright(c) Microsoft Corporation
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files(the ""Software""),
# to deal in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
# OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#--------------------------------------------------------------

#Environment set up for the Bowser Efficiency Test

import builtins
import logging
import core.app_scenario
from core.parameters import Params
import time

class EdgeEMPrep(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    # Set default parameters
    Params.setDefault(module, 'efficiency_mode', 'default') 

    Params.setOverride("global", "prep_tools", "")
    is_prep = True
    efficiency_mode = Params.get(module, 'efficiency_mode')

    # Variables
    success = False

    def runTest(self):       
        # Set reg key to disable Efficiency Mode
        self._call(["cmd.exe", '/C reg delete "HKLM\\Software\\Policies\\Microsoft\\Edge\\EfficiencyModeEnabled" /f'], expected_exit_code="")
        self._call(["cmd.exe", '/C reg delete "HKLM\\Software\\Policies\\Microsoft\\Edge\\EfficiencyMode" /f'], expected_exit_code="")
        time.sleep(10)
        
        if self.efficiency_mode == 'disabled': #disable
            self._call(["cmd.exe", '/C reg add "HKLM\\Software\\Policies\\Microsoft\\Edge" /v EfficiencyModeEnabled /t REG_DWORD /d 0 /f'])
        elif self.efficiency_mode == 'maximum': #max
            # self._call(["cmd.exe", '/C reg add "HKLM\\Software\\Policies\\Microsoft\\Edge" /v EfficiencyModeEnabled /t REG_DWORD /d 1 /f'])
            self._call(["cmd.exe", '/C reg add "HKLM\\Software\\Policies\\Microsoft\\Edge" /v EfficiencyMode /t REG_DWORD /d 5 /f'])
        elif self.efficiency_mode == 'balanced': #balanced
            self._call(["cmd.exe", '/C reg add "HKLM\\Software\\Policies\\Microsoft\\Edge" /v EfficiencyModeEnabled /t REG_DWORD /d 1 /f'])
            self._call(["cmd.exe", '/C reg add "HKLM\\Software\\Policies\\Microsoft\\Edge" /v EfficiencyMode /t REG_DWORD /d 4 /f'])
        
        time.sleep(5)
        self.success = True

    def tearDown(self):
        if self.success:
            self.createPrepStatusControlFile()
        core.app_scenario.Scenario.tearDown(self)
