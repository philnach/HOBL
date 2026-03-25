##
# recharge
# 
# Turns on the device charger and wait until battery level reache specified threshold.
# Relies on the charge_on and charge_off scenarios.
#
# Setup instructions:
#   Set up the charge_on and charge_off paramters in the device profile.
##

import builtins
import logging
import core.app_scenario
from core.parameters import Params
import time
import subprocess

class BattMaintenance(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'upper_threshold', '70')  # Percent battery level to charge to
    Params.setDefault(module, 'lower_threshold', '40')  # Percent battery level to start charging
    Params.setDefault('charge_on', 'charge_on_call', '')
    Params.setDefault('charge_off', 'charge_off_call', '')

    # Get parameters
    upper_threshold = Params.get(module, 'upper_threshold')
    lower_threshold = Params.get(module, 'lower_threshold')
    platform = Params.get('global', 'platform')

    charge_on_call = Params.get('global', 'charge_on_call')
    charge_off_call = Params.get('global', 'charge_off_call')

    if charge_on_call == '' or charge_on_call is None:
        charge_on_call = Params.get('charge_on', 'charge_on_call')
    if charge_off_call == '' or charge_off_call is None:
        charge_off_call = Params.get('charge_off', 'charge_off_call')

    # Override collection of config data, traces, and execution of callbacks 
    Params.setOverride("global", "collection_enabled", "0")
    Params.setOverride("global", "tools", "")

    def runTest(self):
        batt_level = self.getBattLevel()            
        logging.info("Battery level: " + str(batt_level) + "  Maintaining range: [" + str(self.lower_threshold) + "," + str(self.upper_threshold) + "]")
        state = ""
        while True:
            batt_level = self.getBattLevel()            

            if state != "Charging" and batt_level < int(self.lower_threshold):
                logging.info("Battery level: " + str(batt_level) + "  Charging.")
                self._host_call(self.charge_on_call)
                state = "Charging"
            elif state != "Discharging" and batt_level >= int(self.upper_threshold):
                logging.info("Battery level: " + str(batt_level) + "  Discharging")
                self._host_call(self.charge_off_call)
                state = "Discharging"

            time.sleep(300) # sleep 5 minutes    
            

    def getBattLevel(self):
        if self.platform.lower() == "wcos":
            batt_level = int(self._call(["M:\\Tools\\Surface\\SMonitor\\SMonitorUAP.exe /radix dec /batteryrsoc"], blocking=True).split(":")[-1] )
        elif self.platform.lower() == "android":
            command = "adb "
            # if device_ip is not None:
            command = command + "-s " + str(self.dut_ip) + ":5555 "
            command = command + "shell \"dumpsys battery | grep 'level'|cut -f2 -d ':'\""
            p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True)
            out, err = p.communicate()
            actual_exit_code = p.returncode
            batt_level = out
        else:
            batt_level = self._call(["powershell.exe", "Add-Type -Assembly System.Windows.Forms; [Math]::round(([System.Windows.Forms.SystemInformation]::PowerStatus.BatteryLifePercent) * 100, 2)"])
        return int(batt_level)