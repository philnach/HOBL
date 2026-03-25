import logging

def run(scenario):
    logging.debug('Executing code block: code_12VL6EA.py')
    scenario._copy_data_from_remote(scenario.result_dir + "\\MSTeamsLogs", source=scenario.dut_data_path + "/MSTeamsLogs")