# Maxim tool
#
# Produces a csv trace file of subsytem power measured by Maxim power monitoring chips

from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import time
import os
import pandas as pd


class Tool(Scenario):
    '''
    Deprecated.
    '''
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'delay', '0')
    # Get parameters
    delay = Params.get(module, 'delay')

    def initCallback(self, scenario):
        # Initialization code
        # Keep a pointer to the scenario that this tools is being run with
        self.scenario = scenario
        self.conn_timeout = False
        # Copy the exe if it doesn't already exist
        if not self._check_remote_file_exists("MaximTest.exe"):
            self._upload("utilities\\x64\\maxim\\MaximTest.exe", self.dut_exec_path)

    def testBeginCallback(self):
        time.sleep(float(self.delay))
        output_file = os.path.join(self.scenario.dut_data_path, "maxim_trace_" + self.scenario._module + ".csv")
        self._call(["cmd.exe", "/c " + os.path.join(self.dut_exec_path, "MaximTest.exe") + " 2 1 5 5 > " + output_file], blocking=False)
        logging.info("Maxim power collection started.")

    def testEndCallback(self):
        self._kill("MaximTest.exe")
        logging.info("Maxim power collection stopped.")

        if self.conn_timeout:
            logging.info("Maxim power collection file deleted")
            output_file = os.path.join(self.scenario.dut_data_path, "maxim_trace_" + self.scenario._module + ".csv")
            self._call(["cmd.exe", '/c del ' + output_file], expected_exit_code="")
        
    def dataReadyCallback(self):
        if self.conn_timeout:
            return
        # Parse results here.  File will be in self.scenario.result_dir

        # Header in row 8 (starting at 0, skipping blanks)
        # Data in row 12

        try:
            infile = self.scenario.result_dir + "\\maxim_trace_" + self.scenario._module + ".csv"
            outfile = self.scenario.result_dir + "\\maxim_summary_" + self.scenario._module + ".csv"
            df=pd.read_csv(infile, sep=' *, *', index_col=0, header=8, skiprows=[10,11], skipinitialspace=True)
            # Trailing comma in trace file causes a bogus last column in the csv called "Unnamed ...", let's delete it.
            for column in df.columns:
                if "Unnamed" in column:
                    del df[column]
            # Write to csv summary file
            df.mean().to_csv(outfile, sep=',', float_format='%0.1f', header=False)
        except:
            logging.error("Unable to parse maxim data.")
            pass

    def testTimeoutCallback(self):
        self.conn_timeout = True

