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

from functools import partial
import os
from parameters import Params
import utilities.modules

import_run_user_only = partial(utilities.modules.import_run_user_only, here=__file__)

def run():
    Params.setCalculated('scenario_section', __package__.split('.')[-1])
    run_user_only()
    Params.setDefault('mac_enterprise_collab', 'loops', '1', desc='', valOptions=[])
    Params.setDefault('mac_enterprise_collab', 'background_teams', '1', desc='', valOptions=['0', '1'])
    Params.setDefault('mac_enterprise_collab', 'background_timers', '1', desc='', valOptions=['0', '1'])
    Params.setDefault('mac_enterprise_collab', 'background_onedrive_copy', '1', desc='', valOptions=['0', '1'])
    Params.setDefault('mac_enterprise_collab', 'simple_office_launch', '0', desc='', valOptions=['0', '1'])
    Params.setParam(None, 'web_replay_run', '1')
    return

def run_user_only():
    import_run_user_only('..\\_library\\Teams\\teams_setup')
    import_run_user_only('..\\_library\\Teams\\teams_teardown')
    import_run_user_only('..\\_library\\enterprise_collab\\timers_setup')
    import_run_user_only('..\\_library\\productivity\\prod_close')
    import_run_user_only('..\\_library\\productivity\\prod_kill')
    import_run_user_only('..\\_library\\productivity\\prod_open')
    import_run_user_only('..\\_library\\productivity\\prod_setup')
    import_run_user_only('..\\_library\\web\\web_close_browser')
    import_run_user_only('..\\_library\\web\\web_close_tabs')
    import_run_user_only('..\\_library\\web\\web_kill')
    import_run_user_only('..\\_library\\web\\web_run_12')
    import_run_user_only('..\\_library\\web\\web_setup')
    return
