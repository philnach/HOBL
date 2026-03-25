# Powercfg tool

from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import os
import json


class Tool(Scenario):
    '''
    Deprecated.
    '''
    module = __module__.split('.')[-1]
    # Set default parameters
    #Params.setOverride("global", "tools", "")

    # Get parameters
    
    def initCallback(self, scenario):
        # Initialization code
        # Keep a pointer to the scenario that this tools is being run with
        self.scenario = scenario
     
        return

    def testBeginCallback(self):

        logging.info(self.dut_data_path + '\\' + self.testname + '_ConfigPre.json')
        PreRunFile = (self.dut_data_path + '\\' + self.testname + '_ConfigPre.json')
         # Idea is to prevent wasting time with execution when USB devices are accidentally attached, but 2 problems:
            #   1. Sometimes we need to test with devices attached, and the prompt prevents automated excecution.
            #   2. Doesn't work with remote execution.  Looking for the file in the result dir should work with both remote and local execution.

        if ( os.path.exists(PreRunFile)):
            with open(PreRunFile) as json_data:
                d = json.load(json_data)
                if d["Run Start ForeignDevices"] == "1": 
                    MessageToDisplay = '"Foreign Device Detected. Press OK to Continue.  Press CANCEL to Exit."'
                    self._host_call('utilities\\MsgPrompt.exe -MSG ' + MessageToDisplay  + ' -t 90 -tat')
        
    
   

