import logging

def run(scenario):
    logging.debug('Executing code block: code_1ARLLJA.py')
    # Get home directory from DUT and construct iCloud Drive path
    home_dir = scenario._call(["bash", "-c \"echo $HOME\""], expected_exit_code="").strip()
    
    # iCloud Drive path on macOS (equivalent to OneDrive on Windows)
    icloud_base = f"{home_dir}/Library/Mobile Documents/com~apple~CloudDocs"
    download_dir = f"{icloud_base}/onedrivetest"  # Using same subfolder name as Windows example
    
    # Delete download directory
    logging.info(f"Deleting file download directory: {download_dir}")
    scenario._call(["bash", f"-c \"rm -rf '{download_dir}'\""], expected_exit_code="")