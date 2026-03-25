
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
import logging
import core.app_scenario
from core.parameters import Params
import time

##
# Install virtual button.
# Used to put device to sleep and wake up.
##

class ButtonInstall(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    # Set default parameters

    # Get parameters
    dut_architecture = Params.get('global', 'dut_architecture')

    # Override collection of config data, traces, and execution of callbacks 
    Params.setOverride("global", "prep_tools", "")
    is_prep = True

    def runTest(self):
        # Upload
        self._upload('utilities\\proprietary\\button\\'  + self.dut_architecture + "\\*", self.dut_exec_path + "\\button")
        self._upload('utilities\\proprietary\\pwrtest\\'  + self.dut_architecture + "\\*", self.dut_exec_path + "\\pwrtest")

        time.sleep(1)
        # Remove any existing button
        self._call(['cmd.exe' , ' /C "cd /D ' + self.dut_exec_path + '\\button & .\\button.exe -u"'], expected_exit_code="")
        # Install this button
        self._call(['cmd.exe', ' /C "cd /D ' + self.dut_exec_path + '\\button & .\\button.exe -i"'])
        self.createPrepStatusControlFile()

