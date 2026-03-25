import logging
import os
import time

def run(scenario):
    logging.debug('Executing code block: code_1AMVJC3.py')
        
    # Define paths
    target_dir = scenario.dut_exec_path
    exec_name = "mac_timers"
    # SimpleTimer interface: <timer_period_ms> <busy_period_ms> <total_duration_s>
    # 8ms period, 3ms busy work, 2400s (40 min) runtime
    args = ["8", "3", "2400"]
    exec_path = f"{target_dir}/mac_timers"
    
    logging.info(f"Executable path: {exec_path}")
    
    # Check if directory exists on DUT
    check_dir = scenario._call(["bash", f"-c \"test -d '{target_dir}' && echo 'exists' || echo 'missing'\""], expected_exit_code="")
    if "missing" in check_dir:
        logging.error(f"Directory not found on DUT: {target_dir}")
        raise Exception(f"Directory not found: {target_dir}")
    
    # Check if executable exists on DUT (use in_exec_path=False since we have full path)
    if not scenario._check_remote_file_exists(exec_path, in_exec_path=False):
        logging.error(f"Executable not found on DUT: {exec_path}")
        raise Exception(f"Executable not found: {exec_path}")
    
    # Ensure executable permission
    logging.info("Setting executable permission...")
    scenario._call(["bash", f"-c \"chmod +x '{exec_path}'\""], expected_exit_code="")
    
    # Verify file permissions
    perms = scenario._call(["ls", f"-l {exec_path}"], expected_exit_code="")
    logging.info(f"File permissions: {perms}")
    
    # Build the command to run timers with arguments
    args_str = " ".join(args)
    
    # Try running in foreground first to see any errors
    logging.debug("Testing timers execution (foreground)...")
    try:
        test_result = scenario._call(["bash", f"-c \"timeout 2 {exec_path} {args_str} || echo 'timeout or error'\""], expected_exit_code="")
        logging.debug(f"Test run output: {test_result}")
        logging.debug(f"Args: {args_str}")
    except Exception as e:
        logging.warning(f"Test run failed: {e}")
    
    # Now try background execution with output to a file
    logging.info("Starting timers in background with logging...")
    log_file = "/tmp/timers_output.log"
    logging.info(f"Command: {exec_path} {args_str}")
    scenario._call(["bash", f"-c \"nohup {exec_path} {args_str} >{log_file} 2>&1 &\""], expected_exit_code="")
    
    # Wait for process to start
    time.sleep(2)
    
    # Check if process is running
    check_running = scenario._call(["bash", "-c \"pgrep -f timers\""], expected_exit_code="")
    
    if check_running.strip():
        logging.info(f"Timers running with PID: {check_running.strip()}")
        # Store PID in scenario for later cleanup
        scenario.timers_pid = check_running.strip()
    else:
        logging.error("Timers process not found!")
        # Check the log file for errors
        log_output = scenario._call(["cat", log_file], expected_exit_code="")
        logging.error(f"Timers log output: {log_output}")
        raise Exception("Failed to start timers process")
    
    # Verify it's actually running
    ps_output = scenario._call(["bash", "-c \"ps aux | grep timers | grep -v grep\""], expected_exit_code="")
    logging.info(f"Process status: {ps_output}")