# Take screenshots during scenario, where pause = the number of seconds between screenshots.
# Set pause = 0 (default) to only take screenshots at the beginning and end of the scenario.
#
# To use, add "global:tools=screenshot" and optionally "screenshot:pause=<number of seconds>"
# to the hobl command.
# 
# Need this in hobl_bin on DUT: \\ntwdata\powtel\CTF\ClientPower\Tests\x64\ScreenCapture.exe

from builtins import str
from builtins import *
import ctypes
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import os
import time
import threading
import core.call_rpc as rpc
import pandas as pd
import csv

class Tool(Scenario):
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'providers', 'power_light.wprp', desc="ETL provider files to use", valOptions=["@\\providers"], multiple=True)
    Params.setDefault(module, 'trace_duration', '300', desc="The duration of the trace in seconds")
    Params.setDefault(module, 'start_delay', '0', desc="The start delay before the trace starts in seconds")
    Params.setDefault(module, 'enable_check', '1', desc="Check the result of the trace. 0 = no check, 1 = check", valOptions=["0", "1"])
    Params.setDefault(module, 'single_run', '0', desc="Run the trace only once. 0 = no, 1 = yes", valOptions=["0", "1"])

    # Get parameters
    providers = Params.get(module, 'providers')
    trace_duration = int(Params.get(module, 'trace_duration'))
    start_delay = float(Params.get(module, 'start_delay'))
    enable_check = int(Params.get(module, 'enable_check'))
    single_run = int(Params.get(module, 'single_run'))

    
    def initCallback(self, scenario):
        self.scenario = scenario
        self.scenario.enable_tool_threading = True
        self.conn_timeout = False
        self.testResult = True
        
        provider_list = self.providers.split()
        wprStartCommand = ""

        for profile in provider_list:
            try:
                logging.debug("Attempting to move " + profile)
                scenario._upload("providers\\" + profile,
                            scenario.dut_exec_path)
                wprStartCommand = wprStartCommand + " -start " + scenario.dut_exec_path + "\\" + profile
            except:
                raise Exception("Couldn't find provider " + profile)

        self.threadException = threading.Event()

        logging.info("initalizing etl thread")
        self.thread = EtlThread(self.trace_duration, self.start_delay, self.enable_check, self.single_run, self.scenario, wprStartCommand, self.threadException)
        
        
    def testBeginCallback(self):
        logging.info("Starting etl thread")
        try:
            self.thread.start()
        except Exception as e:
            logging.error("Exception in testBeginCallback: " + str(e))
            raise Exception("Exception in testBeginCallback")
        return
        
    def testEndCallback(self):
        logging.info("Stopping screenshot thread. Stopping and saving ETL trace.")
        self.thread.event.set()
        if self.thread.activeEtl:
            try:
                self.thread.stop_etl(self.scenario)
            except:
                pass
        self.thread.join()
        return
        
    def dataReadyCallback(self):
        # Do 1 more check if test result is passed in case of another thread ending the test. 
        if self.testResult:
            if self.enable_check == 1:
                if not self.thread.check_result(self.scenario):
                    raise Exception(self.thread.error_msg)
        return

    def testTimeoutCallback(self):
        logging.info("Stopping etl thread. Stopping and saving ETL trace.")
        self.thread.event.set()
        if self.thread.activeEtl:
            self.thread.stop_etl(self.scenario)
            if self.enable_check == 1:
                if not self.thread.check_result(self.scenario):
                    self.testResult = False
                    raise Exception(self.thread.error_msg)
        self.thread.join()
        self.conn_timeout = True
    
    def toolStatusCallback(self):
        if self.threadException.is_set():
            self.thread.join()
            self.testResult = False
            self.conn_timeout = True
            return (-1, self.thread.error_msg)
        return (0, "continue test")

class EtlThread(threading.Thread):
    def __init__(self, trace_duration, start_delay, enable_check, single_run, scenario, wprStartCommand, exceptionEvent):
        threading.Thread.__init__(self)
        self.trace_duration = trace_duration
        self.start_delay = start_delay
        self.enable_check = enable_check
        self.single_run = single_run
        self.scenario = scenario
        self.wprStartCommand = wprStartCommand
        self.event = threading.Event()
        self.exceptionEvent = exceptionEvent
        self.activeEtl = False
        self.error_msg = ""

        self.setDaemon(True)
        
    def run(self):
        time.sleep(self.start_delay)
        while not self.event.is_set():
            self.start_etl()
            time.sleep(self.trace_duration)
            self.stop_etl()
            if self.enable_check == 1:
                if not self.check_result():
                    self.exceptionEvent.set()
                    self.event.set()
            if self.single_run == 1:
                self.event.set()
        return

    def start_etl(self):
        '''
        Periodically start ETL traces.
        '''
        logging.info("Starting ETL trace.")
        # Cancel any existing ETL traces
        self.scenario._call(["cmd.exe", "/c wpr.exe -cancel > null 2>&1"], expected_exit_code="")

        # start the ETL trace
        self.scenario._call(["cmd.exe", "/c wpr.exe" + self.wprStartCommand + " -filemode"])

        self.activeEtl = True

    def stop_etl(self):
        '''
        Periodically stop ETL traces.
        '''
        # stop the ETL trace
        outfile = os.path.join(self.scenario.dut_data_path, self.scenario.testname + ".etl")
        logging.info("Ending trace and saving at: " + outfile)
        self.scenario._call(["cmd.exe", "/c wpr.exe -stop " + outfile])

        self.scenario._copy_data_from_remote(self.scenario.result_dir, source=outfile, single_file=True)

        basename = os.path.join(self.scenario.result_dir, self.scenario.testname)

        self.scenario._host_call("utilities\\proprietary\\ParsePowerLight\\parse_power_light.exe -m e3 -f " + basename + ".etl" + " -o " + basename, expected_exit_code="")

        self.activeEtl = False

    def check_result(self):
        '''
        Check the top ten process for memcompression and if so then fail the test. 
        '''
        error_msg = ""
        top_ten_process = os.path.join(self.scenario.result_dir, self.scenario.testname + "_top_processes.csv") 
        if os.path.exists(top_ten_process):
            with open(top_ten_process, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if 'memcompression' in row[1]:
                        error_msg = "MemCompression found in top ten process. Test failed."
                        logging.error(error_msg)
                        self.error_msg = error_msg
                        return False
                    if 'Process crashed' in row[0]:
                        if 'Yes' in row[1]:
                            error_msg = "Process crashed. Test failed."
                            logging.error(error_msg)
                            self.error_msg = error_msg
                            return False
        else:
            logging.info(top_ten_process + " not found.")
