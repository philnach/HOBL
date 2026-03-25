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
from builtins import *
import logging
import core.app_scenario
import time
from core.parameters import Params


class UtcPrep(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    Params.setDefault(module, 'enable', '1')
    enable = Params.get(module, 'enable')

    def runTest(self):

        if self.enable == '1':
            self._upload("utilities\\proprietary\\ParseUtc\\UtcPerftrack.xml", "C:\\ProgramData\\Microsoft\\diagnosis\\sideload")
            self._upload("utilities\\proprietary\\ParseUtc\\DisableAllUploads.json", "C:\\ProgramData\\Microsoft\\diagnosis\\sideload")
            self._call(["cmd.exe", '/C reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 3 /f > null 2>&1'])
            self._call(["cmd.exe", '/C reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting" /v DisableWerUpload /t REG_DWORD /d 1 /f > null 2>&1'])
        else:
            self._call(["cmd.exe", '/C reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting" /v DisableWerUpload /f > null 2>&1'])
            self._call(["cmd.exe", '/C reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 1 /f > null 2>&1'])
            self._call(["cmd.exe", '/C del /f "C:\\ProgramData\\Microsoft\\diagnosis\\sideload\\UtcPerftrack.xml"'])
            self._call(["cmd.exe", '/C del /f "C:\\ProgramData\\Microsoft\\diagnosis\\sideload\\DisableAllUploads.json"'])

        rebootDut(self)

def rebootDut(self):
    logging.info("Rebooting DUT")
    try:
        self._call(["cmd.exe",  "/C shutdown.exe /r /f /t 5"])
    except:
        pass
    time.sleep(20)
    self._wait_for_dut_comm()
    logging.info("Reboot complete")
    return