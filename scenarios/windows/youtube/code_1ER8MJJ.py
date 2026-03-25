import logging
import math
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_1ER8MJJ.py')

    duration      = int(Params.get("youtube", "duration"))
    loop_duration = int(Params.get("youtube", "loop_duration"))

    loops = math.ceil(duration / loop_duration)
    logging.info(f"Looping set for {loops} iteration{'s' if loops != 1 else ''}")
    Params.setParam("youtube", "loops", str(loops))
