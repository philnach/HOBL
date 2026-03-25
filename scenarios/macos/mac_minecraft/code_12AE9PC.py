import logging
import time

def run(scenario):
    logging.debug('Executing code block: code_12AE9PC.py')
    
    try:
        scenario._kill("java")
    except:
        pass
    time.sleep(5)
    try:
        scenario._kill("launcher")
    except:
        pass