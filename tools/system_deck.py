# SystemDeck tool

from core.parameters import Params
from core.app_scenario import Scenario
import logging
import os
import sys
import time

class Tool(Scenario):
    '''
    AMD-only.
    '''
    module = __module__.split('.')[-1]

    sys_deck = '"C:\\Program Files\\AMD SystemDeck"'
    
    def initCallback(self, scenario):
        # Initialization code
        # Keep a pointer to the scenario that this tools is being run with
        self.scenario = scenario
        self.conn_timeout = False

    def testBeginCallback(self):
        self.file_name = Params.getCalculated("test_name") + "_pm.csv"
        self._call(["powershell.exe", "start-process -verb runAs -WindowStyle Minimized -FilePath cmd '/c cd C:\\Program Files\\AMD SystemDeck\\ & AMDGraphicsManager.exe -pmlogall -pmperiod=1000 -pmoutput=" + self.file_name + " -pmstopcheck'"], blocking = False)
        time.sleep(2)
    
    def testEndCallback(self):
        self._call(["powershell.exe", "start-process -verb runAs -FilePath cmd '/c cd C:\\Program Files\\AMD SystemDeck\\ & echo > terminate.txt'"], blocking = False)
        time.sleep(5)

        if not self.conn_timeout:
            self.dut_data_path = Params.getCalculated("dut_data_path")
            # self._call(["robocopy.exe", "/MOV " + self.sys_deck + " " + self.dut_data_path + " " + self.file_name], expected_exit_code="")
            self._call(["robocopy.exe", "/copyall " + self.sys_deck + " " + self.dut_data_path + " " + self.file_name], expected_exit_code="")

    def dataReadyCallback(self):
        if Params.get('global', 'collection_enabled') != '0' and self.conn_timeout==False:
            logging.info("Parsing SystemDeck data.")
            # host call of script_path
            infile = self.scenario.result_dir + "\\" + self.scenario.testname + "_pm.csv"
            logging.info("SD data File: " + infile)
            if not os.path.exists(infile):
                logging.info("System Deck: System deck data file not found: " + infile)
                return

            outfile = self.scenario.result_dir + "\\" + self.scenario.testname + "_sd_summary.csv"
            self._host_call("python.exe utilities\\open_source\\parse_sd.py" + " -i " + infile + " -o " + outfile)

    def testTimeoutCallback(self):
        self.conn_timeout = True
