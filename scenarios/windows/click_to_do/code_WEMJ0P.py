import logging
import os

def run(scenario):
    logging.debug('Executing code block: code_WEMJ0P.py')
    scenario._call(["cmd.exe", "/C " + os.path.join(scenario.dut_exec_path, "seattle_test.pdf")], blocking=False, expected_exit_code="")
    logging.info(os.path.join(scenario.dut_exec_path, "seattle_test.pdf"))