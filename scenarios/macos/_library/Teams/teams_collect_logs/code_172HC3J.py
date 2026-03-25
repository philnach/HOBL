import logging

def run(scenario):
    logging.debug('Executing code block: code_172HC3J.py')
    #kill teams process

    scenario._call(["bash", "-c \"pkill -i Teams\""])
    