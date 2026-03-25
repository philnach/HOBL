from parameters import Params
from scenarios.app_scenario import Scenario
import base64
import logging
import re
import time


class Tool(Scenario):
    '''
    Set HDR on/off with optional Auto HDR control. Returns to last mode on test end.
    Attempts full HDR first (MonitorDataStore + Win+Alt+B toggle).
    Falls back to vHDR (VideoSettings registry) if no HDR-capable monitors found.
    Auto HDR is controlled via DirectXUserGlobalSettings registry.
    '''
    module = __module__.split(".")[-1]

    Params.setDefault(module, "hdr_enable", "1", desc="Enable HDR (1/0).", valOptions=["1", "0"])
    hdr_enable = Params.get(module, "hdr_enable")

    Params.setDefault(module, "hdr_autohdr", "0", desc="Enable Auto HDR (1/0). Only applies when hdr_enable=1.", valOptions=["1", "0"])
    hdr_autohdr = Params.get(module, "hdr_autohdr")

    REG_KEY_PATH = r"HKLM\SOFTWARE\HOBL"
    REG_VALUE_NAME = "InitialHDRState"
    REG_HDR_MODE = "HDRMode"
    REG_INITIAL_AUTO_HDR = "InitialAutoHDRState"

    HDR_REG_PATH = r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\VideoSettings"
    HDR_REG_VALUE = "EnableHDRForPlayback"

    MONITOR_DATA_STORE = r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\MonitorDataStore"

    DIRECTX_USER_PREFS = r"HKCU\Software\Microsoft\DirectX\UserGpuPreferences"
    DIRECTX_GLOBAL_SETTINGS = "DirectXUserGlobalSettings"

    # --- Auto HDR helpers ---

    def _get_auto_hdr_state(self):
        """Read AutoHDREnable from DirectXUserGlobalSettings. Returns '1', '0', or None."""
        result = self._call(["cmd.exe", f'/C reg query "{self.DIRECTX_USER_PREFS}" /v "{self.DIRECTX_GLOBAL_SETTINGS}"'], expected_exit_code="")
        if not result or self.DIRECTX_GLOBAL_SETTINGS not in result:
            return None
        match = re.search(r'REG_SZ\s+(.+)', result)
        if not match:
            return None
        settings_str = match.group(1).strip()
        for pair in settings_str.split(";"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                if key.strip() == "AutoHDREnable":
                    return value.strip()
        return None

    def _set_auto_hdr_state(self, enabled):
        """Set AutoHDREnable in DirectXUserGlobalSettings, preserving other values."""
        desired_value = "1" if enabled else "0"
        result = self._call(["cmd.exe", f'/C reg query "{self.DIRECTX_USER_PREFS}" /v "{self.DIRECTX_GLOBAL_SETTINGS}"'], expected_exit_code="")

        if result and self.DIRECTX_GLOBAL_SETTINGS in result:
            match = re.search(r'REG_SZ\s+(.+)', result)
            if match:
                settings_str = match.group(1).strip()
                pairs = settings_str.split(";")
                found = False
                new_pairs = []
                for pair in pairs:
                    if "=" in pair:
                        key, _ = pair.split("=", 1)
                        if key.strip() == "AutoHDREnable":
                            new_pairs.append(f"AutoHDREnable={desired_value}")
                            found = True
                        else:
                            new_pairs.append(pair)
                    elif pair.strip():
                        new_pairs.append(pair)
                if not found:
                    new_pairs.append(f"AutoHDREnable={desired_value}")
                new_settings = ";".join(new_pairs)
            else:
                new_settings = f"AutoHDREnable={desired_value}"
        else:
            new_settings = f"AutoHDREnable={desired_value}"

        self._call(["cmd.exe", f'/C reg add "{self.DIRECTX_USER_PREFS}" /v "{self.DIRECTX_GLOBAL_SETTINGS}" /t REG_SZ /d "{new_settings}" /f'], expected_exit_code="")
        logging.info("Set AutoHDREnable to %s (full value: %s)", desired_value, new_settings)

    # --- Full HDR helpers ---

    def _find_hdr_monitors(self):
        """Search MonitorDataStore for monitors with an HDREnabled key.
        Returns a list of (registry_subkey_path, int_value) tuples."""
        result = self._call(["cmd.exe", f'/C reg query "{self.MONITOR_DATA_STORE}" /s /v HDREnabled'], expected_exit_code="")
        monitors = []
        if not result:
            return monitors
        current_key = None
        for line in result.splitlines():
            stripped = line.strip()
            if stripped.upper().startswith("HKEY_LOCAL_MACHINE") or stripped.upper().startswith("HKLM"):
                current_key = stripped
            elif "HDREnabled" in stripped and current_key:
                match = re.search(r'HDREnabled\s+REG_DWORD\s+(0x[0-9a-fA-F]+)', stripped)
                if match:
                    monitors.append((current_key, int(match.group(1), 16)))
                    current_key = None
        return monitors

    def _get_full_hdr_state(self):
        """Return True if full HDR is currently enabled, False if disabled, None if unavailable."""
        monitors = self._find_hdr_monitors()
        if not monitors:
            return None
        return monitors[0][1] != 0

    def _send_win_alt_b(self):
        """Simulate Win+Alt+B key combination on the DUT to toggle HDR."""
        ps_script = (
            'Add-Type -TypeDefinition \'\n'
            'using System;\n'
            'using System.Runtime.InteropServices;\n'
            'public class KbdSim {\n'
            '    [DllImport("user32.dll")]\n'
            '    static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);\n'
            '    public static void SendWinAltB() {\n'
            '        keybd_event(0x5B, 0, 0, 0);\n'
            '        keybd_event(0x12, 0, 0, 0);\n'
            '        keybd_event(0x42, 0, 0, 0);\n'
            '        keybd_event(0x42, 0, 2, 0);\n'
            '        keybd_event(0x12, 0, 2, 0);\n'
            '        keybd_event(0x5B, 0, 2, 0);\n'
            '    }\n'
            '}\n'
            "'\n"
            '[KbdSim]::SendWinAltB()'
        )
        encoded = base64.b64encode(ps_script.encode('utf-16-le')).decode('ascii')
        self._call(["cmd.exe", f'/C powershell.exe -EncodedCommand {encoded}'], expected_exit_code="")

    def _toggle_full_hdr(self, desired_on):
        """Toggle full HDR to the desired state if needed. Returns True on success."""
        current_on = self._get_full_hdr_state()
        if current_on is None:
            return False

        if current_on == desired_on:
            logging.info("Full HDR already %s, no toggle needed.", "enabled" if desired_on else "disabled")
            return True

        logging.info("Toggling full HDR via Win+Alt+B...")
        self._send_win_alt_b()
        time.sleep(3)

        new_state = self._get_full_hdr_state()
        if new_state == desired_on:
            logging.info("Full HDR successfully set to %s.", "enabled" if desired_on else "disabled")
        else:
            logging.warning("Full HDR toggle verification: expected %s but got %s.", "enabled" if desired_on else "disabled", "enabled" if new_state else "disabled")
        return True

    # --- vHDR helpers (fallback) ---

    def _apply_vhdr_state(self, state: str):
        state = state.lower()
        if state == "1":
            value = 1
        elif state == "0":
            value = 0
        else:
            msg = "Unsupported HDR state '%s'. Use '1' or '0'." % state
            logging.error(msg)
            self.fail(msg)
            return
        self._call(["cmd.exe", f'/C reg add "{self.HDR_REG_PATH}" /v "{self.HDR_REG_VALUE}" /t REG_DWORD /d {value} /f'], expected_exit_code="")

    # --- Callbacks ---

    def initCallback(self, scenario):
        self.scenario = scenario
        desired_hdr_on = self.hdr_enable == "1"
        desired_auto_hdr = self.hdr_autohdr == "1"

        # Try full HDR first
        monitors = self._find_hdr_monitors()
        if monitors:
            logging.info("Found %d HDR-capable monitor(s). Using full HDR mode.", len(monitors))
            initial_hdr_on = monitors[0][1] != 0
            initial_state = "1" if initial_hdr_on else "0"
            logging.info("Initial full HDR state: %s", initial_state)

            # Save and log initial Auto HDR state
            initial_auto_hdr = self._get_auto_hdr_state()
            if initial_auto_hdr is None:
                initial_auto_hdr = "0"
            logging.info("Initial Auto HDR state: %s", initial_auto_hdr)

            # Determine if any change is needed
            hdr_needs_change = initial_hdr_on != desired_hdr_on
            auto_hdr_needs_change = desired_hdr_on and initial_auto_hdr != ("1" if desired_auto_hdr else "0")

            if hdr_needs_change or auto_hdr_needs_change:
                # Store initial states in registry (only if we're actually changing something)
                self._call(["cmd.exe", f'/C reg add "{self.REG_KEY_PATH}" /v "{self.REG_VALUE_NAME}" /t REG_SZ /d "{initial_state}" /f'], expected_exit_code="")
                self._call(["cmd.exe", f'/C reg add "{self.REG_KEY_PATH}" /v "{self.REG_HDR_MODE}" /t REG_SZ /d "full" /f'], expected_exit_code="")
                self._call(["cmd.exe", f'/C reg add "{self.REG_KEY_PATH}" /v "{self.REG_INITIAL_AUTO_HDR}" /t REG_SZ /d "{initial_auto_hdr}" /f'], expected_exit_code="")

                # Set Auto HDR registry before toggling HDR
                self._set_auto_hdr_state(desired_auto_hdr)

                if hdr_needs_change:
                    # HDR state needs to change - toggle picks up Auto HDR automatically
                    self._toggle_full_hdr(desired_hdr_on)
                else:
                    # HDR already on, but Auto HDR changed - double-toggle to apply
                    logging.info("Double-toggling HDR to apply Auto HDR change...")
                    self._send_win_alt_b()
                    time.sleep(3)
                    self._send_win_alt_b()
                    time.sleep(3)
            else:
                logging.info("HDR and Auto HDR already in desired state.")

            logging.info("HDR enable=%s, autohdr=%s", self.hdr_enable, self.hdr_autohdr)
            return

        # Fall back to vHDR
        if desired_auto_hdr:
            logging.warning("Auto HDR is not supported in vHDR mode. Ignoring hdr_autohdr setting.")
        logging.info("No HDR-capable monitors found. Falling back to vHDR mode.")
        result = self._call(["cmd.exe", f'/C reg query "{self.HDR_REG_PATH}" /v "{self.HDR_REG_VALUE}"'], expected_exit_code="")

        if not result or self.HDR_REG_VALUE not in result:
            initial_on = False
        else:
            text = result.lower()
            initial_on = "0x0" not in text

        initial_state = "1" if initial_on else "0"
        logging.info("Initial vHDR state: %s", initial_state)

        if initial_state != self.hdr_enable:
            self._call(["cmd.exe", f'/C reg add "{self.REG_KEY_PATH}" /v "{self.REG_VALUE_NAME}" /t REG_SZ /d "{initial_state}" /f'], expected_exit_code="")
            self._call(["cmd.exe", f'/C reg add "{self.REG_KEY_PATH}" /v "{self.REG_HDR_MODE}" /t REG_SZ /d "vhdr" /f'], expected_exit_code="")
            self._apply_vhdr_state(self.hdr_enable)
            logging.info("vHDR state set to: %s", self.hdr_enable)
        else:
            logging.info("vHDR already at desired state: %s", self.hdr_enable)

    def testBeginCallback(self):
        return

    def testEndCallback(self):
        # Determine which mode was used
        mode_result = self._call(["cmd.exe", f'/C reg query "{self.REG_KEY_PATH}" /v "{self.REG_HDR_MODE}"'], expected_exit_code="")
        use_full_hdr = False
        if mode_result and self.REG_HDR_MODE in mode_result:
            try:
                mode = mode_result.split("REG_SZ")[-1].strip().strip('"').lower()
                use_full_hdr = mode == "full"
            except Exception:
                pass

        # Read stored initial Auto HDR state
        initial_auto_hdr = None
        if use_full_hdr:
            auto_hdr_result = self._call(["cmd.exe", f'/C reg query "{self.REG_KEY_PATH}" /v "{self.REG_INITIAL_AUTO_HDR}"'], expected_exit_code="")
            if auto_hdr_result and self.REG_INITIAL_AUTO_HDR in auto_hdr_result:
                try:
                    initial_auto_hdr = auto_hdr_result.split("REG_SZ")[-1].strip().strip('"')
                except Exception as e:
                    logging.warning("Failed to parse InitialAutoHDRState: %s", e)

        # Read stored initial HDR state and restore
        result = self._call(["cmd.exe", f'/C reg query "{self.REG_KEY_PATH}" /v "{self.REG_VALUE_NAME}"'], expected_exit_code="")

        if result and self.REG_VALUE_NAME in result:
            try:
                initial_state = result.split("REG_SZ")[-1].strip().strip('"').lower()
                logging.info("Restoring HDR state to: %s (mode: %s)", initial_state, "full" if use_full_hdr else "vhdr")
                if use_full_hdr:
                    desired_hdr_on = initial_state == "1"

                    # Restore Auto HDR registry first
                    auto_hdr_changed = False
                    if initial_auto_hdr is not None:
                        current_auto_hdr = self._get_auto_hdr_state()
                        auto_hdr_changed = current_auto_hdr != initial_auto_hdr
                        self._set_auto_hdr_state(initial_auto_hdr == "1")

                    current_hdr_on = self._get_full_hdr_state()
                    if current_hdr_on != desired_hdr_on:
                        # HDR state change needed - toggle picks up Auto HDR
                        self._toggle_full_hdr(desired_hdr_on)
                    elif auto_hdr_changed and desired_hdr_on:
                        # HDR already correct, but Auto HDR needs refresh
                        logging.info("Double-toggling HDR to restore Auto HDR state...")
                        self._send_win_alt_b()
                        time.sleep(3)
                        self._send_win_alt_b()
                        time.sleep(3)
                else:
                    self._apply_vhdr_state(initial_state)
            except Exception as e:
                logging.warning("Failed to restore HDR state: %s", e)

        # Clean up stored values
        self._call(["cmd.exe", f'/C reg delete "{self.REG_KEY_PATH}" /v "{self.REG_VALUE_NAME}" /f'], expected_exit_code="")
        self._call(["cmd.exe", f'/C reg delete "{self.REG_KEY_PATH}" /v "{self.REG_HDR_MODE}" /f'], expected_exit_code="")
        self._call(["cmd.exe", f'/C reg delete "{self.REG_KEY_PATH}" /v "{self.REG_INITIAL_AUTO_HDR}" /f'], expected_exit_code="")

    def dataReadyCallback(self):
        return

    def cleanup(self):
        logging.debug("Cleanup")
        self.testEndCallback()
