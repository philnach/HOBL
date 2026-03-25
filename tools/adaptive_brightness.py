# Adaptive backlight (ALS) tool

from parameters import Params
from scenarios.app_scenario import Scenario
import logging


class Tool(Scenario):
    '''
    Enable or disable adaptive brightness (Change brightness automatically when lighting changes). Returns to last mode on test end.
    Uses powercfg to set the ADAPTBRIGHT setting under sub_video for both AC and DC power schemes.
    '''
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'adaptive_brightness_enable', '0', desc="Enable or disable adaptive brightness (1=enable, 0=disable).", valOptions=["0", "1"])

    # Get parameters
    adaptive_brightness_enable = Params.get(module, 'adaptive_brightness_enable')

    # Registry key path for storing initial adaptive brightness state
    REG_KEY_PATH = r"HKLM\SOFTWARE\HOBL"
    REG_VALUE_AC = "InitialAdaptBrightAC"
    REG_VALUE_DC = "InitialAdaptBrightDC"

    def initCallback(self, scenario):
        # Initialization code
        # Keep a pointer to the scenario that this tool is being run with
        self.scenario = scenario

        # Query the current adaptive brightness state
        result = self._call(["cmd.exe", "/C powercfg -query scheme_current sub_video ADAPTBRIGHT"])
        ac_value = "0"
        dc_value = "0"
        if result:
            for line in result.splitlines():
                if "Current AC Power Setting Index" in line:
                    ac_value = "1" if "0x00000001" in line else "0"
                elif "Current DC Power Setting Index" in line:
                    dc_value = "1" if "0x00000001" in line else "0"
        logging.info(f"Initial Adaptive Brightness - AC: {ac_value}, DC: {dc_value}")

        # Check if already at the desired state
        if ac_value == self.adaptive_brightness_enable and dc_value == self.adaptive_brightness_enable:
            logging.info("Adaptive Brightness already set to %s for both AC and DC. No change needed.", self.adaptive_brightness_enable)
            return

        # Store the initial values in registry on DUT locally.
        # Using reg key to store as when it gets to cleanup() it creates a new scenario so any variables are resetted losing the initial values.
        self._call(["cmd.exe", '/C reg add "' + self.REG_KEY_PATH + '" /v ' + self.REG_VALUE_AC + ' /t REG_SZ /d "' + ac_value + '" /f'])
        self._call(["cmd.exe", '/C reg add "' + self.REG_KEY_PATH + '" /v ' + self.REG_VALUE_DC + ' /t REG_SZ /d "' + dc_value + '" /f'])

        # Set adaptive brightness to desired mode
        self._call(["cmd.exe", f"/C powercfg -setacvalueindex scheme_current sub_video ADAPTBRIGHT {self.adaptive_brightness_enable}"])
        self._call(["cmd.exe", f"/C powercfg -setdcvalueindex scheme_current sub_video ADAPTBRIGHT {self.adaptive_brightness_enable}"])
        self._call(["cmd.exe", "/C powercfg -setactive scheme_current"])
        logging.info(f"Adaptive Brightness set to: {self.adaptive_brightness_enable}")

    def testBeginCallback(self):
        return

    def testEndCallback(self):
        # Read the initial adaptive brightness values from registry
        ac_result = self._call(["cmd.exe", '/C reg query "' + self.REG_KEY_PATH + '" /v ' + self.REG_VALUE_AC], expected_exit_code="")
        dc_result = self._call(["cmd.exe", '/C reg query "' + self.REG_KEY_PATH + '" /v ' + self.REG_VALUE_DC], expected_exit_code="")

        ac_value = None
        dc_value = None

        if ac_result and self.REG_VALUE_AC in ac_result:
            ac_value = ac_result.split("REG_SZ")[-1].strip()
        if dc_result and self.REG_VALUE_DC in dc_result:
            dc_value = dc_result.split("REG_SZ")[-1].strip()

        if ac_value is not None and dc_value is not None:
            logging.info(f"Restoring Adaptive Brightness - AC: {ac_value}, DC: {dc_value}")
            self._call(["cmd.exe", f"/C powercfg -setacvalueindex scheme_current sub_video ADAPTBRIGHT {ac_value}"])
            self._call(["cmd.exe", f"/C powercfg -setdcvalueindex scheme_current sub_video ADAPTBRIGHT {dc_value}"])
            self._call(["cmd.exe", "/C powercfg -setactive scheme_current"])

            # Delete the registry keys after restoring
            self._call(["cmd.exe", '/C reg delete "' + self.REG_KEY_PATH + '" /v ' + self.REG_VALUE_AC + ' /f'], expected_exit_code="")
            self._call(["cmd.exe", '/C reg delete "' + self.REG_KEY_PATH + '" /v ' + self.REG_VALUE_DC + ' /f'], expected_exit_code="")


    def dataReadyCallback(self):
        # You can do any post processing of data here.
        return

    def cleanup(self):
        logging.debug("Cleanup")
        self.testEndCallback()
