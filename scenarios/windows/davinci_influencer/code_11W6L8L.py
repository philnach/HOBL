import logging

def run(scenario):
    logging.debug('Executing code block: code_11W6L8L.py')
    try:
        scenario._kill("Resolve.exe")
    except:
        pass
    try:
        scenario._kill("CrashReporter.exe")
    except:
        pass