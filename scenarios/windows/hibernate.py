##
# Hibernate
#
# Setup instructions:
#   Run Rundaily Prep Script
#   Make sure that hibernation.ps1 file is copied onto working dir of DUT
#   reg keys set to enable Hibernation option 
#   Have script for triggering a button press on the device 
##

import builtins
import unittest
import logging
import time
import core.app_scenario
from core.parameters import Params
import os

class hibernate(core.app_scenario.Scenario):

    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'duration', '600')  # Seconds
    Params.setDefault(module, 'button_to_record_delay', '600')  # Seconds
    Params.setDefault(module, 'button_wake_callback', '')

    # Get parameters
    duration = Params.get(module, 'duration')
    button_to_record_delay = Params.get(module, 'button_to_record_delay')
    button_wake = Params.get(module, 'button_wake_callback')


    def setUp(self):

        # Call base setUp() which runs config_check and starts ETL tracing.
        # Prevent callack_test_begin from executing at this time
        core.app_scenario.Scenario.setUp(self, callback_test_begin="")

        # Put Device to Hibernate
        logging.info("Device hibernate now.")
        try:            
            self._call(["rundll32.exe", "powrprof.dll,SetSuspendState Hibernate"], blocking = False)
        except Exception as e:
            logging.error("Device failed to set Suspend State to Hibernation.")
            pass
        logging.info("Delaying for " + self.button_to_record_delay + " seconds before starting power measurement.")
        time.sleep(float(self.button_to_record_delay))

        # Start recording power
        self._callback(Params.get('global', 'callback_test_begin'))


    def runTest(self):
        # Hibernate for specified duration
        logging.info("Starting Hibernation for " + self.duration + " seconds")
        time.sleep(float(self.duration))

        # Stop recording power
        self._callback(Params.get('global', 'callback_test_end'))

        # Give time for Stop command to propagate
        time.sleep(2)

        # Wake Up Device
        if self.button_wake != '':
            logging.info("Calling local Button Script")
            self._host_call("powershell " + self.button_wake)
            time.sleep(41)

        if self.enable_screenshot == '1':
            self._screenshot(name="end_screen.png")            
        
    def tearDown(self):
        # Prevent callback_test_end from executing in base tearDown() method
        core.app_scenario.Scenario.tearDown(self, callback_test_end="")
        
