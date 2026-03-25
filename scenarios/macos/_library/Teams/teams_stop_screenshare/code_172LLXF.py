import logging

def run(scenario):
    logging.debug('Executing code block: code_172LLXF.py')
    scenario._call(["killall", '"QuickTime Player"'], expected_exit_code="", timeout=10)