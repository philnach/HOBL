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
# config_check
# 
# Runs the config_check script on the DUT to get the system  configuration
# details.
#
# Setup instructions:
#   Run config_check_prep scenario.
##

import builtins
import logging
import core.app_scenario
from core.parameters import Params
import os
import json


class MacConfigCheck(core.app_scenario.Scenario):

    module = __module__.split('.')[-1]
    # Set default parameters
    override_keys = ['Study Type', 'Comments', 'Hardware Version', 'Blade', 'Accessories', 'RTC Reserve (%)', 'Raw Data Location', 'Device Name']
    for key in override_keys:
        Params.setDefault(module, key, '')

    # Get parameters

    # Override some potential global params that wouldn't be appropriate for a config_check
    Params.setOverride("global", "trace", "0")
    Params.setOverride("global", "config_check", "0")
    Params.setOverride("global", "callback_test_begin", "")
    Params.setOverride("global", "callback_test_end", "")
    Params.setOverride("global", "tools", "")

    is_prep = True

    def runTest(self):
        fo = open("hobl_version.txt", "r")
        hobl_ver = fo.readline(50).strip()
        fo.close()

        override_dict = {key: Params.get(self.module, key) for key in self.override_keys}
        override_dict["Hardware Version"] = override_dict["Hardware Version"].upper()
        override_dict['HOBL Version'] = hobl_ver.strip()
        override_str = json.dumps(override_dict)
        override_str = override_str.replace('"', "'")

        dest = self.dut_exec_path + "/config_check.sh"
        self._upload("utilities\\open_source\\config_check.sh", self.dut_exec_path, check_modified=True)
        cmd = f'-c "{dest} --logfile={self.dut_data_path}/Config --override-string=\\\"{override_str}\\\""'
        self._call(["zsh", cmd])
        
        
