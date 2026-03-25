import logging

def run(scenario):
    logging.debug('Executing code block: code_W72XHL.py')
    try:
        scenario._kill("mspaint.exe")
    except:
        pass