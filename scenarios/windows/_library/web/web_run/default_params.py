# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from core.parameters import Params
from utilities.open_source.modules import import_run_user_only

def run():
    Params.setCalculated('scenario_section', __package__.split('.')[-1])
    run_user_only()
    Params.setDefault('web_run', 'load_only', '0', desc='', valOptions=['0', '1'])
    Params.setParam('web', 'tabs', '0')
    return

def run_user_only():
    import_run_user_only('..\\site\\web_site_amazon_bsg', here=__file__)
    import_run_user_only('..\\site\\web_site_amazon_vacuum', here=__file__)
    import_run_user_only('..\\site\\web_site_google_images_apollo', here=__file__)
    import_run_user_only('..\\site\\web_site_google_images_london', here=__file__)
    import_run_user_only('..\\site\\web_site_google_search_belgium', here=__file__)
    import_run_user_only('..\\site\\web_site_google_search_super_bowl', here=__file__)
    import_run_user_only('..\\site\\web_site_instagram', here=__file__)
    import_run_user_only('..\\site\\web_site_reddit', here=__file__)
    import_run_user_only('..\\site\\web_site_the_verge', here=__file__)
    import_run_user_only('..\\site\\web_site_wikipedia', here=__file__)
    import_run_user_only('..\\site\\web_site_youtube_nasa', here=__file__)
    import_run_user_only('..\\site\\web_site_youtube_tos', here=__file__)
    import_run_user_only('..\\web_clear_cache', here=__file__)
    import_run_user_only('..\\web_new_tab', here=__file__)
    Params.setUserDefault('web', 'web_workload', 'amazonbsg amazonvacuum googleimagesapollo googleimageslondon googlesearchbelgium googlesearchsuperbowl instagram reddit theverge wikipedia youtubenasa youtubetos', desc='Specific websites to run.', valOptions=['amazonbsg', 'amazonvacuum', 'googleimagesapollo', 'googleimageslondon', 'googlesearchbelgium', 'googlesearchsuperbowl', 'instagram', 'reddit', 'theverge', 'wikipedia', 'youtubenasa', 'youtubetos'], multiple=True)
    return
