# Produce a table of the running processes and the estimated energy they consume

from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import pandas as pd
import logging
import sys
import os
import re


class Tool(Scenario):
    '''
    Collect and parse framerate and timing data.  Does not have a significant impact on power consumption.
    '''
    module = __module__.split('.')[-1]
    # Set default parameters


    def initCallback(self, scenario):
        # Keep a pointer to the scenario that this tools is being run with
        self.scenario = scenario
        self.conn_timeout = False
        logging.info("Frame Data Tool - initializing, associated with scenario: " + self.scenario._module) 

        # Getting global providers and adding to the list with etl_trace providers
        all_providers = Params.getCalculated('trace_providers')
        all_providers = all_providers + " abl_perf.wprp"
        Params.setCalculated('trace_providers', all_providers)
  
    def dataReadyCallback(self):
        if self.conn_timeout and self.rundown_mode=='0' and int(self.stop_soc) <= 0:
            return
        # ETL traces have been pulled back to the host
        # result_dir contains the full path to the results directory, and ends in <testname>_<iteration>

        etl_trace = self.scenario.result_dir + "\\" + self.scenario.testname + ".etl"
        logging.info("ETL trace: " + etl_trace)
        if not os.path.exists(etl_trace):
            logging.info("Frame Data Tool: Trace file not found: " + etl_trace)
            return

        logging.info("Frame Data Tool - Running ParseFrameData.exe on " + etl_trace)
        self._host_call("utilities\\proprietary\\ParseFrameData\\ParseFrameData.exe " + etl_trace, expected_exit_code="")


    def testTimeoutCallback(self):
        self.conn_timeout = True

