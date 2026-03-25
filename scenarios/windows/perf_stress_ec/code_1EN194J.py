import logging
import os
from parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_1EN194J.py')

    if Params.get('perf_stress_ec', 'stress_run') != '1':
        logging.info('Skipping background trace/stress scripts because stress_run is disabled')
        return

    # Existing UTC side-load setup.
    scenario._upload("utilities\\ParseUtc\\UtcPerftrack.xml", "C:\\ProgramData\\Microsoft\\Diagnosis\\Sideload")
    scenario._upload("utilities\\ParseUtc\\DisableAllUploads.json", "C:\\ProgramData\\Microsoft\\Diagnosis\\Sideload")
    scenario._call(["cmd.exe", '/C reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 3 /f > null 2>&1'])
    scenario._call(["cmd.exe", '/C reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting" /v DisableWerUpload /t REG_DWORD /d 1 /f > null 2>&1'])

    src_dir = os.path.dirname(__file__)
    repo_root = os.path.abspath(os.path.join(src_dir, "..", "..", ".."))
    dut_bin_dir = r"C:\hobl_bin"

    files_to_upload = [
        os.path.join(src_dir, "Install_Python.ps1"),
        os.path.join(src_dir, "70_percentile_stress.py"),
        os.path.join(repo_root, "scenarios", "cs_floor_resources", "cs_floor_wrapper.cmd"),
        os.path.join(repo_root, "scenarios", "cs_floor_resources", "sleep.exe"),
        os.path.join(src_dir, "Right_Click_Context_Menu.ps1"),
        os.path.join(src_dir, "Stop_PerfStress_Background.ps1"),
    ]

    scenario._remote_make_dir(dut_bin_dir)
    for src_file in files_to_upload:
        if not os.path.isfile(src_file):
            scenario.fail(f"Required file missing: {src_file}")
        logging.info(f"Uploading to DUT {dut_bin_dir}: {src_file}")
        scenario._upload(src_file, dut_bin_dir)

    # Install Python dependency before starting stress script.
    # Run this synchronously so fresh devices are ready before stress starts.
    install_ps = rf"{dut_bin_dir}\Install_Python.ps1"
    marker_file = rf"{dut_bin_dir}\.python_ready"
    marker_result = scenario._call([
        "cmd.exe",
        f'/C if exist "{marker_file}" (echo READY) else (echo MISSING)',
    ], expected_exit_code="", fail_on_exception=False)
    install_timeout = 180 if "READY" in str(marker_result) else 960
    logging.info(f"Python install timeout on DUT: {install_timeout}s")
    logging.info("Ensuring Python runtime is available on DUT.")
    scenario._call([
        "cmd.exe",
        f'/C powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "{install_ps}"',
    ], blocking=True, timeout=install_timeout)

    # Start stress script in background so scenario can proceed.
    # (Trace collection is handled by the early code_PSECTRC.py block.)
    stress_py = rf"{dut_bin_dir}\70_percentile_stress.py"
    target_cpu = Params.get('perf_stress_ec', 'stress_cpu_target')
    if target_cpu not in ['25', '50', '75']:
        target_cpu = '75'
    load_label = {
        '25': 'low',
        '50': 'medium',
        '75': 'high',
    }.get(target_cpu, 'high')
    logging.info(f"Starting 70_percentile_stress.py in minimized window with target CPU {target_cpu}% ({load_label} load).")
    scenario._call([
        "cmd.exe",
        f'/C start "" /min cmd.exe /c "where py > nul 2>&1 && py -3 \"{stress_py}\" --target-cpu {target_cpu} || python \"{stress_py}\" --target-cpu {target_cpu}"',
    ], expected_exit_code="", blocking=False)

    scenario._sleep_to_now()
            