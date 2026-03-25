import logging
import time

def run(scenario):
    logging.debug('Executing code block: code_V4J32J.py')
    
    try:
        scenario._kill("msedge.exe")
    except:
        pass
    try:
        scenario._kill("chrome.exe")
    except:
        pass
        
    time.sleep(3)

    scenario._web_replay_kill()

    scenario._sleep_to_now()
