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
from core.parameters import Params
import utilities.open_source.modules

import_run_user_only = partial(utilities.open_source.modules.import_run_user_only, here=__file__)

def run():
    Params.setCalculated('scenario_section', __package__.split('.')[-1])
    run_user_only()
    Params.setDefault('teams_verge', 'loops', '4', desc='', valOptions=[])
    Params.setParam(None, 'web_replay_run', '1')
    Params.setParam('teams', 'send_screen', '1')
    Params.setParam('teams', 'show_desktop', '1')
    Params.setParam('teams', 'number_of_bots', '1')
    Params.setParam('teams', 'send_video', '1')
    Params.setParam('teams', 'send_audio', '1')
    Params.setParam('teams', 'bots_send_video', '1')
    Params.setParam('teams', 'bots_send_audio', '1')
    Params.setParam('teams', 'bots_share_screen', '0')
    Params.setParam('teams', 'bots_force_subscribe_resolution', '0')
    return

def run_user_only():
    import_run_user_only('..\\_library\\Teams\\teams_setup')
    import_run_user_only('..\\_library\\Teams\\teams_teardown')
    import_run_user_only('..\\_library\\web\\site\\web_site_the_verge')
    import_run_user_only('..\\_library\\web\\web_check')
    import_run_user_only('..\\_library\\web\\web_clear_cache')
    import_run_user_only('..\\_library\\web\\web_close_browser')
    import_run_user_only('..\\_library\\web\\web_kill')
    import_run_user_only('..\\_library\\web\\web_setup')
    Params.setUserDefault('teams', 'duration', '600', desc='Sets the time in seconds for the test to run.', valOptions=['60', '120', '240', '300', '600', '900'])
    Params.setUserDefault('teams', 'maintain_bots', '0', desc='Set to 1 to have the test peridically check that all bots are present in the call and add bots if needed.', valOptions=['0', '1'])
    return
