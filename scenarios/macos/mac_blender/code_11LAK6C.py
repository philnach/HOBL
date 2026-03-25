import logging
import time
import os

def run(scenario):
    logging.debug('Executing code block: code_11LAK6C.py')

    # Define paths
    zip_file = os.path.join("scenarios", "blender_resources", "benchmark-launcher-cli-mac.zip")
    extract_dir = os.path.join("scenarios", "blender_resources", "mac")
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
    mac_cli = os.path.join(extract_dir, "benchmark-launcher-cli")

    # Download the zip file if not already present
    scenario._check_and_download('benchmark-launcher-cli-mac.zip', "scenarios\\blender_resources", url='https://download.blender.org/release/BlenderBenchmark2.0/launcher/benchmark-launcher-cli-3.1.0-macos.zip')
    
    try:
        # Extract the zip file
        scenario._host_call(["cmd.exe", "/C " + f"tar -xf {zip_file} -C {extract_dir}"], expected_exit_code="")
    except:
        logging.debug("Could already being extracted, wait for extraction to finish")
        time.sleep(5)

    # Check if the .exe file already exists on the DUT
    if scenario._check_remote_file_exists("/Users/Shared/hobl_bin/benchmark-launcher-cli", False):
        logging.info("benchmark-launcher-cli already found on DUT. Skipping upload")
    else:
        logging.info("Uploading benchmark-launcher-cli to " + "/Users/Shared/hobl_bin/")
        scenario._upload(mac_cli, "/Users/Shared/hobl_bin/")

    logging.info("Removing quarantine attribute from benchmark-launcher-cli")
    try:
        scenario._call(["xattr", "-d com.apple.quarantine /Users/Shared/hobl_bin/benchmark-launcher-cli"])
    except:
        pass
    
    logging.info("Checking/Downloading Benchmark Version")
    scenario._call(["/Users/Shared/hobl_bin/benchmark-launcher-cli", "blender download 4.4.0"])

    logging.info("Checking/Downloading Benchmark Scenes")
    scenario._call(["/Users/Shared/hobl_bin/benchmark-launcher-cli", " scenes download --blender-version 4.4.0 monster junkshop classroom"])

