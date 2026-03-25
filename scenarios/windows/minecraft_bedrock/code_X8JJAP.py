import logging
import time

def run(scenario):
    logging.debug('Executing code block: code_X8JJAP.py')
    try:
        scenario._kill("Minecraft.Windows.exe")
    except:
        pass
        