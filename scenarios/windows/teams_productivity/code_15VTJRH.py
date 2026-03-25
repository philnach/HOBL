import logging
from parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_15VTJRH.py')
    #loops = Params.get('teams_verge', 'loops')
    teams_duration = Params.get('teams', 'duration')

    if int(teams_duration) < 760:
        Params.setParam('teams_productivity', 'loops', "1")
        Params.setParam('teams', 'duration', "760")
    else:
        loops = int(int(teams_duration)/760)
        teams_duration = loops * 760
        Params.setParam('teams_productivity', 'loops', str(loops))
        Params.setParam('teams', 'duration', str(teams_duration))
