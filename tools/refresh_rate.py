# Refresh rate tool (WinAppDriver UI automation only)

import time
import logging
import re
import base64
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from parameters import Params
from scenarios.app_scenario import Scenario


class Tool(Scenario):
    '''
    Set display refresh rate. Returns to last mode on test end.
    Controls settings under System -> Display -> Advanced display.
    Uses WinAppDriver UI automation for both refresh rate and DRR toggle.

    Values: 60, 120, dynamic
      - 60 or 120: sets the fixed refresh rate and turns DRR off
      - dynamic: sets refresh rate to 120 Hz then enables Dynamic Refresh Rate
    '''
    module = __module__.split('.')[-1]

    # Set default parameters
    Params.setDefault(module, 'refresh_rate', '120', desc="Target refresh rate: 60, 120, or dynamic. Leave empty to not change.", valOptions=["60", "120", "dynamic"])

    # Get parameters
    refresh_rate = Params.get(module, 'refresh_rate').strip().lower()

    # Registry key path for storing initial values
    REG_KEY_PATH = r"HKLM\SOFTWARE\HOBL"
    REG_INITIAL_REFRESH_RATE = "InitialRefreshRate"
    REG_INITIAL_DRR = "InitialDRRState"

    # --- WinAppDriver helpers ---

    def _start_driver(self):
        """Start WinAppDriver and connect with Root desktop session."""
        self._call([
            (self.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe"),
            (self.dut_ip + " " + self.app_port)],
            blocking=False
        )
        time.sleep(2)
        driver = self._launchApp({"app": "Root"})
        driver.implicitly_wait(10)
        return driver

    def _stop_driver(self, driver):
        """Close driver and kill WinAppDriver + SystemSettings."""
        try:
            driver.close()
        except Exception:
            pass
        self._kill("SystemSettings.exe")
        self._kill("WinAppDriver.exe")

    def _navigate_to_advanced_display(self, driver):
        """Open Settings and navigate to Advanced Display page."""
        self._call(["cmd.exe", '/C start ms-settings:'])
        time.sleep(1)

        # Maximize Settings window via Win32 FindWindow + ShowWindow.
        # ShowWindow(SW_MAXIMIZE) is idempotent: maximizes a windowed window, no-op if already
        # maximized. Uses FindWindow with UWP window class to get a reliable handle.
        ps_script = (
            "Add-Type -Name Win -Namespace Native -MemberDefinition @'\n"
            '[DllImport("user32.dll")] public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);\n'
            '[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);\n'
            "'@\n"
            "$h = [Native.Win]::FindWindow('ApplicationFrameWindow', 'Settings')\n"
            "if ($h -ne [IntPtr]::Zero) { [Native.Win]::ShowWindow($h, 3) }"
        )
        encoded = base64.b64encode(ps_script.encode('utf-16-le')).decode('ascii')
        self._call(["cmd.exe", f'/C powershell.exe -EncodedCommand {encoded}'], expected_exit_code="")
        time.sleep(1)

        driver.find_element_by_name("System").click()
        time.sleep(1)

        driver.find_element_by_name("Display").click()
        time.sleep(1)

        driver.find_element_by_name("Advanced display").click()
        time.sleep(1)

    # --- Refresh rate (dropdown) ---

    def setRefreshRateMode(self, driver, hz):
        """Set the refresh rate via the dropdown on the Advanced Display page.
        Assumes driver is already on the Advanced Display page.
        Returns previous rate string (e.g. '120') if changed, or None if already set."""
        # Find the refresh rate ComboBox (name varies by Windows build)
        try:
            rr_combo = driver.find_element_by_xpath(
                "//ComboBox[contains(@Name, 'refresh rate') or contains(@Name, 'Refresh rate')]"
            )
        except Exception:
            rr_combo = driver.find_element_by_name("Refresh rate")

        # Read the current selection text before expanding
        current_name = rr_combo.text
        logging.info("Current refresh rate dropdown value: %s", current_name)

        # Extract numeric Hz from current text (e.g. "120 Hz" -> "120")
        previous_hz = None
        if current_name:
            match = re.search(r'(\d+)', current_name)
            if match:
                previous_hz = match.group(1)

        # Check if already at desired rate before opening dropdown
        if previous_hz == str(hz):
            logging.info("Refresh rate already at %s Hz, no change needed.", hz)
            return None

        rr_combo.click()
        time.sleep(1)

        # Find target rate using partial match (handles "60 Hz", "60.000 Hz", etc.)
        try:
            target_rate = driver.find_element_by_name(f"{hz} Hz")
        except Exception:
            target_rate = driver.find_element_by_xpath(
                f"//*[contains(@Name, '{hz}') and contains(@Name, 'Hz')]"
            )
        time.sleep(1)

        target_rate.click()
        time.sleep(1)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Keep changes"))
        ).click()

        time.sleep(2)
        logging.info("Refresh rate set to %s Hz.", hz)
        return previous_hz

    # --- DRR (toggle) ---

    def setDynamicRefreshRate(self, driver, enabled):
        """Set the DRR toggle on the Advanced Display page.
        Assumes driver is already on the Advanced Display page.
        Returns previous state as '1' or '0', or None on failure."""
        # Scroll down to ensure DRR toggle is visible
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1)

        try:
            drr_toggle = driver.find_element_by_xpath(
                "//Button[contains(@Name, 'Dynamic refresh rate')]"
            )
        except Exception:
            drr_toggle = driver.find_element_by_name("Dynamic refresh rate")

        current_state = drr_toggle.get_attribute("Toggle.ToggleState")
        if current_state is not None:
            previous = "1" if current_state == "1" else "0"
        else:
            previous = "1" if drr_toggle.is_selected() else "0"
        logging.info("Current DRR state: %s", "on" if previous == "1" else "off")

        # Check if toggle is enabled (DRR requires a high refresh rate to be selected)
        is_enabled = drr_toggle.is_enabled()
        if not is_enabled:
            logging.warning("DRR toggle is grayed out. A higher refresh rate may need to be selected first.")
            return previous

        desired_state = "1" if enabled else "0"
        if previous != desired_state:
            drr_toggle.click()
            time.sleep(1)
            new_state = drr_toggle.get_attribute("Toggle.ToggleState")
            if new_state is not None:
                new_val = "1" if new_state == "1" else "0"
            else:
                new_val = "1" if drr_toggle.is_selected() else "0"
            logging.info("DRR toggled to: %s", "on" if new_val == "1" else "off")
        else:
            logging.info("DRR already %s, no change needed.", "on" if enabled else "off")

        return previous

    # --- Callbacks ---

    def initCallback(self, scenario):
        self.scenario = scenario

        if not self.refresh_rate:
            logging.info("No refresh rate change requested.")
            return

        want_dynamic = self.refresh_rate == "dynamic"
        target_hz = "120" if want_dynamic else self.refresh_rate

        logging.info("Starting WinAppDriver for refresh rate settings...")
        driver = self._start_driver()

        try:
            self._navigate_to_advanced_display(driver)

            # Set the fixed refresh rate
            previous_hz = self.setRefreshRateMode(driver, target_hz)
            if previous_hz is not None:
                self._call(["cmd.exe", '/C reg add "' + self.REG_KEY_PATH + '" /v ' + self.REG_INITIAL_REFRESH_RATE + ' /t REG_SZ /d "' + previous_hz + '" /f'])
                logging.info("Saved initial refresh rate: %s Hz", previous_hz)

            # Handle DRR: enable for "dynamic", disable for 120, skip for 60 (grayed out at 60)
            if want_dynamic or target_hz == "120":
                if previous_hz is not None:
                    # Re-navigate after refresh rate change
                    self._navigate_to_advanced_display(driver)
                previous_drr = self.setDynamicRefreshRate(driver, want_dynamic)
                if previous_drr is not None and previous_drr != ("1" if want_dynamic else "0"):
                    self._call(["cmd.exe", '/C reg add "' + self.REG_KEY_PATH + '" /v ' + self.REG_INITIAL_DRR + ' /t REG_SZ /d "' + previous_drr + '" /f'])
                    logging.info("Saved initial DRR state: %s", "on" if previous_drr == "1" else "off")

        except Exception as e:
            logging.warning("Refresh rate setup failed: %s", e)

        finally:
            self._stop_driver(driver)

    def testBeginCallback(self):
        return

    def testEndCallback(self):
        needs_driver = False

        # Check if DRR needs restoring
        drr_result = self._call(["cmd.exe", '/C reg query "' + self.REG_KEY_PATH + '" /v ' + self.REG_INITIAL_DRR], expected_exit_code="")
        drr_saved = None
        if drr_result and self.REG_INITIAL_DRR in drr_result:
            drr_saved = drr_result.split("REG_SZ")[-1].strip().strip('"')
            needs_driver = True

        # Check if refresh rate needs restoring
        rr_result = self._call(["cmd.exe", '/C reg query "' + self.REG_KEY_PATH + '" /v ' + self.REG_INITIAL_REFRESH_RATE], expected_exit_code="")
        rr_saved = None
        if rr_result and self.REG_INITIAL_REFRESH_RATE in rr_result:
            rr_saved = rr_result.split("REG_SZ")[-1].strip().strip('"')
            needs_driver = True

        if not needs_driver:
            return

        logging.info("Starting WinAppDriver to restore refresh rate settings...")
        driver = self._start_driver()

        try:
            self._navigate_to_advanced_display(driver)

            # Restore DRR first (before changing rate, in case DRR needs the current high rate)
            if drr_saved:
                logging.info("Restoring DRR to: %s", "on" if drr_saved == "1" else "off")
                self.setDynamicRefreshRate(driver, drr_saved == "1")
                self._call(["cmd.exe", '/C reg delete "' + self.REG_KEY_PATH + '" /v ' + self.REG_INITIAL_DRR + ' /f'], expected_exit_code="")

            # Restore refresh rate last (no re-navigation needed after)
            if rr_saved:
                logging.info("Restoring refresh rate to: %s Hz", rr_saved)
                self.setRefreshRateMode(driver, rr_saved)
                self._call(["cmd.exe", '/C reg delete "' + self.REG_KEY_PATH + '" /v ' + self.REG_INITIAL_REFRESH_RATE + ' /f'], expected_exit_code="")

        except Exception as e:
            logging.warning("Failed to restore refresh rate settings: %s", e)

        finally:
            self._stop_driver(driver)

    def dataReadyCallback(self):
        return

    def cleanup(self):
        logging.debug("Cleanup")
        self.testEndCallback()
