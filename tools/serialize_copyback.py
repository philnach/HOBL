# Uses renaming to lock the folder in "\\powerdata\powerarchieve"
# The folder is also specific, named "copyback_lock"
# 
# Need the file in shared location "\\powerdata\powerarchieve"

from builtins import range
from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import os
import time

class Tool(Scenario):
    '''
    Deprecated.
    '''
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'counter', '900')
    Params.setDefault(module, 'lock_path', '')

    #Get parameters
    counter = Params.get(module, 'counter')
    lock_path = Params.get(module, 'lock_path')
    collection_enabled = Params.get('global', 'collection_enabled')

    lock_name = os.path.join(lock_path, 'copyback_lock')
    busy_name = os.path.join(lock_path, 'copyback_busy')
    valid_name = os.path.join(lock_path, 'copyback_valid')
    scenario=""
    is_valid = False
    
    def initCallback(self, scenario):
        self.scenario = scenario
        if self.collection_enabled == '0' or self.lock_path == "":
            return
        try:
            os.mkdir(self.valid_name)
            os.mkdir(self.lock_name)
        except:
            pass
        if os.path.isdir(self.valid_name)==False:
            self.is_valid=False
            return
        self.is_valid = True
        
    def testBeginCallback(self):
        return
        
    def testEndCallback(self):
        if not self.is_valid :
            return
        logging.info("Trying to acquire lock for copyback for " + self.scenario.testname)
        for count in range(int(self.counter)):
            try:
                os.rename(self.lock_name, self.busy_name)
                return
            except:
                time.sleep(2)
        raise Exception("Too many tries to lock file copyback for " + self.scenario.testname)
        
    def dataReadyCallback(self):
        if self.is_valid :
            os.rename(self.busy_name, self.lock_name)
