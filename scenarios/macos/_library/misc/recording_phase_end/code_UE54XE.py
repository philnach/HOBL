import logging
from core.parameters import Params
import time

def run(scenario):
    logging.debug('Executing code block: code_UE54XE.py')
    duration = time.time() - scenario.phase_start_time
    category = Params.get(scenario.component, "phase_category")
    name = Params.get(scenario.component, "phase_name")
    scenario._record_phase_time(category + ": " + name, scenario.phase_start_time, duration)