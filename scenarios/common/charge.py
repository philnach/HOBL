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
# charge_on
# 
# Turns on the device charger.
# Intended to be included at the end of a test plan
#
# Setup instructions:
#   Specify the command to call to turn on the charger for the "charge_on_call" parameter in your parameters file.
##

import logging
import core.app_scenario
from core.parameters import Params


class Charge(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    # Override collection of config data, traces, and execution of callbacks 
    Params.setDefault(module, 'state', 'on')

    # Get parameters
    charge_on_call = Params.get('global', 'charge_on_call')
    charge_off_call = Params.get('global', 'charge_off_call')
    state = Params.get(module, 'state')

    is_prep = True

    def setUp(self):
        # Don't call base setUp so that we don't interact with DUT.
        return

    def runTest(self):    
        if self.state == "on":
            logging.info("Attempting to turn on charger...")
            if self.charge_on_call == '':      
                logging.warning("No charge_on_call specified.")             
            else:
                self._host_call(self.charge_on_call)            
                logging.info("Charger turned on.")
            if Params.get('global', 'local_execution') == '1':
                self._host_call('utilities\\MsgPrompt.exe -WaitForAC')
                logging.info("Charger plugged in.")
        else:
            logging.info("Attempting to turn off charger...")
            if self.charge_off_call == '':
                logging.warning("No charge_off_call specified.")
            else:
                self._host_call(self.charge_off_call)
                logging.info("Charger turned off.")
            if Params.get('global', 'local_execution') == '1':
                self._host_call('utilities\\MsgPrompt.exe -WaitForDC')
                logging.info("Charger unplugged.")

    def tearDown(self):
        # Don't call base tearDown so that we don't interact with DUT.
        return

    def kill(self):
        # Prevent base kill routine from running
        return 0
