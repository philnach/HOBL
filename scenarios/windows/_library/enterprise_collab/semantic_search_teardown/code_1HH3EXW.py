import os
import logging

from parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_1HH3EXW.py')
    semantic_search_dir = Params.get('enterprise_collab','semantic_index_testdrive')
    index_updater_path = os.path.join(scenario.dut_exec_path, "IndexUpdater.exe")
    update_command = f'remove "{semantic_search_dir}"'
    logging.info("Remove Command %s",update_command)
    semantic_index_update_result = scenario._call([index_updater_path, update_command])
    logging.info("Semantic Index Update Result: %s", semantic_index_update_result)
    scenario._remote_make_dir(semantic_search_dir, True)