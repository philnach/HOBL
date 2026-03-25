# Template for creating a tool wrapper

from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys


class Tool(Scenario):
    '''
    A template that can be used for creating new tools.
    '''
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'example_parameter', 'example value')

    # Get parameters
    example_parameter = Params.get(module, 'example_parameter')

    def initCallback(self, scenario):
        # Initialization code

        # Keep a pointer to the scenario that this tools is being run with
        self.scenario = scenario

        logging.info("Example Tool - initializing, associated with scenario: " + self.scenario._module)
        logging.info("Example Tool - result_dir: " + self.scenario.result_dir)
        return

    def testBeginCallback(self):
        # result_dir contains the full path to the results directory, and ends in <testname>_<iteration>
        # _module contains just the testname
        logging.info("Example Tool - testBeginCallback for module: " + self.scenario._module)
        return

    def testEndCallback(self):
        logging.info("Example Tool - testEndCallback for module: " + self.scenario._module)
        return

    def dataReadyCallback(self):
        # You can do any post processing of data here.
        logging.info("Example Tool - dataReadyCallback for module: " + self.scenario._module)
        return
