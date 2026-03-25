import logging
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_1A1LKMY.py')
    duration = int(Params.get("minecraft_bedrock", 'duration'))
    # loop_duration = int(Params.get("minecraft_bedrock", 'loop_duration'))

    if (duration < 10):
        logging.info("Got into less than 10 duration setting loop duration to " + str(duration))
        Params.setOverride("minecraft_bedrock", 'loop_duration', str(duration))
        updated_duration = duration - duration
    else:
        logging.info("Setting loop duration to 10")
        Params.setOverride("minecraft_bedrock", 'loop_duration', '10')
        updated_duration = duration - 10

    Params.setOverride("minecraft_bedrock", 'duration', str(updated_duration))
    logging.info("updated duration: " + str(updated_duration))