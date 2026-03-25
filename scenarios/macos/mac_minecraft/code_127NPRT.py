import logging
import time
import os

def run(scenario):
    logging.debug('Executing code block: code_127NPRT.py')
    
    logging.info("Resetting map for next run.")
    scenario._call(["rm", "-rf " + '"/Users/testuser/Library/Application Support/minecraft/saves/Demo_World"'], callback=False)

    time.sleep(1)
    
    scenario._upload(os.path.join("scenarios", "minecraft_resources", "Demo_World"), "/Users/testuser/Library/Application Support/minecraft/saves/")

    time.sleep(3)
    logging.info("Map Reset Finished")
