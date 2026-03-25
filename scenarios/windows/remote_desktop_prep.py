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
import os
import logging
import core.app_scenario
from core.parameters import Params

class RemoteDesktopPrep(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    # Override collection of config data, traces, and execution of callbacks 
    # Params.setOverride("global", "collection_enabled", "0")
    is_prep = True

    def runTest(self):       
        # Set reg keys to enable remote desktop client
        logging.info('Setting reg keys.')
        self._call(["cmd.exe", '/C reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f'])
        self._call(["cmd.exe", '/C netsh adv firewall set rule group=@FirewallAPI.dll,-28752 new enable=yes'])
        self._call(["cmd.exe", '/C reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v ForceAutoLogon /t REG_DWORD /d 0x0 /f'])
        
    def tearDown(self):
        core.app_scenario.Scenario.tearDown(self)
