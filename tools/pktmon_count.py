# Netsh tool

from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import time

class Tool(Scenario):
    '''
    Count types of network packets transmitted and received.
    '''
    module = __module__.split('.')[-1]

    # Set default parameters
    Params.setDefault(module, 'comp', '')

    # Get parameters
    comp = Params.get(module, 'comp')

    def initCallback(self, scenario):
        # Initialization code
        # Keep a pointer to the scenario that this tools is being run with
        self.scenario = scenario
        self.conn_timeout = False

    def testBeginCallback(self):
        self.file_name = Params.getCalculated("test_name")
        self._call(["cmd.exe", "/C pktmon start --capture --counters-only"])
    
    def testEndCallback(self):
        self._call(["cmd.exe", "/C pktmon stop > c:\\hobl_data\\pktmon.txt"])

    def dataReadyCallback(self):
        return
    
    def testTimeoutCallback(self):
        self._call(["cmd.exe", "/C pktmon stop"])
        self.conn_timeout = True
