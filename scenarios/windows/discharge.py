##
# discharge
# 
# Wait until charge is below specified threshold
#
# Setup instructions:
#   Set up the charge_on and charge_off paramters in the device profile.
##

import logging
import subprocess
import time

from core.parameters import Params
import core.app_scenario


class Discharge(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    # Set default parameters
    Params.setDefault(module, 'resume_threshold', '100', desc="Percent battery level to discharge to")
    Params.setDefault(module, 'poll_period', '30', desc="How often to check battery level (default 30s)")
    Params.setDefault(module, 'run_scenario', '', desc="Run LVP, FishBowl, or GPU stress in the background", valOptions=["lvp", "fishbowl", "stress"])

    Params.setOverride('global', 'tools', '')
    Params.setOverride('global', 'prep_tools', '')
    Params.setOverride('global', 'collection_enabled', '0')

    # Get parameters
    resume_threshold = int(Params.get(module, 'resume_threshold'))
    charge_off_call  = Params.get('global', 'charge_off_call')
    poll_period      = int(Params.get(module, 'poll_period'))
    run_scenario     = Params.get(module, 'run_scenario')

    run_dir     = Params.getCalculated('run_dir')
    params_file = Params.getCalculated('params_file')

    is_prep = True


    def is_discharge_done(self):
        batt_level = self.getBattLevel()
        logging.info(f"Battery level: {str(batt_level)} Expected Level: {str(self.resume_threshold)}")

        if batt_level <= self.resume_threshold:
            logging.info("Discharging complete")
            return True
        return False


    def runTest(self):
        logging.info("Discharging...")
        self._host_call(self.charge_off_call)

        if self.is_discharge_done():
            return

        p = None

        if self.run_scenario.lower() == "lvp":
            logging.info(f"Starting {self.run_scenario.lower()}")

            p = subprocess.Popen([
                ".\\hobl.cmd",
                "-p", self.params_file,
                "-s", "lvp",
                f"global:result_dir_complete={self.run_dir}",
                "lvp:duration=14400",
                "global:tools=tearcheck",
                "global:post_run_delay=0"
            ], stdin=subprocess.PIPE)

            time.sleep(30)
        elif self.run_scenario.lower() == "fishbowl":
            logging.info(f"Starting {self.run_scenario.lower()}")

            p = subprocess.Popen([
                ".\\hobl.cmd",
                "-p", self.params_file,
                "-s", "fishbowl",
                f"global:result_dir_complete={self.run_dir}",
                "fishbowl:duration=14400",
                "fishbowl:fish_count=2000",
                "global:tools=tearcheck",
                "global:post_run_delay=0"
            ], stdin=subprocess.PIPE)

            time.sleep(30)
        elif self.run_scenario.lower() == "stress":
            logging.info(f"Starting {self.run_scenario.lower()}")

            p = subprocess.Popen([
                ".\\hobl.cmd",
                "-p", self.params_file,
                "-s", "stress",
                f"global:result_dir_complete={self.run_dir}",
                "stress:duration=14400",
                "stress:loads=GPU",
                "global:tools=tearcheck",
                "global:delay_between_runs=0"
            ], stdin=subprocess.PIPE)

            time.sleep(30)

        while True:
            if self.is_discharge_done():
                break
            else:
                time.sleep(int(self.poll_period))

        if p:
            logging.info(f"Stopping {self.run_scenario.lower()}")

            p.stdin.write(b"teardown\n")
            p.stdin.flush()
            p.wait()


    def getBattLevel(self):
        batt_level = self._call(["powershell.exe",
            "Add-Type -Assembly System.Windows.Forms; [Math]::round(([System.Windows.Forms.SystemInformation]::PowerStatus.BatteryLifePercent) * 100, 2)"
        ])

        return int(batt_level)


    def kill(self):
        if self.run_scenario.lower() == "lvp":
            subprocess.run([
                ".\\hobl.cmd",
                "-p", self.params_file,
                "-k", "lvp"
            ])
        elif self.run_scenario.lower() == "fishbowl":
            subprocess.run([
                ".\\hobl.cmd",
                "-p", self.params_file,
                "-k", "fishbowl"
            ])
        elif self.run_scenario.lower() == "stress":
            subprocess.run([
                ".\\hobl.cmd",
                "-p", self.params_file,
                "-k", "stress"
            ])

        return 0
