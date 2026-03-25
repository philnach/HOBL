from core.parameters import Params
from core.app_scenario import Scenario
import logging
import time


class Tool(Scenario):
    '''
    Stops the Windows Widgets from running.
    '''
    module = __module__.split('.')[-1]

    def initCallback(self, scenario):
        logging.info("Killing Windows Widgets")
        self._kill("Widgets.exe", force = True)  # hard kill
    
    def testBeginCallback(self):
        pass
        
    def testEndCallback(self):
        pass

    def dataReadyCallback(self):
        pass
