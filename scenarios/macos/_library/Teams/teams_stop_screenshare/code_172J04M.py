import logging
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_172J04M.py')
    join_meeting_uri = Params.get('teams', 'join_meeting_uri')
    
    scenario._call(["open", f"{join_meeting_uri}"])
