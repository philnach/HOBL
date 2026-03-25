#--------------------------------------------------------------
#
# HOBL
# Copyright(c) Microsoft Corporation
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files(the ''Software''),
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

##
# Reboot DUT
##

import builtins
import os
import unittest
import logging
import core.app_scenario
import time
from core.parameters import Params


class RebootMeasured(core.app_scenario.Scenario):
	# Don't run any tools with reboot, since processes running on the DUT will be killed when the reboot happens.
	Params.setOverride("global", "prep_tools", "")
	
	# Get parameters
	def runTest(self):              
		logging.info("Rebooting DUT")        
		self._call(["shutdown.exe", "/r /f /t 5"])
		time.sleep(15)
		self._wait_for_dut_comm()
		# Wait for 120s after reboot completes for the scheduled task to minimize windows to run.
		# time.sleep(120)


