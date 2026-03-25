import logging
import os
import time
from core.parameters import Params
import core.app_scenario

class MacCinebench(core.app_scenario.Scenario):
    """
    Scenario to run Cinebench on Mac, supporting singleCore and multiCore runs, collecting scores and battery rundown.
    """
    module = __module__.split('.')[-1]

    Params.setDefault(module, 'duration', '60', desc="Minimum run time in seconds")
    Params.setDefault(module, 'workload', 'multi_core', desc="Workload type: single_core or multi_core", valOptions=["single_core", "multi_core"])
    prep_version = "1"

    def setUp(self):    
        self.duration = int(Params.get(self.module, 'duration'))
        self.workload = Params.get(self.module, 'workload')

        self.package_name = f"cinebench-2024-macos"
        self.out_filename = "cinebench_output.txt"
        
        host_path = f"scenarios\\cinebench_resources\\{self.package_name}"

        # Test if already set up
        if self.checkPrepStatus([self.module + self.prep_version]):
            # Download and upload dmg
            self._check_and_download(f"{self.package_name}", path = "scenarios\\cinebench_resources")
            self._upload(f"{host_path}", self.dut_exec_path)

            # unpack the dmg and install cinebench
            self._call(["hdiutil", "attach " + self.dut_exec_path + "/" + self.package_name + "/" + "Cinebench2024_macOS.dmg"])
            logging.info("Installing Cinebench...")
            self._call(["bash", "-c \"cp -R '/Volumes/Maxon Cinebench 2024/Cinebench.app' '/Applications/'\""])
            self._call(["bash", "-c \"hdiutil detach '/Volumes/Maxon Cinebench 2024'\""])

            # delete cinebench dmg 
            self._call(["rm", "-rf " + self.dut_exec_path + "/" + self.package_name])
            self.createPrepStatusControlFile(self.prep_version)

        super().setUp()


    def runTest(self):
        if self.workload == 'single_core':
            workload_arg = 'g_CinebenchCpu1Test=true'
        else:
            workload_arg = 'g_CinebenchCpuXTest=true'
        logging.info("Cinebench started.")
        cinebench_exe = "/Applications/Cinebench.app/Contents/MacOS/Cinebench"
        results = self._call([cinebench_exe, workload_arg + f" g_CinebenchMinimumTestDuration={self.duration}"], timeout=self.duration + 1200)
        # write the results to output file. On macos
        with open(os.path.join(self.result_dir, self.out_filename), 'w', encoding='utf-8') as f:
            f.write(results)

        logging.info("Cinebench completed.")


    def tearDown(self):
        logging.info("Tearing down Cinebench scenario.")
       
        # Extract score from output file
        output_file = os.path.join(self.result_dir, self.out_filename)
        logging.info(f"Extracting score from {output_file}")
        with open(output_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("CB "):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            score = float(parts[1])
                        except ValueError:
                            logging.error(f"Failed to convert score to float: {parts[1]}")

        # Write score to cinebench.csv
        with open(self.result_dir + '\\cinebench.csv', 'w') as out:
            out.write(f"Cinebench Score,{score}\n")

        super().tearDown()
        # core.app_scenario.Scenario.tearDown(self)
        logging.info(f"Cinebench score: {score}")

