from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario


class Tool(Scenario):
    '''
    Deprecated. Wake the DUT on timeout.
    '''
    module = __module__.split('.')[-1]

    # This is a bad idea since there are a number of cases where waiting is expected, such as reboot or os_install.
    
    def initCallback(self, scenario):
        self.scenario = scenario
        self.scenario.timeout_wake = '1'
        pass

    def testBeginCallback(self):
        pass

    def testEndCallback(self):
        pass

    def dataReadyCallback(self):
        pass


