import logging

def run(scenario):
    logging.debug('Executing code block: code_1062A47.py')
    try:
        scenario._kill("Cyberpunk2077.exe")
    except:
        pass
    try:
        scenario._kill("CrashReporter.exe")
    except:
        pass
        