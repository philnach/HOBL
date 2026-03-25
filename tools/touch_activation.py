
from builtins import str
from builtins import *
from core.parameters import Params
import logging
import sys
import os
import time
import datetime
import threading
import core.call_rpc as rpc
import numpy as np
import cv2
import core.app_scenario
from PIL import Image
import subprocess

class TouchDutyCycleThread(threading.Thread):
    def __init__(self, scenario_namespace, scenario, dut_ip, control_list, start_delay, timer, hostcall):
        threading.Thread.__init__(self)
        self.scenario = scenario
        self.dut_ip = dut_ip
        self.event = threading.Event()
        self.control_list = control_list
        self.start_delay = start_delay
        self.timer = timer
        self.setDaemon(True)
        self.adbLock = threading.Lock()
        self.scenario_namespace = scenario_namespace
        self._host_call = hostcall
        
    def run(self):

        # intialize vars for duty cycle
        prev = 0
        start_time = datetime.datetime.now()
        disconnect = False

        # Count time
        prev = datetime.datetime.now()

        # Start delay before duty cycle if needed
        if self.start_delay:
            time.sleep(int(self.start_delay))

        # Main loop
        while not self.event.is_set():
            # Interpret control list entries into digitizer state commands
            for entry in self.control_list:
                # NOTE: Try to keep this loop very short!
                with self.adbLock:
                    # connect if disconnected
                    if not (self.dut_ip in self._host_call("adb devices", expected_exit_code="")):
                        disconnect = True
                        logging.info("Not Connected to device, connecting to " + self.dut_ip)
                        logging.info(self._host_call("adb connect " + self.dut_ip + ":5555", expected_exit_code=""))
                    else:
                        disconnect = False

                    # Issue digitizaer state change
                    if entry[1] == 3:
                        self._host_call("ToolBoxOne.exe digitizer -t cli --sid 2 --device " + self.dut_ip + " --command \"SetSystemState State " + str(entry[0]) +"\" >> C:\\temp\\opt.txt", expected_exit_code="", cwd=".\\utilities\\Android\\ToolboxOne\\3.186.0\\x64")
                        time.sleep(0.5)
                        self._host_call("ToolBoxOne.exe digitizer -t cli --sid 1 --device " + self.dut_ip + " --command \"SetSystemState State " + str(entry[0]) +"\" >> C:\\temp\\opt.txt", expected_exit_code="", cwd=".\\utilities\\Android\\ToolboxOne\\3.186.0\\x64")
                    else:
                        self._host_call("ToolBoxOne.exe digitizer -t cli --sid" + str(entry[1]) + " --device " + self.dut_ip + " --command \"SetSystemState State " + str(entry[0]) +"\" >> C:\\temp\\opt.txt", expected_exit_code="", cwd=".\\utilities\\Android\\ToolboxOne\\3.186.0\\x64")
                    
                    # disconnect if needed
                    if disconnect:
                        logging.info("Disconnecting from " + self.dut_ip)
                        logging.info(self._host_call( "adb disconnect " + self.dut_ip + ":5555", expected_exit_code=""))
                
                # Wait duration
                time.sleep(entry[2])

            # Update time
            prev = datetime.datetime.now()

            # End cycle if time is greater than timer
            if self.timer and prev >= int(self.timer):
                return

        duration = (datetime.datetime.now() - start_time).total_seconds()
        logging.debug("Duration: " + str(duration))

