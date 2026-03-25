import logging

def run(scenario):
    logging.debug('Executing code block: code_11W5X8N.py')
    try:
        scenario._kill("Resolve.exe")
    except:
        pass
    try:
        scenario._kill("CrashReporter.exe")
    except:
        pass