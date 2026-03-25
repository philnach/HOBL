import logging
from core.parameters import Params
import time

def run(scenario):
    logging.debug('Executing code block: code_16KJEV9.py')
    license_key = Params.get('mac_puget_prep', 'puget_license')

    # check if pugetbench exists on the mac
    check_puget_path = scenario._call(["bash","-c \"ls /Applications | grep 'PugetBench for Creators.app'\""], expected_exit_code="")
    
    if check_puget_path == "":
        # Attempt to download and install pugetbench
        try:
            logging.info("PugetBench not found. Downloading and installing.")
            scenario._call(["curl", " -L -o " + scenario.dut_exec_path + "/pugetbench.dmg https://download.pugetsystems.com/pugetbench/pugetbench_creators/PugetBench%20for%20Creators_1.3.20_universal.dmg?submissionGuid=51975095-e8bb-45c0-8b1d-9d42a0c86bb8"])
            logging.info("Mounting DMG...")
            scenario._call(["hdiutil", "attach " + scenario.dut_exec_path + "/pugetbench.dmg"])
            logging.info("Installing PugetBench...")
            scenario._call(["bash", "-c \"cp -R '/Volumes/PugetBench for Creators/PugetBench for Creators.app' '/Applications/'\""])
            scenario._call(["bash", "-c \"hdiutil detach '/Volumes/PugetBench for Creators'\""])            
            # Check if pugetbench installed correctly
            check_puget_path = scenario._call(["bash","-c \"ls /Applications | grep 'PugetBench for Creators.app'\""], expected_exit_code="")
            if check_puget_path == "":
                raise Exception("PugetBench installation failed. May need manual installation.")
            # delete the dmg file to save space
            scenario._call(["rm", scenario.dut_exec_path + "/pugetbench.dmg"])
        except Exception as e:
            logging.error(str(e))
            raise Exception("PugetBench installation failed. May need manual installation.")

    benchmark_exe = "/Applications/PugetBench for Creators.app/Contents/MacOS/PugetBench for Creators"
    if license_key != "":
        logging.info("Found License Key. Activating License.")
        scenario._call([benchmark_exe, "--license " + license_key])

    scenario._call(["open", '"/Applications/PugetBench for Creators.app"'])
    time.sleep(10) # Give time to let PugetBench open
