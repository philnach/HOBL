# Template for creating a tool wrapper

from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import core.call_rpc as rpc
import os
import csv

class Tool(Scenario):
    '''
    Generate a report for the test run.
    '''
    module = __module__.split('.')[-1]
    # Set default parameters
    Params.setDefault(module, 'script', '')
    Params.setDefault(module, 'goals', '')
    Params.setDefault(module, 'template', '')
    Params.setDefault(module, 'report_level', '2')
    Params.setDefault(module, 'result_path', '')
    Params.setDefault(module, 'phase_power_type', 'Total')
    Params.setDefault(module, 'fail_on', '')
    Params.setDefault(module, 'files', 'run_info.csv study_vars.csv rundown.csv *power_data.csv maxim_summary*.csv *power_light_summary.csv *e3_power_summary.csv *ConfigPre.csv *ConfigPost.csv *top_processes.csv *socwatch.csv *.csv')
    Params.setDefault(module, 'name_prefix', '')

    # Get parameters
    script = Params.get(module, 'script')
    template = Params.get(module, 'template')
    files = Params.get(module, 'files')
    goals = Params.get('global', 'goals')
    if goals == "" or goals == None:
        goals = Params.get(module, 'goals')
    goal_limit = Params.get('global', 'goal_limit')
    warn_limit = Params.get('global', 'warn_limit')
    report_level = Params.get(module, 'report_level')
    phase_power_type = Params.get(module, 'phase_power_type')
    name_prefix = Params.get(module, 'name_prefix')
    fail_on = Params.get(module, 'fail_on')

    def initCallback(self, scenario):
        # Initialization code

        # Keep a pointer to the scenario that this tools is being run with
        self.scenario = scenario

    def testBeginCallback(self):

        # Write Study Variables to csv
        csv_name = self.scenario.result_dir + os.sep + "study_vars.csv"
        logging.debug("Writing CSV file: " + csv_name)
        with open(csv_name, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
            sv_keys = Params.getKeysForSection("study_vars")
            for key in sv_keys:
                val = Params.get("study_vars", key)
                writer.writerow(["VAR_" + key, val])

        if (self.fail_on == "") or (self.goals == ""):
            return

        logging.info("Checking if DUT is not in fail_on mode")

        if Params.get('global', 'local_execution') !='1':
            file_name = self.testname + "_ConfigPre.csv"
            source = os.path.join(self.dut_data_path, file_name)
            rpc.download(self.dut_ip, self.rpc_port, source, self.result_dir)

        goals_arg = " -g " + str(self.goals)

        fail_on_args = self.fail_on.split("|")
        fail_on_args = " -o " + ' '.join([x.strip().replace(" ", "_") for x in fail_on_args])

        logging.info(".\\hobl.cmd -e utilities.open_source.rollup_metrics" + " -r" + " -d " + self.scenario.result_dir + " -f *ConfigPre.csv" + goals_arg + fail_on_args + " -w " + self.warn_limit + " -l " + self.goal_limit  + " -p " + self.phase_power_type.replace(" ", ""))
        self._host_call(".\\hobl.cmd -e utilities.open_source.rollup_metrics" + " -r" + " -d " + self.scenario.result_dir + " -f *ConfigPre.csv" + goals_arg + fail_on_args + " -w " + self.warn_limit + " -l " + self.goal_limit  + " -p " + self.phase_power_type.replace(" ", ""))

    def reportCallback(self):    
        logging.info("Generating Run Report")
        # host call of script
        if self.script != "":
            command = f'python.exe {self.script} {self.scenario.result_dir} -l {self.report_level} -r -t {self.template}'

            if self.name_prefix != '':
                command += f' -n {self.name_prefix}'

            logging.info(command)
            self._host_call(command)

        logging.info("Files: " + self.files)
        logging.info("Goals: " + str(self.goals))
        logging.info("Warn Limit T: " + self.warn_limit)
        logging.info("Goal Limit T: " + self.goal_limit)
        
        goals_arg = ""
        if (self.goals != ""):
            goals_arg = " -g " + str(self.goals)

        fail_on_args = ""
        if (self.fail_on != ""):
            fail_on_args = self.fail_on.split("|")
            fail_on_args = " -o " + ' '.join([x.strip().replace(" ", "_") for x in fail_on_args])

        logging.info(".\\hobl.cmd -e utilities.open_source.rollup_metrics" + " -r" + " -d " + self.scenario.result_dir + " -f " + self.files + goals_arg + fail_on_args + " -w " + self.warn_limit + " -l " + self.goal_limit  + " -p " + self.phase_power_type.replace(" ", ""))
        self._host_call(".\\hobl.cmd -e utilities.open_source.rollup_metrics" + " -r" + " -d " + self.scenario.result_dir + " -f " + self.files + goals_arg + fail_on_args + " -w " + self.warn_limit + " -l " + self.goal_limit  + " -p " + self.phase_power_type.replace(" ", ""))
        self._host_call(".\\hobl.cmd -e utilities.open_source.rollup_metrics_json" + " -r" + " -d " + self.scenario.result_dir + " -f " + self.files + goals_arg + fail_on_args + " -w " + self.warn_limit + " -l " + self.goal_limit  + " -p " + self.phase_power_type.replace(" ", ""))
