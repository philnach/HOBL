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
    return

def run_user_only():
    import_run_user_only('..\\..\\..\\..\\windows\\_library\\Teams\\teams_verify_bots')
    Params.setUserDefault('teams', 'send_video', '1', desc='Set to 1 to have the DUT turn on its camera. Set to 0 to have the DUT camera off.', valOptions=['0', '1'])
    Params.setUserDefault('teams', 'send_audio', '1', desc='Set to 1 to have the DUT have its mic on. Set to 0 to have the DUT be muted.', valOptions=['0', '1'])
    Params.setUserDefault('teams', 'send_screen', '0', desc='Set to 0 to have the DUT share its screen. Set to 0 to have the DUT not screen share.', valOptions=['0', '1'])
    Params.setUserDefault('teams', 'presentation_video_path', '/teams_resources/ppt.mp4', desc='Sets the path to the video file to use as the presented screen when the DUT is screen sharing.', valOptions=[])
    Params.setUserDefault('teams', 'show_desktop', '0', desc='Set to 1 to have the DUT screen share their desktop when screen sharing. Set to 0 to share a video of a presentation instead.', valOptions=['0', '1'])
    Params.setUserDefault('teams', 'access_key', '-1', desc='The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key.', valOptions=[])
    Params.setUserDefault('teams', 'bots_test_server', '0', desc='For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use.', valOptions=['0', '1'])
    Params.setUserDefault('teams', 'bots_force_subscribe_resolution', '0', desc='Force the bots to subscribe to a specific video resolution', valOptions=['0', '1080', '720', '480', '360'])
    return