class Tool(core.app_scenario.Scenario):
    '''
    Surface-only.  Digitizer debug.
    '''
    module = __module__.split('.')[-1]
    Params.setDefault(module, 'single_touch_time', '0')
    Params.setDefault(module, 'multi_touch_time', '48')
    Params.setDefault(module, 'pen_track_time', '0')
    Params.setDefault(module, 'idle_time', '12')
    # sid 3 will send commands that target both sid 1 and 2
    Params.setDefault(module, 'sid', '3')
    Params.setDefault(module, 'control_list', '')
    Params.setDefault(module, 'start_delay', '0')
    Params.setDefault(module, 'timer', '')

    single_touch_time = int(Params.get(module, 'single_touch_time'))
    multi_touch_time = int(Params.get(module, 'multi_touch_time'))
    pen_track_time = int(Params.get(module, 'pen_track_time'))
    idle_time = int(Params.get(module, 'idle_time'))
    # sid 3 will send commands that target both sid 1 and 2
    sid = int(Params.get(module, 'sid'))
    control_list = Params.get(module, 'control_list')
    start_delay = Params.get(module, 'start_delay')
    timer = Params.get(module, 'timer')

    already_started = False

    def initCallback(self, scenario):

        # Keep pointer to the scenario
        self.scenario = scenario

        # # Connect to dut using toobox
        # self._host_call(".\\android_tool.exe connect --ip " + self.dut_ip, expected_exit_code="", cwd=".\\Utilities\\Android\\android_tool")

        # # Run TPAgent
        # self._host_call(".\\android_tool.exe tpagent_restart", expected_exit_code="", cwd=".\\Utilities\\Android\\android_tool")
        # time.sleep(0.5)

        # # # Reset FW
        # # self._host_call("ToolBoxOne.exe digitizer -t cli --sid 1 --device " + self.dut_ip + " --command 'ResetFW'", expected_exit_code="", cwd=".\\utilities\\Android\\ToolboxOne\\3.186.0\\x64")
        

    def testBeginCallback(self):

        # if control list was not used then create one using state vars
        if not self.control_list:
            self.control_list = [(0, self.sid, self.single_touch_time), (2, self.sid, self.multi_touch_time), (4, self.sid, self.pen_track_time), (5, self.sid, self.idle_time)]
            
            # Remove entries with 0 second time
            for entry in self.control_list:
                if entry[2] == 0:
                    self.control_list.remove(entry)

        # Create touch duty cycle thread
        logging.info(self.control_list)
        self.thread = TouchDutyCycleThread(self, self.scenario, self.dut_ip, self.control_list, self.start_delay, self.timer, self._host_call)

        # Sarting touch duty cycle Here
        logging.info("Starting touch duty cycle")
        self.thread.start()

    def testEndCallback(self):
        return
        
    def dataReadyCallback(self):
        try:
            logging.debug("Trying self.thread")
            self.thread
        except NameError:
            logging.debug("Setting thread to None")
            self.thread = None

        if self.thread is not None:
            logging.info("Stopping touch duty cycle")
            self.thread.event.set()
            logging.info("Thread stopped")
            time.sleep(1) # Necessary delay between stopping thread and closing input to prevent EOI issue and program crash
            # self.out.stdin.close()
            # logging.debug("Stdin closed")
            # self.out.wait()
            # logging.debug("Wait done")

        # Set touch state on sid 1 and 2 to 'Disable Force'
        self._host_call("ToolBoxOne.exe digitizer -t cli --sid 2 --device " + self.dut_ip + " --command \"SetSystemState State 255\" >> C:\\temp\\opt.txt", expected_exit_code="", cwd=".\\utilities\\Android\\ToolboxOne\\3.186.0\\x64")
        time.sleep(0.5)
        self._host_call("ToolBoxOne.exe digitizer -t cli --sid 1 --device " + self.dut_ip + " --command \"SetSystemState State 255\" >> C:\\temp\\opt.txt", expected_exit_code="", cwd=".\\utilities\\Android\\ToolboxOne\\3.186.0\\x64")
        time.sleep(0.5)
        
        # Reset FW
        # self._host_call("ToolBoxOne.exe digitizer -t cli --sid 1 --device " + self.dut_ip + " --command 'ResetFW'", expected_exit_code="", cwd=".\\utilities\\Android\\ToolboxOne\\3.186.0\\x64")
        # time.sleep(0.5)


        # Kill TPAgent

        # self._host_call(".\Utilities\Android\android_tool\android_tool.exe connect --ip " + self.dut_ip)

        # Disconnect from android_tool

        # self._host_call(".\\Utilities\\Android\\android_tool\\android_tool.exe disconnect --ip " + self.dut_ip, expected_exit_code="")
        time.sleep(0.5)
        # self._host_call("adb connect " + self.dut_ip + ":5555", expected_exit_code="")


    def cleanup(self):
        logging.debug("Cleanup")
        self.dataReadyCallback()

    def testTimeoutCallback(self):
        self.dataReadyCallback()
        self.conn_timeout = True

