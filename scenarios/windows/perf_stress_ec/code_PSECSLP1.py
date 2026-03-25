import logging
import os
import time
from parameters import Params
import utilities.call_rpc as rpc


def run(scenario):
    logging.debug('Executing code block: code_PSECSLP1.py')

    if Params.get('perf_stress_ec', 'stress_run') != '1':
        logging.info('Skipping mid-workload sleep/resume checkpoint because stress_run is disabled')
        return

    # Keep one deterministic sleep/resume checkpoint mid-workload.
    # Target budget: ~30s sleep transition + ~90s reconnect window (+ small overhead).
    sleep_window_seconds = 30
    wifi_off_duration_seconds = sleep_window_seconds
    disconnect_wait_seconds = 30
    reconnect_wait_seconds = 90
    poll_interval_seconds = 2

    wrapper = os.path.join(scenario.dut_exec_path, 'cs_floor_resources', 'cs_floor_wrapper.cmd')

    def _dut_alive():
        try:
            rpc.call_rpc(scenario.dut_ip, scenario.rpc_port, 'GetVersion', [], log=False, timeout=5)
            return True
        except Exception:
            return False

    logging.info('Starting mid-workload sleep/resume checkpoint')
    logging.info(
        f'Sleep window: {sleep_window_seconds}s, wifi off duration: {wifi_off_duration_seconds}s, '
        f'disconnect wait: {disconnect_wait_seconds}s, reconnect wait: {reconnect_wait_seconds}s'
    )

    scenario._call([
        'cmd.exe',
        '/C "' + wrapper + '" ' + str(wifi_off_duration_seconds) + ' ' + scenario.dut_exec_path,
    ], blocking=False)

    # Avoid racing into next UI actions while the DUT is transitioning to sleep.
    if Params.get('global', 'local_execution') != '1':
        logging.info('Waiting for DUT to enter sleep (communication drop)')
        saw_disconnect = False
        poll_count = int(disconnect_wait_seconds / poll_interval_seconds)

        for _ in range(poll_count):
            if not _dut_alive():
                saw_disconnect = True
                logging.info('Detected DUT communication loss (sleep transition started)')
                break
            time.sleep(poll_interval_seconds)

        if not saw_disconnect:
            logging.warning('Did not observe DUT disconnect before timeout; continuing to reconnect wait')

    logging.info('Waiting for DUT to resume and reconnect')
    reconnected = False
    reconnect_poll_count = int(reconnect_wait_seconds / poll_interval_seconds)
    for _ in range(reconnect_poll_count):
        if _dut_alive():
            reconnected = True
            logging.info('DUT communication restored after sleep/resume')
            break
        time.sleep(poll_interval_seconds)

    if not reconnected and Params.get('global', 'local_execution') != '1':
        raise RuntimeError(
            f'DUT did not reconnect within {reconnect_wait_seconds}s after sleep/resume checkpoint'
        )

    # Give input stack/UI a short settle window before continuing prod/web actions.
    time.sleep(10)
    scenario._sleep_to_now()
