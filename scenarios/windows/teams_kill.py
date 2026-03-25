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
# Force kill the Teams process
##

import core.app_scenario


class TeamsKill(core.app_scenario.Scenario):

    # Local parameters
    is_prep = True

    def setUp(self):
        # Intentionally not calling base method to prevent extraneous call attempts to DUT
        pass

    def runTest(self):
        self._kill("Teams.exe", force = True)  # hard kill
        self._kill("ms-teams.exe", force = True)  # hard kill

    def tearDown(self):
        # Don't call base tearDown so that we don't interact with DUT.
        pass

    def kill(self):
        # self._kill("Teams.exe", force = True)
        try:
            logging.debug("Killing Teams.exe")
            self._kill("Teams.exe", force = True)  # hard kill
            self._kill("ms-teams.exe", force = True)  # hard kill
        except:
            pass