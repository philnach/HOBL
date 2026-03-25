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
    Params.setParam('web', 'tabs', '0')
    return

def run_user_only():
    import_run_user_only('..\\site\\web_site_amazon_got')
    import_run_user_only('..\\site\\web_site_amazon_vacuum')
    import_run_user_only('..\\site\\web_site_google_images_apollo')
    import_run_user_only('..\\site\\web_site_google_images_london')
    import_run_user_only('..\\site\\web_site_google_search_belgium')
    import_run_user_only('..\\site\\web_site_google_search_super_bowl')
    import_run_user_only('..\\site\\web_site_instagram')
    import_run_user_only('..\\site\\web_site_reddit')
    import_run_user_only('..\\site\\web_site_the_verge')
    import_run_user_only('..\\site\\web_site_wikipedia')
    import_run_user_only('..\\site\\web_site_youtube_nasa')
    import_run_user_only('..\\site\\web_site_youtube_tos')
    import_run_user_only('..\\web_clear_cache')
    import_run_user_only('..\\web_new_tab')
    Params.setUserDefault(None, 'web_workload', 'amazongot amazonvacuum googleimagesapollo googleimageslondon googlesearchbelgium googlesearchsuperbowl instagram reddit theverge wikipedia youtubenasa youtubetos', desc='', valOptions=['amazonbsg', 'amazongot', 'amazonvacuum', 'googleimagesapollo', 'googleimageslondon', 'googlesearchbelgium', 'googlesearchsuperbowl', 'instagram', 'reddit', 'theverge', 'wikipedia', 'youtubenasa', 'youtubetos'], multiple=True)
    return
