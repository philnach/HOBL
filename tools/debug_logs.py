"""
//--------------------------------------------------------------
//
// HOBL
// Copyright(c) Microsoft Corporation
// All rights reserved.
//
// MIT License
//
// Permission is hereby granted, free of charge, to any person obtaining
// a copy of this software and associated documentation files(the ""Software""),
// to deal in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies
// of the Software, and to permit persons to whom the Software is furnished to do so,
// subject to the following conditions :
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
// FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS
// OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
// OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//
//--------------------------------------------------------------
"""
# Tool wrapper for audio control

from builtins import str
from builtins import *
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import sys
import os
import decimal
import time
import re
import collections
import csv
import zipfile
import glob

class Tool(Scenario):
    '''
    Deprecated.
    '''
    module = __module__.split('.')[-1]

    # Set default parameters
    #Params.setDefault(module, 'mute', "False")
    Params.setDefault(module, 'bugreport', "1")
    Params.setDefault(module, 'appVersion', "0")

    # Get parameters
    platform = Params.get('global', 'platform')
    result_dir = Params.get('global', 'result_dir')
    dut_ip = Params.get('global', 'dut_ip')
    platformVersion = Params.get('global', 'platformVersion')
    appVersion = Params.get(module, 'appVersion')
    # additional_logs = Params.get(module, 'additional_logs')
    additional_logs = "0"
    bugreport = Params.get(module, 'bugreport')
    #mute = Params.get(module, 'mute')

    def initCallback(self, scenario):

        # Keep pointer to scenario
        self.scenario = scenario

        # Enable full wake history
        if self.platform.lower() == "android":
            attached_devices = ""
            my_device = ""
            try:
                attached_devices = self._host_call("adb devices", expected_exit_code="")
                my_device = (re.search(str(self.dut_ip) + r'[^\r]+', str(attached_devices), flags=re.MULTILINE)).group()
            except:
                pass
            logging.info(my_device)

            if(my_device != "" and "offline" not in my_device.lower()):
                logging.info("Saving pretest debug logs to: " + self.result_dir)

                # Root device
                self._host_call("adb -s " + self.dut_ip + ":5555 root", expected_exit_code="")
                time.sleep(1)

                # Get the build type
                self.build = self._host_call("adb -s " + self.dut_ip + ":5555 shell getprop ro.product.build.variant", expected_exit_code="")

                # Battery Stats
                self._host_call("adb -s " + self.dut_ip + ":5555 shell dumpsys batterystats --enable full-wake-history", expected_exit_code="")
                time.sleep(1)

                self._host_call("adb -s " + self.dut_ip + ":5555 shell dumpsys batterystats --reset", expected_exit_code="")
                time.sleep(1)

                # echo commands (from additional logs)
                self._host_call("adb -s " + self.dut_ip + ":5555 shell \"echo 0 > /proc/sys/kernel/printk\"", expected_exit_code="")
                time.sleep(1)

                self._host_call("adb -s " + self.dut_ip + ":5555 shell \"echo 1 > /sys/module/msm_show_resume_irq/parameters/debug_mask\"", expected_exit_code="")
                time.sleep(1)

                self._host_call("adb -s " + self.dut_ip + ":5555 shell \"echo Y > /sys/module/printk/parameters/console_suspend\"", expected_exit_code="")
                time.sleep(1)

                # Set Dev build only options
                if (self.build.lower() == "developer" or self.build.lower() == "dev"):
                    # Remount device
                    self._host_call("adb.exe -s " + self.dut_ip + ":5555 remount", expected_exit_code="")
                    time.sleep(1)

                    self._host_call("adb -s " + self.dut_ip + ":5555 shell \"echo 0 > /sys/module/qpnp_rtc/parameters/poweron_alarm\"", expected_exit_code="") # TODO: Not Working even with dev remount
                    time.sleep(1)

                    self._host_call("adb -s " + self.dut_ip + ":5555 shell \"echo 1 > /sys/kernel/debug/clk/debug_suspend\"", expected_exit_code="")
                    time.sleep(1)

                    self._host_call("adb -s " + self.dut_ip + ":5555 shell \"echo 32 > /sys/module/msm_pm/parameters/debug_mask\"", expected_exit_code="") # TODO: Not Working even with dev remount
                    time.sleep(1)

                    self._host_call("adb -s " + self.dut_ip + ":5555 shell \"echo 8 > /sys/module/mpm_of/parameters/debug_mask\"", expected_exit_code="") # TODO: Not Working even with dev remount
                    time.sleep(1)

                    # lpm stats
                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/lpm_stats/stats > " + self.result_dir + "\\lpm_stats_before_idle.txt", expected_exit_code="")
                    time.sleep(1)

                    # wakelocks
                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/wakeup_sources > " + self.result_dir + "\\wakelocks_before.txt", expected_exit_code="")
                    time.sleep(1)

                # set prop commands for sensors (from addition logs)
                self._host_call("adb -s " + self.dut_ip + ":5555 shell \"setprop persist.vendor.debug.sensors.hal v\"", expected_exit_code="")
                time.sleep(1)

                self._host_call("adb -s " + self.dut_ip + ":5555 shell \"setprop persist.debug.sensors.hal v\"", expected_exit_code="")
                time.sleep(1)

                self._host_call("adb -s " + self.dut_ip + ":5555 shell \"setprop persist.debug.sensors.daemon v\"", expected_exit_code="")
                time.sleep(1)

                self._host_call("adb -s " + self.dut_ip + ":5555 shell \"setprop persist.vendor.sensors.debug.hal v\"", expected_exit_code="")
                time.sleep(1)

                self._host_call("adb -s " + self.dut_ip + ":5555 shell \"setprop persist.vendor.debug.sensors.daemon v\"", expected_exit_code="")
                time.sleep(1)

                # System sleep stats
                self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /sys/power/soc_sleep/stats > " + self.result_dir + "\\system_sleep_before.txt", expected_exit_code="")
                time.sleep(1)

                # soc sleep stats
                # self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /sys/power/soc_sleep/stats > " + self.result_dir + "\\soc_sleep_before.txt", expected_exit_code="")
                # time.sleep(1)

                # rpmh stats
                self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /sys/power/rpmh_stats/master_stats > " + self.result_dir + "\\rpmh_stats_before_idle.txt", expected_exit_code="")
                time.sleep(1)

                # interrupts
                self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /proc/interrupts > " + self.result_dir + "\\interrupts_before.txt", expected_exit_code="")
                time.sleep(1)

                # sensorservice
                self._host_call("adb -s " + self.dut_ip + ":5555 shell dumpsys sensorservice > " + self.result_dir + "\\sensorservice_before.txt", expected_exit_code="")
                time.sleep(1)

                # Get date
                self._host_call("adb -s " + self.dut_ip + ":5555 shell date > " + self.result_dir + "\\testtime.txt", expected_exit_code="")
                time.sleep(1)

                # locat and dmesg

                # adb shell "logcat -c"
                # adb shell "dmesg -C"

                # Collect additional logs
                if self.additional_logs == "1":
                    self._host_call("mkdir " + self.result_dir + "\\additional_logs", expected_exit_code="")
                    time.sleep(1)

                    self._host_call(".\\Utilities\\Android\\AdditionalLogs\\_before_test_ver5.bat " + self.result_dir + "\\additional_logs", expected_exit_code="")
                    time.sleep(1)

        return

    def testBeginCallback(self):
        pass

    def testEndCallback(self):
        pass

    def dataReadyCallback(self):
        if self.platform.lower() == "android":
            attached_devices = ""
            my_device = ""
            try:
                attached_devices = self._host_call("adb devices", expected_exit_code="")
                my_device = (re.search(str(self.dut_ip) + r'[^\r]+', str(attached_devices), flags=re.MULTILINE)).group()
            except:
                pass
            logging.info(my_device)

            if(my_device != "" and "offline" not in my_device.lower()):
                # Use adb command to fetch batery stats
                logging.info("Saving after test debug logs to: " + self.result_dir)

                # root device
                self._host_call("adb -s " + self.dut_ip + ":5555 root", expected_exit_code="")
                time.sleep(1)

                # Get date
                self._host_call("adb -s " + self.dut_ip + ":5555 shell date >> " + self.result_dir + "\\testtime.txt", expected_exit_code="")
                time.sleep(1)

                # System sleep stats
                self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /sys/power/soc_sleep/stats > " + self.result_dir + "\\system_sleep.txt", expected_exit_code="")
                time.sleep(1)

                # rpmh stats
                self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /sys/power/rpmh_stats/master_stats > " + self.result_dir + "\\rpmh_stats.txt", expected_exit_code="")
                time.sleep(1)   

                # interrupts
                self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /proc/interrupts > " + self.result_dir + "\\interrupts.txt", expected_exit_code="")
                time.sleep(1)

                # sensorservice
                self._host_call("adb -s " + self.dut_ip + ":5555 shell dumpsys sensorservice > " + self.result_dir + "\\sensorservice.txt", expected_exit_code="")
                time.sleep(1)

                # Dump battery stats
                self._host_call("adb -s " + self.dut_ip + ":5555 shell dumpsys batterystats > " + self.result_dir + "\\batterystats.txt", expected_exit_code="")
                time.sleep(1)

                # top activities
                self._host_call("adb -s " + self.dut_ip + ":5555 shell top -H -O TID -b -n 1 > " + self.result_dir + "\\top_activity_device.txt", expected_exit_code="")
                time.sleep(1)

                # RAM detail
                self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /proc/meminfo > " + self.result_dir + "\\ramdetail.txt", expected_exit_code="")
                time.sleep(1)
            
                if (self.build.lower() == "developer" or self.build.lower() == "dev"):
                    # lpm stats
                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/lpm_stats/stats > " + self.result_dir + "\\lpm_stats.txt", expected_exit_code="")
                    time.sleep(1)

                    # wakelocks
                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/wakeup_sources > " + self.result_dir + "\\wakelocks.txt", expected_exit_code="")
                    time.sleep(1)

                    # Mem info
                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/ipc_logging/adsp/log > " + self.result_dir + "\\adsp_glink.log", expected_exit_code="")
                    time.sleep(1)

                    # ipc_logging
                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/ipc_logging/modem/log > " + self.result_dir + "\\modem_glink.log", expected_exit_code="")
                    time.sleep(1)

                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/ipc_logging/cdsp/log > " + self.result_dir + "\\cdsp_glink.log", expected_exit_code="")
                    time.sleep(1)

                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/ipc_logging/glink_pkt/log > " + self.result_dir + "\\glink_pkt.log", expected_exit_code="")
                    time.sleep(1)

                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/ipc_logging/glink_probe/log > " + self.result_dir + "\\glink_probe.log", expected_exit_code="")
                    time.sleep(1)

                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/ipc_logging/qrtr_0/log > " + self.result_dir + "\\modem_qrtr.log", expected_exit_code="")
                    time.sleep(1)

                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/ipc_logging/qrtr_5/log > " + self.result_dir + "\\adsp_qrtr.log", expected_exit_code="")
                    time.sleep(1)

                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/ipc_logging/qrtr_9/log > " + self.result_dir + "\\sensor_qrtr.log", expected_exit_code="")
                    time.sleep(1)

                    self._host_call("adb -s " + self.dut_ip + ":5555 shell cat /d/ipc_logging/qrtr_10/log > " + self.result_dir + "\\NPU_qrtr.log", expected_exit_code="")
                    time.sleep(1)

                self._host_call("adb -s " + self.dut_ip + ":5555 shell /vendor/bin/qrtr-lookup > " + self.result_dir + "\\qrtr-lookup.txt", expected_exit_code="")
                time.sleep(1)

                # Kernal log
                self._host_call("adb -s " + self.dut_ip + ":5555 shell \"dmesg > /data/kernel_log.txt\"", expected_exit_code="")
                time.sleep(1)

                self._host_call("adb -s " + self.dut_ip + ":5555 pull /data/kernel_log.txt " + self.result_dir, expected_exit_code="")
                time.sleep(1)

                if self.bugreport == "1":
                    # bugreport
                    self._host_call("adb -s " + self.dut_ip + ":5555 bugreport " + self.result_dir + "\\bugreport.zip", expected_exit_code="")
                    time.sleep(1)

                # Collect additional logs
                if self.additional_logs == "1":
                    self._host_call(".\\Utilities\\Android\\AdditionalLogs\\_after_test_ver4.bat " + self.result_dir + "\\additional_logs", expected_exit_code="")
                    time.sleep(1)

        return

    def reportCallback(self):    
        # Parse battery_stats to get top processes
        if os.path.exists(self.scenario.result_dir + "\\batterystats.txt") and os.path.exists(os.path.join(self.scenario.result_dir, self.scenario.testname + "_metrics.csv")):
            
            if self.platformVersion == "11":
                pass
            else:
                logging.info("Appending additional metrics to *_metrics.csv")
                    
                # open file and read and close
                batterystats = open(self.scenario.result_dir + "\\batterystats.txt", "r")
                text = batterystats.read()
                batterystats.close()

                # Cut out important parts and create dictionary
                # Get top processes
                statDict = collections.OrderedDict()
                
                # number of processes to list
                n_processes=10
                
                # Divide up PowerUse by the lines in the Estimated Power use section
                try:
                    processes = re.search(r'Estimated power use \(mAh\):\n((.*\n){3,' + str(n_processes+1) + r'})', text).group(1).split('\n')
                    
                    # Get each line but drop the first one.
                    for x in range(n_processes):
                        try:
                            statDict['Top Process '+ str(x+1)] = re.search(r'\D([\d\D]*?)\d ', processes[x+1]).group(0).lstrip() + " mAh"
                        except:
                            print('Only ' + str(x) +' or fewer processes found. Alternatively, an invalid item broke the regex code.')
                            break
                except:
                    logging.info("Unable to get top processes")

                # Get stats that don't fit the pattern of ending with \n
                statList = [r'Time on battery', r'Time on battery screen off', r'Screen on']

                for statName in statList:
                    try:
                        statDict[statName] = re.search(statName + r':' + r'(.*?) \(', text).group(1).lstrip()
                    except:
                        logging.info("Could not find " + statName)

                # Get other stats
                statList = [r'Screen off discharge', r'Screen on discharge', r'Cellular kernel active time', r'Cellular Sleep time', r'Cellular Idle time', r'Cellular Rx time', r'Cellular Tx time', r'less than 0dBm', r'0dBm to 8dBm', r'8dBm to 15dBm', r'15dBm to 20dBm', r'above 20dBm', r'Wifi kernel active time', r'WiFi Scan time', r'WiFi Sleep time', r'WiFi Idle time', r'WiFi Rx time', r'WiFi Tx time', r'Wifi data received', r'Wifi data sent', r'Bluetooth total received', r'Bluetooth scan time', r'BLuetooth Idle time', r'Bluetooth Rx time', r'Bluetooth Tx time']

                for statName in statList:
                    try:
                        statDict[statName] = re.search(statName + r':' + r'(.*?)\n', text).group(1).lstrip()
                    except:
                        logging.info("Could not find " + statName)
                        
                # Find metrics.csv
                csv_name = os.path.join(self.scenario.result_dir, self.scenario.testname + "_metrics.csv")

                # Append to Metrics.csv
                with open(csv_name, 'a') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
                    for key in statDict:
                        # print pair
                        writer.writerow([key, statDict[key]])

        if self.appVersion == '1' and os.path.exists(self.scenario.result_dir + "\\bugreport.zip"):
            logging.debug("Unpacking Bugreport")
            os.makedirs(os.path.join(self.scenario.result_dir, "bugreport"), exist_ok=True)
            with zipfile.ZipFile(self.scenario.result_dir + "\\bugreport.zip", 'r') as zip_report:
                zip_report.extractall(os.path.join(self.scenario.result_dir, "bugreport"))
            
            # Get Bugreport Filename
            logging.debug("Looking for bugreport at" + os.path.join(self.scenario.result_dir, "bugreport"))
            try:
                filename = glob.glob( os.path.join(self.scenario.result_dir, "bugreport", "bugreport*.txt"))[0]
            except:
                logging.error("Unable to locate bug report!")
                return

            self._host_call("python .\\utilities\\Android\\GetAppVersions.py --input=" + filename + " --output=" + os.path.join(self.scenario.result_dir, "AppVersions.csv"))
            

        return




