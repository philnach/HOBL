"""
Handles remote operations.
"""

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread, QMutex, QWaitCondition
from datetime import datetime
import call_rpc as rpc
import time
import remote
import json
import ipaddress

class ConnectionManager(QThread):
    connection_available_signal = pyqtSignal()
    connection_attempt_signal = pyqtSignal()
    connection_no_ip_signal = pyqtSignal()


    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.remote_thread = remote.RemoteThread(self.settings)
        self.dut_ip = self.settings.get("dut_ip")
        self.current_display = 0
        self.enabled = False
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()


    def connect(self):
        self.dut_ip = self.settings.get("dut_ip")

        if self.remote_thread.isRunning():
            self.remote_thread.stop()
            self.remote_thread = remote.RemoteThread(self.settings)

        try:
            ipaddress.ip_address(self.dut_ip)
        except:
            time.sleep(1)
            self.connection_no_ip_signal.emit()
            self.enabled = False
            return
        self.connection_attempt_signal.emit()
        while(1):
            success = self.simple_remote_connect()
            if success:
                success = self.remote_thread.connect()

            if success:
                break
            time.sleep(1)
            self.dut_ip = self.settings.get("dut_ip")
        self.connection_available_signal.emit()
        self.enabled = False

        self.remote_thread.finished.connect(self.resume)
        self.remote_thread.start()


    def run(self):
        self.connect()

        while(True):
            self._mutex.lock()
            while not self.enabled:
                self._wait_condition.wait(self._mutex)
            self._mutex.unlock()

            self.connect()
            self.pause()


    def pause(self):
        self._mutex.lock()
        self.enabled = False
        self._mutex.unlock()


    def resume(self):
        self._mutex.lock()
        self.enabled = True
        self._wait_condition.wakeAll()
        self._mutex.unlock()


    def set_display(self, display):
        self.current_display = display


    def simple_remote_connect(self):
        result = rpc.call_rpc(self.dut_ip, 8000, "RunWithResultAndExitCode", ["uname"])

        if result == "TIMEOUT":
            return False

        try:
            if "result" in json.loads(result):
                print("Connecting to macOS DUT")
                return self.simple_remote_connect_macos()
            else:
                print("Connecting to Windows DUT")
                return self.simple_remote_connect_windows()
        except:
            return False


    def simple_remote_connect_windows(self):
        res = rpc.plugin_load(self.dut_ip, 8000, "InputInject", "InputInject.Application", "C:\\hobl_bin\\InputInject\\InputInject.dll")
        if res == "TIMEOUT":
            print("Timeout loading plugin.")
            return False
        else:
            # Use SimpleRemote to launch ScreenServer
            result = rpc.call_rpc(self.dut_ip, 8000, "RunWithResultAndExitCode", ["cmd.exe", '/C tasklist | findstr /I "ScreenServer"'])
            if result == "TIMEOUT":
                print("Timeout killing ScreenServer.")
                return False
            result_dict = json.loads(result)
            data = result_dict["result"]
            exit_code = data[0]
            # Keep trying to kill until it doesn't exist
            while exit_code == "0":
                result = rpc.call_rpc(self.dut_ip, 8000, "RunWithResultAndExitCode", ["cmd.exe", "/C taskkill /IM ScreenServer.exe /T /F"])
                if result == "TIMEOUT":
                    print("Timeout killing ScreenServer.")
                    return False
                result = rpc.call_rpc(self.dut_ip, 8000, "RunWithResultAndExitCode", ["cmd.exe", '/C tasklist | findstr /I "ScreenServer"'])
                if result == "TIMEOUT":
                    print("Timeout killing ScreenServer.")
                    return False
                result_dict = json.loads(result)
                data = result_dict["result"]
                exit_code = data[0]
            result = rpc.call_rpc(self.dut_ip, 8000, "Run", ["c:\\hobl_bin\\ScreenServer\\ScreenServer.exe", str(self.current_display)])
            if result == "TIMEOUT":
                print('Timeout starting ScreenServer.')
                return False
            print("ScreenServer started.")
            return True


    def simple_remote_connect_macos(self):
        res = rpc.plugin_load(self.dut_ip, 8000, "InputInject", "InputInject.Application", "/Users/Shared/hobl_bin/InputInject/InputInject.dll")
        if res == "TIMEOUT":
            print("Timeout loading plugin.")
            return False
        else:
            # Use SimpleRemote to launch ScreenServer
            result = rpc.call_rpc(self.dut_ip, 8000, "RunWithResultAndExitCode", ["pgrep", "-x ScreenServer"])
            if result == "TIMEOUT":
                print("Timeout killing ScreenServer.")
                return False
            result_dict = json.loads(result)
            data = result_dict["result"]
            exit_code = data[0]
            # Keep trying to kill until it doesn't exist
            while exit_code == "0":
                result = rpc.call_rpc(self.dut_ip, 8000, "RunWithResultAndExitCode", ["killall", "ScreenServer"])
                if result == "TIMEOUT":
                    print("Timeout killing ScreenServer.")
                    return False
                result = rpc.call_rpc(self.dut_ip, 8000, "RunWithResultAndExitCode", ["pgrep", "-x ScreenServer"])
                if result == "TIMEOUT":
                    print("Timeout killing ScreenServer.")
                    return False
                result_dict = json.loads(result)
                data = result_dict["result"]
                exit_code = data[0]
            result = rpc.call_rpc(self.dut_ip, 8000, "Run", ["/Users/Shared/hobl_bin/ScreenServer/ScreenServer.app/Contents/MacOS/ScreenServer"])
            if result == "TIMEOUT":
                print('Timeout starting ScreenServer.')
                return False
            print("ScreenServer started.")
            return True


    def stop(self):
        self.remote_thread.stop()
