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
# Check if rundown_abl_prep scenarios have all passed, and if so, launch rundown_abl plan
##

import core.app_scenario
from core.parameters import Params
import fnmatch
import os
import requests
import logging
from urllib.parse import (
    urlparse,
    urlunparse,
    urlencode
)

class RunAblIfPrepsPassed(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    dashboard_url = Params.get('global', 'dashboard_url')
    study_type = Params.getOverride('global', 'study_type')

    is_prep = True


    def setUp(self):
        # Don't call base setUp so that we don't interact with DUT
        return


    def runTest(self):
        prep_scenarios = ["productivity_prep", "button_install", "edge_install", "msa_prep", "onedrive_prep", "daily_prep", "config_check", "store_prep", "adaptive_color_disable"]
        # Check if preps ran
        assert_list = ""
        assert_list += self.checkPrepStatus(prep_list)

        training_root, training_folder = self._find_latest_training_folder("abl")
        if training_folder == "":
            assert_list += "abl_training folder is missing on the Host.\n"
        local_training = training_root + os.sep + training_folder
        for files in os.listdir(local_training):
            if fnmatch.fnmatch(files, '.FAIL'):
                assert_list  += "Most recent abl_training Failed.\n"

        if assert_list != "":
            self._assert(assert_list)
        else:
            # All preps passed, launch abl rundown
            args = arguments.args
            params_file = args.profile
            profile = os.path.basename(params_file).rsplit('.',1)[0]

            url = urlunparse(
                urlparse(self.dashboard_url)._replace(
                    path="/plan/RunPlan"
                )
            )

            study_type_param = ""

            if self.study_type:
                study_type_param = f"&studyType={self.study_type}"

            response = requests.get(url + "?profile=" + profile + "&plan=rundown_abl.ps1&autoResubmit=true" + study_type_param)
            logging.info("Launching rundown_abl.ps1 for profile " + profile + ": " + str(response))



    def tearDown(self):
        # Don't call base tearDown so that we don't interact with DUT
        return


    def kill(self):
        # Prevent base kill routine from running
        return 0
