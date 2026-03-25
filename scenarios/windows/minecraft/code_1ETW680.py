import logging
from parameters import Params
import math

def run(scenario):
    logging.debug('Executing code block: code_1ETW680.py')
    duration = int(Params.get("minecraft", 'duration'))
    loop_duration = int(Params.get("minecraft", 'loop_duration'))
    
    loops = math.ceil(duration / loop_duration)
    Params.setOverride("minecraft", 'loops', str(loops))
    #logging.info("Setting loops to: " + str(loops))
    
    if (duration % loop_duration == 0):
        Params.setOverride("minecraft", 'final_loop_duration', str(loop_duration))
    else:
        final_loop_duration = duration % loop_duration
        Params.setOverride("minecraft", 'final_loop_duration', str(final_loop_duration))