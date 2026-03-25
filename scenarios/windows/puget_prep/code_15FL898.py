import logging
import time
from core.parameters import Params


def run(scenario):
    logging.debug('Executing code block: code_15FL898.py')
    license_key = Params.get('puget_prep', 'puget_license')
    # check if pugetbench exists on the device
    # if not scenario._check_remote_file_exists("C:\\Program Files\\PugetBench for Creators\\PugetBench for Creators.exe"):
    puget_bench_path = "C:\\Program Files\\PugetBench for Creators\\PugetBench for Creators.exe"
    check_puget_path = scenario._call(["cmd.exe", '/c if exist "' + puget_bench_path + '" echo Puget Benchmark exists'], expected_exit_code="")

    if check_puget_path == "":
        try:
            # attempt to download and install pugetbench. 
            logging.info("PugetBench not found. Downloading and installing.")
            scenario._call(["powershell.exe", "wget \\\"https://download.pugetsystems.com/pugetbench/pugetbench_creators/PugetBench%20for%20Creators_1.3.20_x64_en-US.msi?submissionGuid=c9e5a74a-9c96-48d9-b6fb-10bc3f068b31\\\" -outfile " + scenario.dut_exec_path + "\\pugetbench.msi"])

            logging.info("Installing PugetBench...")
            scenario._call(["cmd.exe", "/C start /wait " + scenario.dut_exec_path + "\\pugetbench.msi" + "  /passive /norestart"])

            # Check if pugetbench installed correctly
            check_puget_path = scenario._call(["cmd.exe", '/c if exist "' + puget_bench_path + '" echo Puget Benchmark exists'], expected_exit_code="")
            if check_puget_path == "":
                raise Exception("PugetBench installation failed. May need manual installation.")
        except Exception as e:
            logging.error(str(e))
            raise Exception("PugetBench installation failed. May need manual installation.")
        
    benchmark_exe = f"\"C:\\Program Files\\PugetBench for Creators\\PugetBench for Creators.exe\""
    if license_key != "":
        logging.info("Found License Key. Activating License.")
        scenario._call(["cmd.exe", "/C " + benchmark_exe + " --license " + license_key])
        
    scenario._call(["cmd.exe", "/C " + benchmark_exe], blocking=False)
    time.sleep(10) # Give time to let PugetBench open