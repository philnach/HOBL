#--------------------------------------------------------------
#
# HOBL
# Copyright(c) Microsoft Corporation
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files(the ''Software''),
# to deal in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
# OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#--------------------------------------------------------------

import builtins
import os
import unittest
import logging
import core.app_scenario
import time
from core.parameters import Params


class RunReport(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    # Set default parameters
    Params.setDefault(module, 'script', '')
    Params.setDefault(module, 'goals', '')
    Params.setDefault(module, 'template', '')
    Params.setDefault(module, 'report_level', '2')
    Params.setDefault(module, 'result_path', '')
    Params.setDefault(module, 'phase_power_type', 'Total')
    # Params.setDefault(module, 'fail_on', 'Run Start Audio Volume (%) | Run Start Screen Brightness (%) | Run Start Charge State | Run Stop Charge State | Run Stop Battery State (%) | Run Start Battery State (%)')
    Params.setDefault(module, 'fail_on', '')
    Params.setDefault(module, 'files', 'run_info.csv study_vars.csv rundown.csv *power_data.csv maxim_summary*.csv *power_light_summary.csv *e3_power_summary.csv *ConfigPre.csv *ConfigPost.csv *top_processes.csv *socwatch.csv *.csv')
    Params.setDefault(module, 'name_prefix', '')

    # Get parameters
    result_path = Params.get(module, 'result_path')
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
    fail_on = Params.get(module, 'fail_on')

    is_prep = True

    # warn_limit = '20'
    # goal_limit = '30'

    # logging.info("Warn limit: " + str(warn_limit))
    # logging.info("Goal limit: " + str(goal_limit))

    def setUp(self):
        # Don't call base setUp so that we don't interact with DUT.
        return

    def runTest(self):
        if (self.result_path == ''):
            self.result_path = Params.getCalculated("study_result_dir")
        logging.info("Generating Run Report at: " + self.result_path)

        # host call of script
        if self.script != "":
            logging.info("python.exe " + self.script + " " + self.result_path + " -l " + self.report_level + " -r -t " + self.template)
            self._host_call("python.exe " + self.script + " " + self.result_path + " -l " + self.report_level + " -r -t " + self.template)
        logging.info("Files: " + self.files)
        logging.info("Goals: " + str(self.goals))
        logging.info("Warn limit: " + self.warn_limit)
        logging.info("Goal limit: " + self.goal_limit)

        goals_arg = ""
        if (self.goals != ""):
            goals_arg = " -g " + str(self.goals)

        fail_on_args = ""
        if (self.fail_on != ""):
            fail_on_args = self.fail_on.split("|")
            fail_on_args = " -o " + ' '.join([x.strip().replace(" ", "_") for x in fail_on_args])

        logging.info(".\hobl.cmd -e utilities.open_source.rollup_metrics" + " -r" + " -d " + self.result_path + " -f " + self.files + goals_arg + fail_on_args + " -w " + self.warn_limit + " -l " + self.goal_limit  + " -p " + self.phase_power_type.replace(" ", ""))
        self._host_call(".\hobl.cmd -e utilities.open_source.rollup_metrics" + " -r" + " -d " + self.result_path + " -f " + self.files + goals_arg + fail_on_args + " -w " + self.warn_limit + " -l " + self.goal_limit + " -p " + self.phase_power_type.replace(" ", ""))

        logging.info(".\hobl.cmd -e utilities.open_source.rollup_metrics_json" + " -r" + " -d " + self.result_path + " -f " + self.files + goals_arg + fail_on_args + " -w " + self.warn_limit + " -l " + self.goal_limit  + " -p " + self.phase_power_type.replace(" ", ""))
        self._host_call(".\hobl.cmd -e utilities.open_source.rollup_metrics_json" + " -r" + " -d " + self.result_path + " -f " + self.files + goals_arg + fail_on_args + " -w " + self.warn_limit + " -l " + self.goal_limit + " -p " + self.phase_power_type.replace(" ", ""))
    def tearDown(self):
        # Don't call base tearDown so that we don't interact with DUT.
        return

    def kill(self):
        # Prevent base kill routine from running
        return 0
