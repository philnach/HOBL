import logging
import time
import os
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_W33UMT.py')

    sleep_mode = Params.get('abl_standby', 'sleep_mode')
    standby_duration = Params.get('abl_standby', 'standby_duration')
    button_sleep = ""  # If we ever want to use the physical power button, we'll need to set this to the global:button_sleep_callback parameter.
    button_wake = ""  # If we ever want to use the physical power button, we'll need to set this to the global:button_wake_callback parameter.
    enable_active = "0"  # If we ever incorporate standby back into abl, we'll need to convert this to a parameter.
    local_execution = "0"
    wake_wait = "15"  # seconds to wait for Wi-Fi to connect after waking from standby.

    # Put Device to Sleep
    logging.info("Device sleep now.")
    # start_time = time.time()
    test_begin_callback_delay = 0

    if button_sleep != '':
        logging.info("Calling local Button Script.")
        scenario._host_call("powershell " + button_sleep)
    else:
        if sleep_mode.lower() == "s3":
            logging.info("Calling pwrtest.exe /sleep /s:3 on DUT.")
            result = scenario._call([os.path.join(scenario.dut_exec_path, "pwrtest", "pwrtest.exe"), " /sleep /s:3 /p:" + str(int(standby_duration))], blocking = False)
            print (result)
            if result is not None and 'error' in result :
                raise Exception("pwrtest.exe could not found!")
            # Compensate for the 3s delay before hitting the button in the above button.exe command.
            time.sleep(3)
        elif sleep_mode.lower() == "s1":
            logging.info("Calling pwrtest.exe /sleep /s:1 on DUT.")
            result = scenario._call([os.path.join(scenario.dut_exec_path, "pwrtest", "pwrtest.exe"), " /sleep /s:1 /p:" + str(int(standby_duration))], blocking = False)
            print (result)
            if result is not None and 'error' in result :
                raise Exception("pwrtest.exe could not found!")
            # Compensate for the 3s delay before hitting the button in the above button.exe command.
            time.sleep(3)
        else:  # Connected Standby
            logging.info("Calling Button.exe on DUT.")
            result = scenario._call(["cmd.exe", "/C timeout 3 > NUL && " + os.path.join(scenario.dut_exec_path, "button", "button.exe") + " -s " + str(int(standby_duration) * 1000)], blocking = False)
            print (result)
            if result is not None and 'error' in result :
                raise Exception("Button.exe could not found!")
            # Compensate for the 3s delay before hitting the button in the above button.exe command.
            time.sleep(3)

    logging.info("Starting standby for " + standby_duration + " seconds.")
    if local_execution != "1":
        # Wait 1s to make sure screen is off
        time.sleep(1.0)
        if enable_active == '0':
            # If only doing standby, start recording power 1s after sleep
            callback_start_time = time.time()
            scenario._callback(Params.get('global', 'callback_test_begin'))
            test_begin_callback_delay = time.time() - callback_start_time
            logging.debug("test_begin_callback_delay: {0:.2f}s".format(test_begin_callback_delay))

    # Sleep for specified duration
    if local_execution != "1":
        sleep_time = float(standby_duration) - 3.0 - test_begin_callback_delay
        logging.debug("Sleeping for {0:.2f}s until Test End Callback".format(sleep_time))
        time.sleep(sleep_time)
        # If only doing standby, stop recording power 2s before wake
        if enable_active == '0':
            scenario._callback(Params.get('global', 'callback_test_end'))
        time.sleep(2.0)

    # if scenario.record_app_launch == "1":
    #     scenario._record_phase_time('sby: run', start_time, (time.time() - start_time))

    # Trigger endTest callback to stop recording before we wake back up
    logging.info("Device should be awake now.")
    # Wake Up Device
    if button_wake != '':
        logging.info("Calling local Button Script.")
        scenario._host_call("powershell " + button_wake)

    # Give time for system to wake up before tear down
    logging.info("Waiting for " + wake_wait + " seconds for device Wi-Fi to reconnect.")
    time.sleep(int(wake_wait))
