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


class Reboot(core.app_scenario.Scenario):

	module = __module__.split('.')[-1]

	# Set default parameters
	Params.setDefault(module, 'to_uefi', '0')
	
	# Don't run any tools with reboot, since processes running on the DUT will be killed when the reboot happens.
	Params.setOverride("global", "prep_tools", "")

	is_prep = True
	
	def runTest(self):
		# Get parameters
		self.to_uefi = Params.get(self.module, 'to_uefi')
		self._dut_reboot(to_uefi=self.to_uefi == '1')
		              