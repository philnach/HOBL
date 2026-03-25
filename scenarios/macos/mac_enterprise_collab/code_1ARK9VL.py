import logging
import os
from pathlib import Path
from parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_1ARK9VL.py')
    
    """Main entry point for macOS download scenario - downloads ON the DUT.
    
    Args:
        scenario: HOBL scenario object with configuration and state
    """
    module = "mac_enterprise_collab"
    
    # Download configuration
    download_url = "https://download.microsoft.com/download/0/8/b/08b0f0ba-1571-41c0-9b8a-9af8a43681ae/SurfacePro7_Win11_22621_24.121.14800.0.msi"
    download_filename = "SurfacePro7_Win11_22621_24.121.14800.0.msi"

    # Get home directory from DUT and construct iCloud Drive path
    home_dir = scenario._call(["bash", "-c \"echo $HOME\""], expected_exit_code="").strip()
    
    # iCloud Drive path on macOS (equivalent to OneDrive on Windows)
    icloud_base = f"{home_dir}/Library/Mobile Documents/com~apple~CloudDocs"
    download_dir = f"{icloud_base}/onedrivetest"
    download_path = f"{download_dir}/{download_filename}"
    
    logging.info(f"Downloading file from: {download_url}")
    logging.info(f"Saving to iCloud Drive path: {download_path}")
    logging.info(f"DUT home directory: {home_dir}")
    
    # Create directory if it doesn't exist (equivalent to Windows mkdir command)
    logging.info(f"Creating directory if needed: {download_dir}")
    scenario._call(["bash", f"-c \"mkdir -p '{download_dir}'\""], expected_exit_code="")
    
    # Verify directory was created
    check_dir = scenario._call(["bash", f"-c \"test -d '{download_dir}' && echo 'exists' || echo 'missing'\""], expected_exit_code="")
    if "missing" in check_dir:
        logging.error(f"Failed to create directory: {download_dir}")
        raise Exception(f"Directory creation failed: {download_dir}")
    
    #Start download in background on DUT using curl with nohup
    logging.info("Starting background download on DUT...")
    log_file = "/tmp/download_output.log"
    
    # Use curl to download in background
    cmd = f"nohup curl -L -o '{download_path}' '{download_url}' >{log_file} 2>&1 &"
    scenario._call(["bash", f"-c \"{cmd}\""], expected_exit_code="")
    
    # Wait a moment for process to start
    import time
    time.sleep(2)
    
    # Check if download process is running
    check_running = scenario._call(["bash", "-c \"pgrep -f curl\""], expected_exit_code="")
    
    if check_running.strip():
        download_pid = check_running.strip()
        Params.setParam(module, 'download_pid', download_pid)
        logging.info(f"Background download started with PID: {download_pid}")
    else:
        logging.error("Download process not found!")
        log_output = scenario._call(["cat", log_file], expected_exit_code="")
        logging.error(f"Download log: {log_output}")
        raise Exception("Failed to start background download")
    
    # Store download path for later verification/cleanup
    Params.setParam(module, 'download_path', download_path)