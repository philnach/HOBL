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
# Send plan completion email
##

import core.app_scenario
from core.parameters import Params

from utilities.open_source.email_notify import send_plan_complete_email


class Notify(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    is_prep = True

    Params.setOverride('global', 'local_execution',    '1')
    Params.setOverride('global', 'post_run_delay', '0')

    Params.setDefault(module, 'plan_run_type', '')

    plan_run_type = Params.get(module, 'plan_run_type')


    def setUp(self):
        # Don't call base setUp so that we don't interact with DUT
        return


    def runTest(self):
        send_plan_complete_email(self.plan_run_type)


    def tearDown(self):
        # Don't call base tearDown so that we don't interact with DUT
        return


    def kill(self):
        # Prevent base kill routine from running
        return 0
