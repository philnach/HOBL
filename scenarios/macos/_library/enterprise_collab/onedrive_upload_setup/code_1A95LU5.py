import logging
import os

def run(scenario):
    logging.debug('Executing code block: code_1A95LU5.py')
    
    target_path = "scenarios\\MacOS\\mac_enterprise_collab\\resources\\large"

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    for i in range(3):
        os.system("fsutil file createnew " + target_path + "\\temp_" + str(i) + ".bin 1610612736")

    logging.info("Large files created for OneDrive copy operations")