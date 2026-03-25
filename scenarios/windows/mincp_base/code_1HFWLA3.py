import logging
import os
from parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_1HFWLA3.py')
    semantic_search_dir = getattr(scenario, 'semantic_index_testdrive', None)
    index_updater_path = os.path.join(scenario.dut_exec_path, "IndexUpdater.exe")
    update_command = f'remove "{semantic_search_dir}"'
    semantic_index_update_result = scenario._call([index_updater_path, update_command])
    logging.info("Semantic Index Update Result: %s", semantic_index_update_result)
    scenario._remote_make_dir(semantic_search_dir, True)