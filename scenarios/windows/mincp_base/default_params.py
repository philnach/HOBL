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
from utilities.modules import import_run_user_only

def run():
    Params.setCalculated('scenario_section', __package__.split('.')[-1])
    run_user_only()
    Params.setDefault('mincp_base', 'background_timers', '1', desc='', valOptions=['0', '1'])
    Params.setDefault('mincp_base', 'background_teams', '1', desc='', valOptions=['0', '1'])
    Params.setDefault('mincp_base', 'background_onedrive_copy', '1', desc='', valOptions=['0', '1'])
    Params.setDefault('mincp_base', 'simple_office_launch', '0', desc='', valOptions=['1', '0'])
    Params.setParam(None, 'web_replay_run', '1')
    Params.setParam(None, 'phase_reporting', '1')
    Params.setDefault('mincp_base', 'perf_run', '0', desc='', valOptions=['0', '1'])
    return

def run_user_only():
    import_run_user_only('scenarios\\windows\\_library\\Teams\\teams_setup')
    import_run_user_only('scenarios\\windows\\_library\\Teams\\teams_teardown')
    import_run_user_only('scenarios\\windows\\_library\\enterprise_collab\\diagnostics_disable')
    import_run_user_only('scenarios\\windows\\_library\\enterprise_collab\\diagnostics_enable')
    import_run_user_only('scenarios\\windows\\_library\\enterprise_collab\\live_captions_setup')
    import_run_user_only('scenarios\\windows\\_library\\enterprise_collab\\semantic_search_setup')
    import_run_user_only('scenarios\\windows\\_library\\enterprise_collab\\semantic_search_teardown')
    import_run_user_only('scenarios\\windows\\_library\\enterprise_collab\\timers_setup')
    import_run_user_only('scenarios\\windows\\_library\\enterprise_collab\\timers_teardown')
    import_run_user_only('scenarios\\windows\\_library\\misc\\click_to_do_setup')
    import_run_user_only('scenarios\\windows\\_library\\misc\\click_to_do_teardown')
    import_run_user_only('scenarios\\windows\\_library\\misc\\studio_effect_blur')
    import_run_user_only('scenarios\\windows\\_library\\productivity\\prod_close')
    import_run_user_only('scenarios\\windows\\_library\\productivity\\prod_kill')
    import_run_user_only('scenarios\\windows\\_library\\productivity\\prod_open')
    import_run_user_only('scenarios\\windows\\_library\\productivity\\prod_setup')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_check')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_close_tabs')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_kill')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_run_mincp')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_setup')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_switchto')
    Params.setUserDefault(None, 'mincp_workloads', '', desc='', valOptions=['live_captions', 'copilot_query', 'semantic_search', 'click_todo', 'studioeffect_blur', 'productivity'], multiple=True)
    return
