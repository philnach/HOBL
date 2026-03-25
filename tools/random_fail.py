from core.parameters import Params
from core.app_scenario import Scenario
import logging
import time
from random import *

class Tool(Scenario):
    '''
    Randomly fail a test, for devolpment/debug purposes.
    '''
    module = __module__.split('.')[-1]

    def initCallback(self, scenario):
        pass
    
    def testBeginCallback(self):
        if random() > 0.5:
            logging.info("Not injecting failure.")
        else:
            logging.info("Injecting failure.")
            assert(False)
        
        
    def testEndCallback(self):
        pass

    def dataReadyCallback(self):
        pass
