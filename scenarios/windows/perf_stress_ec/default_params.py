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
    Params.setDefault('perf_stress_ec', 'background_teams', '1', desc='', valOptions=['0', '1'])
    Params.setDefault('perf_stress_ec', 'background_onedrive_copy', '1', desc='', valOptions=['0', '1'])
    Params.setDefault('perf_stress_ec', 'simple_office_launch', '1', desc='', valOptions=['1', '0'])
    Params.setDefault('perf_stress_ec', 'shell_probes', '1', desc='', valOptions=['0', '1'])
    Params.setDefault('perf_stress_ec', 'sleep_resume_midrun', '0', desc='', valOptions=['0', '1'])
    Params.setDefault('perf_stress_ec', 'edge_close_relaunch', '1', desc='', valOptions=['0', '1'])
    Params.setDefault('perf_stress_ec', 'perftrack_app_launch', '0', desc='', valOptions=['0', '1'])
    Params.setDefault('perf_stress_ec', 'provider', 'perf_utc.wprp', desc='WPRP file to use for perf_utc tracing.', valOptions=['@\\providers'])
    Params.setDefault('perf_stress_ec', 'bg_edge_tabs', '0', desc='', valOptions=[])
    Params.setParam(None, 'web_replay_run', '1')
    Params.setParam(None, 'phase_reporting', '1')
    Params.setDefault('perf_stress_ec', 'stress_run', '0', desc='', valOptions=['0', '1'])
    Params.setDefault('perf_stress_ec', 'stress_cpu_target', '75', desc='Target CPU load percentage for stress mode.', valOptions=['25', '50', '75'])
    return

def run_user_only():
    import_run_user_only('scenarios\\windows\\_library\\Teams\\teams_setup')
    import_run_user_only('scenarios\\windows\\_library\\Teams\\teams_teardown')
    import_run_user_only('scenarios\\windows\\_library\\misc\\capture_taskbar')
    import_run_user_only('scenarios\\windows\\_library\\misc\\etw_event_tag')
    import_run_user_only('scenarios\\windows\\_library\\misc\\recording_phase_begin')
    import_run_user_only('scenarios\\windows\\_library\\misc\\recording_phase_end')
    import_run_user_only('scenarios\\windows\\_library\\productivity\\prod_close')
    import_run_user_only('scenarios\\windows\\_library\\productivity\\prod_kill')
    import_run_user_only('scenarios\\windows\\_library\\productivity\\prod_open')
    import_run_user_only('scenarios\\windows\\_library\\productivity\\prod_run_no_onenote')
    import_run_user_only('scenarios\\windows\\_library\\productivity\\prod_setup')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_bg_tabs')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_check')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_close_tabs')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_kill')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_run_12')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_setup')
    import_run_user_only('scenarios\\windows\\_library\\web\\web_switchto')
    return
