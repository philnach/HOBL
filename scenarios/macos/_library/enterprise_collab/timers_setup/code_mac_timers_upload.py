import logging
import os

def run(scenario):
    """
    Upload macOS timers executable from Host to DUT.
    Source: utilities/open_source/SimpleTimer/macos/bin/SimpleTimer (on Host)
    Target: {dut_exec_path}/mac_timers (on DUT)
    """
    logging.info('Executing timers_setup: Uploading timers executable to DUT')
    
    # Source path on Host (relative to hobl root)
    source_path = "utilities\\open_source\\SimpleTimer\\macos\\bin\\SimpleTimer"
    
    # Target directory on DUT
    target_dir = scenario.dut_exec_path
    target_name = "mac_timers"
    target_path = f"{target_dir}/{target_name}"
    
    logging.info(f"Source (Host): {source_path}")
    logging.info(f"Target (DUT): {target_path}")
    
    # Verify source file exists on Host
    if not os.path.isfile(source_path):
        logging.error(f" ERROR - Source SimpleTimer executable not found: {source_path}")
        raise FileNotFoundError(f"Source SimpleTimer executable not found: {source_path}")
    
    # Upload the timers executable to DUT
    # The _upload method copies file from Host to DUT
    logging.info("Uploading SimpleTimer executable from Host to DUT...")
    scenario._upload(source_path, target_dir)
    
    # Rename the uploaded file from 'SimpleTimer' to 'mac_timers'
    uploaded_path = f"{target_dir}/SimpleTimer"
    logging.info(f"Renaming {uploaded_path} to {target_path}...")
    scenario._call(["mv", f"{uploaded_path} {target_path}"], expected_exit_code="")
    
    # Set executable permissions
    logging.info("Setting executable permissions...")
    scenario._call(["chmod", f"+x {target_path}"], expected_exit_code="")
    
    # Verify the file exists and has correct permissions
    verify_result = scenario._call(["ls", f"-la {target_path}"], expected_exit_code="")
    logging.info(f"Verification: {verify_result}")
    
    # Check if file exists
    if not scenario._check_remote_file_exists(target_path, in_exec_path=False):
        logging.error(f" ERROR - Failed to upload mac_timers to {target_path}")
        raise Exception(f"Failed to upload mac_timers to {target_path}")
    
    logging.info(f"Successfully uploaded mac_timers to {target_path}")
