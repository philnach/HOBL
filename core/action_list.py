from builtins import str
from builtins import *
from builtins import object
from fileinput import filename
from appium import webdriver
import logging
import time
import json
import collections
import subprocess
import os
from cv2 import log
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from appium.webdriver.common.touch_action import TouchAction
from core.parameters import Params
from core.app_scenario import Scenario
import core.call_rpc as rpc

class ActionList(object):
    if (Params.get('global', 'platform') or "").lower() == "android":
        default_click_time = 100
        logging.debug("Setting Default Click to 100ms")
    else:
        default_click_time = 400
        logging.debug("Setting Default Click to 700ms")

    # There is an intrinsic delay of 30ms above what is specified on keystroke injection.
    typing_delay_adder = 30
    
    def __init__(self, file_path):
        # print "ActionList init"
        self.act_list = []
        self.file_path = file_path
        self.delay_accumulation = 0
        # Instantiate Scenario with bare argument to prevent tools from being initialized and hobl directories recreated.
        self.scenario = Scenario(bare=True)
        self.dut_exec_path = Params.getCalculated("dut_exec_path")

        if os.path.exists(os.path.join(self.scenario.result_dir, "SSCThreshold.json")) == False and self.scenario.training_mode == "1":
            with open(os.path.join(self.scenario.result_dir, "SSCThreshold.json"), 'w') as fp:
                sscThreshold = {"blackScreenSSC" : 0}
                json.dump(sscThreshold, fp)


    def clearDelayAccumulation(self):
        self.delay_accumulation = 0

    def getDelayAccumulation(self):
        return(self.delay_accumulation)

    def recordClickSS(self, driver, elem, name, delay = default_click_time, x_offset = 0, y_offset = 0, window_y = 0, window_x = 0, scale = 1.0, click_now = True, perf="0", primary=True):
        img = rpc.plugin_screenshot(self.dut_ip, self.rpc_port, "InputInject")
        with open("c:\\temp\\test.png", 'bw') as f:
            f.write(img)
        self.recordClick(driver, elem, name, delay, x_offset, y_offset, window_y, window_x, scale, click_now, perf, primary)

    def recordClick(self, driver, elem, name, delay = default_click_time, x_offset = 0, y_offset = 0, window_y = 0, window_x = 0, scale = 1.0, click_now = True, perf="0", primary=True):
        # logging.debug("Click set to: " + str(self.default_click_time))
        # logging.debug("Delay set to: " + str(delay))

        if (window_x == 0 and window_y == 0) and Params.get('global', 'absolute_coords') != "1":
            try:
                window_coords = driver.get_window_position()
                # print "Found window position"
            except:
                # print "Using default window coords"
                window_coords = {'y':0, 'x':0}
        else:
            window_coords = {'y':window_y, 'x':window_x}

        elem_coords = elem.location
        elem_size = elem.size

        if x_offset == 0:
            x = window_coords["x"] + elem_coords["x"] + (elem_size["width"] / 2)
        else:
            x = window_coords["x"] + elem_coords["x"] + x_offset

        if y_offset == 0:
            y = window_coords["y"] + elem_coords["y"] + (elem_size["height"] / 2)
        else:
            y = window_coords["y"] + elem_coords["y"] + y_offset

        x = x * scale
        y = y * scale

        print ("Coordinates for " + name + ":")
        print ("  Window X = ", window_coords["x"])
        print ("  Window Y = ", window_coords["y"])
        print ("  Element X = ", elem_coords["x"])
        print ("  Element Y = ", elem_coords["y"])
        print ("  Element Width = ", elem_size["width"])
        print ("  Element Height = ", elem_size["height"])
        print ("  Scale = ", scale)
        print ("  Final X = ", x)
        print ("  Final Y = ", y)

        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'tap'
        action[u'x'] = [str(int(x))]
        action[u'y'] = [str(int(y))]
        action[u'delay'] = [str(delay)]
        action[u'perf'] = perf
        action[u'primary'] = primary
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += delay

        if click_now:
            if int(delay) > 1000:
                TouchAction(driver).press(elem).wait(ms=int(delay)).release().perform()
            else:
                if x_offset == 0 and y_offset == 0:
                    if (primary):
                        # left-click
                        elem.click()
                    else:
                        # right-click
                        ActionChains(driver).context_click(elem).perform()
                else:
                    if (primary):
                        # left-click
                        ActionChains(driver).move_to_element_with_offset(elem, x_offset, y_offset).click().perform()
                    else:
                        # right-click
                        ActionChains(driver).move_to_element_with_offset(elem, x_offset, y_offset).context_click(elem).perform()


    def recordSlowTypingElem(self, elem, text, name, delay=350, type_now=True, layout="Default", perf="0", training_text=None):
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'type'
        action[u'keys'] = text
        action[u'delay'] = [str(delay)]
        action[u'layout'] = layout
        action[u'perf'] = perf
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += (len(text) * (float(delay) + self.typing_delay_adder))

        if type_now:
            if training_text != None:
                for c in training_text:
                    elem.send_keys(c)
                    time.sleep(0.150)
            else:
                for c in text:
                    elem.send_keys(c)
                    time.sleep(0.150)


    def recordTypingElem(self, elem, text, name, delay=350, type_now=True, layout="Default", perf="0", training_text=None):
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'type'
        action[u'keys'] = text.replace("\\\\", "\\")
        action[u'delay'] = [str(delay)]
        action[u'layout'] = layout
        action[u'perf'] = perf
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += (len(text) * (float(delay) + self.typing_delay_adder))

        if type_now:
            if training_text != None:
                training_text = training_text.replace(" ", "\ue00d")
                self.scenario._call([os.path.join(self.dut_exec_path, "InputInject", "InputInject.exe"), r"""[{'cmd':'type','delay':['""" + str(delay) + r"""'],'keys':'""" + training_text + r"""','layout':'""" + layout + r"""'}]"""])
                # elem.send_keys(training_text)
            else:
                text = text.replace(" ", "\ue00d")
                self.scenario._call([os.path.join(self.dut_exec_path, "InputInject", "InputInject.exe"), r"""[{'cmd':'type','delay':['""" + str(delay) + r"""'],'keys':'""" + text + r"""','layout':'""" + layout + r"""'}]"""])
                # elem.send_keys(text)


    def recordTyping(self, driver, text, name, delay=350, type_now = True, layout="Default", perf="0", training_text=None):
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'type'
        action[u'keys'] = text.replace("\\\\", "\\")
        action[u'delay'] = [str(delay)]
        action[u'layout'] = layout
        action[u'perf'] = perf
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += (len(text) * (float(delay) + self.typing_delay_adder))

        if type_now:
            if training_text != None:
                training_text = training_text.replace(" ", "\ue00d")
                self.scenario._call([os.path.join(self.dut_exec_path, "InputInject", "InputInject.exe"), r"""[{'cmd':'type','delay':['""" + str(delay) + r"""'],'keys':'""" + training_text + r"""','layout':'""" + layout + r"""'}]"""])
                # ActionChains(driver).send_keys(training_text).perform()
            else:
                text = text.replace(" ", "\ue00d")
                self.scenario._call([os.path.join(self.dut_exec_path, "InputInject", "InputInject.exe"), r"""[{'cmd':'type','delay':['""" + str(delay) + r"""'],'keys':'""" + text + r"""','layout':'""" + layout + r"""'}]"""])
                # ActionChains(driver).send_keys(text).perform()

    def recordFastTyping(self, driver, text, name, delay=0, type_now = True, layout="Default", training_text=None):
        action = collections.OrderedDict()
        action["tag"] = name
        action["cmd"] = "fasttype"
        action["keys"] = text
        action["delay"] = [str(delay)]
        action["layout"] = layout
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += (len(text) * (float(delay) + self.typing_delay_adder))

        if type_now:
            if training_text != None:
                ActionChains(driver).send_keys(training_text).perform()
            else:
                ActionChains(driver).send_keys(text).perform()


    def recordDateTimeElem(self, elem, remote_pattern, local_pattern, name, delay=100, layout="Default"):
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'datetime'
        action[u'keys'] = remote_pattern
        action[u'delay'] = [str(delay)]
        action[u'layout'] = layout
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += (19 * (float(delay) + self.typing_delay_adder))

        elem.send_keys(datetime.now().strftime(local_pattern))


    def recordSleep(self, delay, name="", sleep_now = True, perf="0"):
        if name == "":
            name = "Wait for {:.1f}s".format(float(delay))
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'sleep'
        action[u'delay'] = [str(int(delay*1000))]
        action[u'perf'] = perf
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += float(delay*1000)

        if sleep_now:
            time.sleep(delay)

    def recordSleepTo(self, delay, name="", sleep_now = False, perf="0"):
        if name == "":
            name = "Wait until {:.1f}s".format(float(delay))
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'sleepto'
        action[u'delay'] = [str(int(delay*1000))]
        action[u'perf'] = perf
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation = float(delay*1000) # delay is from beginning of recording, so accumulation is now equal to this.

        if sleep_now:
            raise NotImplementedError

    def recordSnapWindow(self, driver, name):
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'snapwindow'
        self.act_list.append(action)

        ActionChains(driver).key_down().perform()

    def recordEtwEvent(self, tag):
        action = collections.OrderedDict()
        action[u'tag'] = tag
        action[u'cmd'] = u'etw'
        action[u'perf'] = "1"
        self.act_list.append(action)
        
    def saveRecording(self, name):
        # print (json.dumps(self.act_list, indent=4, separators=(',', ': ')))
        with open(self.file_path, "w") as json_file:
            json_str = json.dumps(self.act_list, indent=4, separators=(',', ': '))
            json_file.write(json_str)

    def recordCursorMoveBy(self, driver, x, y, name="Move cursor by offset", delay=100, now=True):
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'moveby'
        action[u'x'] = [str(int(x))]
        action[u'y'] = [str(int(y))]
        action[u'delay'] = [str(int(delay))]
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += int(delay)

        if now:
            ActionChains(driver).move_by_offset(int(x), int(y)).perform()

    def recordCursorMoveTo(self, driver, x, y, name="Move cursor", delay=100, now=True):
        x = str(int(x))
        y = str(int(y))
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'moveto'
        action[u'x'] = [x]
        action[u'y'] = [y]
        action[u'delay'] = [str(int(delay))]
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += int(delay)

        if now:
            # ActionChains(driver).move_by_offset(int(x), int(y)).perform()
            dut_exec_path = Params.getCalculated("dut_exec_path")
            self.scenario._call([os.path.join(dut_exec_path, "InputInject", "InputInject.exe"), r"""[{'cmd':'moveto','delay':['100'],'x':[""" + x + r"""],'y':[""" + y + r"""]}]"""])


    def recordSwipePoint(self, start_x, start_y, end_x, end_y, name="Swipe", driver=None, delay=100, swipe_now=True):
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'swipe'
        action[u'x'] = [str(int(start_x)), str(int(end_x))]
        action[u'y'] = [str(int(start_y)), str(int(end_y))]
        action[u'delay'] = [str(int(delay))]
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += int(delay)

        if swipe_now:
            if Params.get('global', 'platform').lower() == "android":
                self._host_call("adb -s " + Params.get('global', 'dut_ip') + " shell input touchscreen swipe " + str(start_x) + " " + str(start_y) + " " + str(end_x) + " " + str(end_y) + " " + str(delay), expected_exit_code="")
                pass
            else:
                # TouchAction(driver).press(el, int(start_x), int(start_y)).waitAction(int(delay)).moveTo(int(end_x), int(end_y)).release().perform()
                driver.swipe(int(start_x), int(start_y), int(end_x), int(end_y), int(delay))


    def recordClickPoint(self, driver, name, delay = default_click_time, x=0, y=0, scale=1.0, click_now=True):
        # logging.debug("Click set to: " + str(self.default_click_time))
        # logging.debug("Delay set to: " + str(delay))
        x = x * scale
        y = y * scale

        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = "tap"
        action[u'x'] = [str(int(x))]
        action[u'y'] = [str(int(y))]
        action[u'delay'] = [str(delay)]
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += int(delay)

        if click_now:
            if Params.get('global', 'platform').lower() == "android":
                if delay < 300:
                    self._host_call("adb -s " + Params.get('global', 'dut_ip') + " shell input touchscreen " + "tap " + str(x) + " " + str(y), expected_exit_code="")
                else:
                    self._host_call("adb -s " + Params.get('global', 'dut_ip') + " shell input touchscreen swipe " + str(x) + " " + str(y) + " " + str(x) + " " + str(y) + " " + str(delay), expected_exit_code="")
            else:
                if delay < 300:
                    TouchAction(driver).tap(None, x, y, (float(delay)/1000)).perform()
                else:
                    TouchAction(driver).press(x=int(x), y=int(y)).wait(ms=delay).release().perform()
                # ActionChains(driver).move_to_element_with_offset(driver.find_element_by_xpath("//*"), x, y).click_and_hold().pause(float(delay)/1000).release().perform()


    def recordDateTime(self, driver, remote_pattern, local_pattern, name, delay=100, layout="Default"):
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'datetime'
        action[u'keys'] = remote_pattern
        action[u'delay'] = [str(delay)]
        action[u'layout'] = layout
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += (19 * (float(delay) + self.typing_delay_adder))

        ActionChains(driver).send_keys(datetime.now().strftime(local_pattern)).perform()


    def recordScroll(self, name, x=300, y=500, scroll_now=False, direction="down", clicks=6, perf="0"):
        movement = clicks * 120
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'scroll'
        action[u'x'] = [str(int(x))]
        action[u'y'] = [str(int(y))]
        action[u'direction'] = direction
        action[u'delay'] = [str(movement)]
        action[u'perf'] = perf
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)
        self.delay_accumulation += (float(clicks) * 10) # 10ms per click, measured empirically

        if(scroll_now):
            dut_exec_path = Params.getCalculated("dut_exec_path")
            self.scenario._call([os.path.join(dut_exec_path, "InputInject", "InputInject.exe"), r"""[{'cmd':'scroll','delay':[""" + str(movement) + r"""],'x':[""" + str(int(x)) + r"""],'y':[""" + str(int(y)) + r"""],'direction':'""" + direction + r"""'}]"""])


    def recordKeyEvent(self, keyEvent, name="Inject KeyEvent"):
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'keyevent'
        action[u'keys'] = [str(keyEvent)]
        self.act_list.append(action)

        if Params.get('global', 'platform').lower() == "android":
            self._host_call("adb -s " + Params.get('global', 'dut_ip') + " shell input " + "keyevent " + str(keyEvent), expected_exit_code="")
        else:
            raise NotImplementedError


    def recordAdb(self, arguments, name="Inject Adb Command", inject_now=True):
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'adb'
        action[u'arguments'] = [str(arguments)]
        self.act_list.append(action)

        if Params.get('global', 'platform').lower() == "android":
            if inject_now:
                self._host_call("adb -s " + Params.get('global', 'dut_ip') + " " + str(arguments), expected_exit_code="")
        else:
            raise Exception('PlatformNotSupportedError')
        
    
    def _host_call(self, command, cwd=".", expected_exit_code="0", blocking=True, shell=True):
        
        # Create a new process for the host call with pipes for stdout and stderr
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell = shell,
            cwd = cwd
        )

        # Temporary buffers to collect output and error streams for result
        data_out = bytearray()
        data_err = bytearray()

        # Continuously read output while the process is running, Non-blocking wait for process return 
        while p.poll() is None:
            try:
                # Collect stdout and stderr
                data_out += p.stdout.read()
                data_err += p.stderr.read()
            except:
                # Ignore read errors (e.g., if stream is temporarily unavailable)
                pass

        out = data_out
        err = data_err

        actual_exit_code = str(p.returncode)

        # Log standard output and error lines
        if len(out) > 0:
            for line in out.split(b'\n'):
                decoded_line = line.decode()
                if decoded_line:
                    logging.debug(decoded_line.rstrip())
        if len(err) > 0:
            for line in err.split(b'\n'):
                decoded_line = line.decode()
                if decoded_line:
                    logging.error(decoded_line.rstrip())

        # Validate the exit code if expected_exit_code is specified
        if(expected_exit_code !=""):
            if actual_exit_code != expected_exit_code :
                raise Exception('The call\'s exit code {0} doesn\'t match with expected exit code {1}'.format(actual_exit_code, expected_exit_code))
        
        # Decode result to byte output to string before returning
        out = out.decode()
        err = err.decode()
        
        return out

    def recordScreenshot(self, name, fileName, threshold = 0, perf="1", blackScreenSSC = "0", region = None):
        action = collections.OrderedDict()
        action[u'tag'] = name
        action[u'cmd'] = u'screenshot'
        action[u'fileName'] = fileName
        action[u'perf'] = perf
        action[u'accum_delay'] = str(self.delay_accumulation)
        self.act_list.append(action)

        if threshold != 0 or blackScreenSSC == "1":
            fileDir = os.path.join(self.scenario.result_dir, "SSCThreshold.json")
            #open a json file that contains threshold values
            with open(fileDir) as json_file:
                sscThreshold = json.load(json_file)

            if threshold != 0:
                #adds the threshold value that it got passed from a scenario
                imageName = fileName.split("\\")[-1]
                sscThreshold[imageName] = threshold
                if region != None:
                    sscThreshold[imageName + "_crop"] = region

            if blackScreenSSC == "1":
                sscThreshold["blackScreenSSC"] = blackScreenSSC

            with open(fileDir, "w") as outfile:
                json.dump(sscThreshold, outfile)

        fileName = fileName.replace("\\", "\\\\")
        json_str = "[{'cmd':'screenshot','fileName':" + "'" + fileName + "'}]"
        logging.debug("Taking screenshot of: " + fileName)

        # Getting a screenshot of the screen in training mode
        dut_exec_path = Params.getCalculated("dut_exec_path")
        self.scenario._call([os.path.join(dut_exec_path, "InputInject", "InputInject.exe"),json_str])
        
            
            
            

