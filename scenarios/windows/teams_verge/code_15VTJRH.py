import logging
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_15VTJRH.py')
    #loops = Params.get('teams_verge', 'loops')
    teams_duration = Params.get('teams', 'duration')

    if int(teams_duration) < 125:
        Params.setParam('teams_verge', 'loops', "1")
        Params.setParam('teams', 'duration', "125")
    else:
        loops = int(int(teams_duration)/125)
        teams_duration = loops * 125
        Params.setParam('teams_verge', 'loops', str(loops))
        Params.setParam('teams', 'duration', str(teams_duration))
