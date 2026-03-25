# Tool that runs a battery bar widget on the screen
from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys, os


class Tool(Scenario):
    '''
    Overlays a widget showing battery level.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'version', 'v1.0.0')

    # Get parameters
    version = Params.get(module, 'version')

    def initCallback(self, scenario):
        # Initialization code
        # Keep a pointer to the scenario that this tools is being run with
        self.scenario = scenario

        # Check if BatteryBar is already on the DUT or upload it
        if not self._check_remote_file_exists("BatteryBar\\BatteryBar.exe", in_exec_path=True):
            logging.debug("BatteryBar not found on DUT, uploading...")
            self._upload("utilities\\BatteryBar\\bin\\" + self.version + "\\*", os.path.join(self.dut_exec_path, "BatteryBar"))
        else:
            logging.debug("BatteryBar found on DUT")

        # Run the BatteryBar process
        self._call([os.path.join(self.dut_exec_path, "BatteryBar\\BatteryBar.exe")], blocking=False)
        return

    def testBeginCallback(self):
        return

    def testEndCallback(self):
        # Kill the BatteryBar process
        logging.info("Killing BatteryBar.exe")
        self._kill("BatteryBar.exe")
        return

    def dataReadyCallback(self):
        return
    
    def testScenarioFailed(self):
        logging.debug("Test failed, cleaning up.")
        self.testEndCallback()

    def testTimeoutCallback(self):
        self.testEndCallback()
        self.conn_timeout = True
        
    def cleanup(self):
        self.testEndCallback()