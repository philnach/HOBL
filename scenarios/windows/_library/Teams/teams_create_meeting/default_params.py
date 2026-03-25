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
from utilities.open_source.modules import import_run_user_only

def run():
    Params.setCalculated('scenario_section', __package__.split('.')[-1])
    run_user_only()
    return

def run_user_only():
    Params.setUserDefault('teams', 'meeting_time', '0', desc='Set the time in minutes that the meeting can last up to. Default is teams:duration + 30 min.', valOptions=[])
    Params.setUserDefault('teams', 'access_key', '-1', desc='The access key for the Teams Bots Server. Contact HOBL Support to inquire for a key.', valOptions=[])
    Params.setUserDefault('teams', 'number_of_bots', '1', desc='Sets the number of bots to have in the meeting.', valOptions=['1', '2', '4', '8', '9'])
    Params.setUserDefault('teams', 'bots_send_video', '1', desc='Set to 1 if bots should have their cameras on. Set to 0 for audio only calls.', valOptions=['0', '1'])
    Params.setUserDefault('teams', 'bots_send_audio', '1', desc='Set to 1 to have bots send audio. Set to 0 to have bots be muted.', valOptions=['0', '1'])
    Params.setUserDefault('teams', 'bots_share_screen', '0', desc='Set to 1 to have the primary bot share its screen in the meeting.', valOptions=['0', '1'])
    Params.setUserDefault('teams', 'bots_test_server', '0', desc='For advanced use. Set to 1 to use the testing instance of the bots server. Not Recomended for general use.', valOptions=['0', '1'])
    return
