import logging
import os
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_163V74Y.py')
    
    presentation_video_path = Params.get('teams', 'presentation_video_path')
    presentation_video_full_path = scenario.dut_exec_path + presentation_video_path

    scenario._call(["open", presentation_video_full_path])