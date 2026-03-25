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
# Prep for Local Video Playback
# 
# Setup instructions:
##

import builtins
import os
import logging
import core.app_scenario
from core.parameters import Params
import time


class CsFloorPrep(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    # Set default parameters

    # Get parameters

    Params.setOverride("global", "prep_tools", "")

    is_prep = True

    def runTest(self):
        #self._upload('scenarios\\cs_floor_resources', self.dut_exec_path, check_modified=True)
        self._upload("scenarios\\windows\\cs_floor\\cs_floor_wrapper.cmd", os.path.join(self.dut_exec_path, "cs_floor_resources"))
        self._upload("utilities\\proprietary\\sleep\\sleep.exe", os.path.join(self.dut_exec_path, "sleep"))

        self.createPrepStatusControlFile()

    def tearDown(self):
        core.app_scenario.Scenario.tearDown(self)
