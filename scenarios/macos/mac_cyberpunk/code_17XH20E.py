import logging

def run(scenario):
    logging.debug('Executing code block: code_17XH20E.py')
    try:
        scenario._call(["pkill", '-f "Cyberpunk 2077"'], expected_exit_code="", timeout=10)
    except:
        pass