# Netsh tool

from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import time

class Tool(Scenario):
    '''
    Get ETL trace of wns_client.
    '''
    module = __module__.split('.')[-1]

    def initCallback(self, scenario):
        # Initialization code
        # Keep a pointer to the scenario that this tools is being run with
        self.scenario = scenario
        self.conn_timeout = False

    def testBeginCallback(self):
        self.file_name = Params.getCalculated("test_name")
        self._call(["cmd.exe", "/C" + " netsh trace start wns_client per=yes traceFile=" + self.dut_data_path + "\\NetTrace.etl"], blocking = False)
        time.sleep(2)
    
    def testEndCallback(self):
        self._call(["cmd.exe", "/C" + " netsh trace stop"], blocking = True)
        time.sleep(5)

        # if not self.conn_timeout:
        #     dut_username = Params.get('global', 'dut_username')
        #     self.trace_location = "c:\\users\\" + dut_username + "\\AppData\\local\\Temp\\NetTraces\\"
        #     self.dut_data_path = Params.getCalculated("dut_data_path")
        #     self._call(["robocopy.exe", "/MOV /s " + self.trace_location + " " + self.dut_data_path], expected_exit_code="")

    def dataReadyCallback(self):
        return

    def testTimeoutCallback(self):
        self.conn_timeout = True
