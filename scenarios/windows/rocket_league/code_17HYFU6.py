import logging

def run(scenario):
    logging.debug('Executing code block: code_17HYFU6.py')

    try:
        scenario._kill("RocketLeague.exe")
    except:
        pass

    scenario._sleep_to_now()
