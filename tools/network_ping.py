# Pings dut every 60 seconds
# if dut does not respond to ping, charge is enabled.
# When ping is detected, charge is disabled.
#  

from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import time

class Tool(Scenario):
    '''
    Deprecated.
    '''
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'dut_ip', '')
    
    dut_ip = Params.get('global', 'dut_ip')
    

    # Need to cal charge_on.py and charge_off.py, or raritan_charge_on, and raritan_charge_off
    # Raritan calls need to specify ip address and port

    def initCallback(self, scenario):
        
        #time.sleep(5)
        while (True):
            this_ping = self._host_call("cmd.exe /c ping.exe " + self.dut_ip + " -n 4")
            #print(this_ping)
            if ("Sent = 4, Received = 4, Lost = 0 (0% loss)" in this_ping):
                logging.info("Pings detected.")
                break
            else:
                print("Ping(s) not detected.")
 
                time.sleep(10) # set to 10 seconds
        logging.info("Pings detected.")
        
    def testBeginCallback(self):
        return

    def testEndCallback(self):
        return

    def dataReadyCallback(self):
        return
    

