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
# Perf gate prep that will enable energy recommendations
#   
##


from core.parameters import Params
from core.app_scenario import Scenario
import core.app_scenario
import logging
import os
import time

class EnergyRecom(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    Params.setDefault('module', 'source_path', '..\\ScenarioAssets\\ERTestApp\\')

    source_path = Params.get('module', 'source_path')
    dut_architecture = Params.get('global', 'dut_architecture')
    

    
    # Params.setOverride("global", "collection_enabled", "0")
    Params.setOverride("global", "prep_tools", "")
    is_prep = True


    def runTest(self):
        
        if self.dut_architecture == "arm64":
            logging.info("Moving ERTestApp for arm64 to DUT")
            if not self._check_remote_file_exists("ERTestApp.exe", in_exec_path=True, target_ip=None):
                self._upload(self.source_path + "\\arm64\\ERTestApp.exe", self.dut_exec_path)
        else:
            logging.info("Moving ERTestApp for arm64 to DUT")
            if not self._check_remote_file_exists("ERTestApp.exe", in_exec_path=True, target_ip=None):
                self._upload(self.source_path + "\\amd64\\ERTestApp.exe", self.dut_exec_path)
        
        time.sleep(5)

        logging.info("Enabling energy recommendation for device")
        self._call([os.path.join(self.dut_exec_path, "ERTestApp.exe"), "PowerMode,ScreenSaver,Brightness,CABC,DarkTheme,DynamicRefresh,ReduceRefreshRate"], 
        blocking=True, timeout=172800, expected_exit_code="")


    def tearDown(self):
        core.app_scenario.Scenario.tearDown(self)

       
