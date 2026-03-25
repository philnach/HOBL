import logging
from core.parameters import Params
import math

def run(scenario):
    logging.debug('Executing code block: code_1A2RJ6A.py')
    duration = int(Params.get("minecraft_bedrock", 'duration'))
    loop_duration = int(Params.get("minecraft_bedrock", 'loop_duration'))
    
    loops = math.ceil(duration / loop_duration)
    Params.setOverride("minecraft_bedrock", 'loops', str(loops))
    #logging.info("Setting loops to: " + str(loops))
    
    if (duration % loop_duration == 0):
        Params.setOverride("minecraft_bedrock", 'final_loop_duration', str(loop_duration))
    else:
        final_loop_duration = duration % loop_duration
        Params.setOverride("minecraft_bedrock", 'final_loop_duration', str(final_loop_duration))