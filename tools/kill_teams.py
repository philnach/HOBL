from core.parameters import Params
from core.app_scenario import Scenario
import logging
import time


class Tool(Scenario):
    '''
    Kill all instances of Teams processes.
    '''
    module = __module__.split('.')[-1]

    Params.setDefault(module, 'restart', '0')

    restart = Params.get(module, 'restart')

    def initCallback(self, scenario):
        logging.info("Killing Teams")
        self._kill("Teams.exe", force = True)  # hard kill
    
    def testBeginCallback(self):
        pass
        
    def testEndCallback(self):
        if self.restart == "1":
            logging.info("Relaunching Teams")

            # First launch may only put icon in status bar.
            self._call(["powershell", "start msteams:"])
            time.sleep(10)

            logging.info("Minimizing Teams")
            self._call(["powershell.exe", '-command "$x = New-Object -ComObject Shell.Application; $x.minimizeall()"'])

    def dataReadyCallback(self):
        pass
