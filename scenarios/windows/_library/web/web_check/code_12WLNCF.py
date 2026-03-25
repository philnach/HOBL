import logging
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_12WLNCF.py')

    scenario._web_replay_check_log(int(Params.get("web_check", "youtube_duration")))
