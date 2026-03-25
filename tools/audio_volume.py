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


class Tool(Scenario):
    '''
    Set specified audio volume.
    '''
    module = __module__.split('.')[-1]

    # Set default parameters
    Params.setDefault(module, 'volume', 'Unknown')
    #Params.setDefault(module, 'mute', "False")

    # Get parameters
    volume = Params.get(module, 'volume')
    #mute = Params.get(module, 'mute')

    def initCallback(self, scenario):

        self.scenario = scenario
        if self.volume == "Unknown":
            logging.error("Could not resolve specified volume parameter.")
            self.fail("Could not resolve specified volume parameter.")

        self.set_vol = (decimal.Decimal(self.volume) / 100)
        
        if self.platform.lower() == "macos":
            self._call(["zsh", f"-c \"osascript -e 'set volume output volume {self.volume}'\""])
            logging.info("Audio volume set to: " + str(self.volume))
            return
        
        elif self.platform.lower() == "windows":

            # exists = os.path.isfile(self.dut_exec_path)
            exists = os.path.isfile(self.dut_exec_path + "\\audio_volume.ps1")
            if exists:
                pass
            else:
                self._upload("utilities\\audio_volume.ps1", self.dut_exec_path)
            
            self._call(["powershell.exe ", self.dut_exec_path + "\\audio_volume.ps1 " +  str(self.set_vol)])
            logging.info("Audio volume set to: " + str(self.set_vol))
            return

    def testBeginCallback(self):
        pass

    def testEndCallback(self):
        pass

    def dataReadyCallback(self):
        pass



