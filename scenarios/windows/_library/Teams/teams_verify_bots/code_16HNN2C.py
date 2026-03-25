import logging
import json
import requests
import qoi
import cv2 as cv
import core.call_rpc as rpc
from core.parameters import Params
import easyocr, io, contextlib
import time

def run(scenario):
    number_of_bots = int(Params.get("teams", "number_of_bots"))
    
    # Initialize OCR
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        # We need to suppress model download output
        scenario.reader = easyocr.Reader(['en'], gpu = False)

    screen_data = rpc.plugin_screenshot(scenario.dut_ip, scenario.rpc_port, "InputInject", x=0, y=0, w=1, h=1)
    img = qoi.decode(screen_data)
    # Convert array format for opencv
    rgb_image = cv.cvtColor(img, cv.COLOR_RGB2BGR)

    result = scenario.reader.readtext(rgb_image, detail = 0)
    bot_list = []
    for t in result:
        if t.startswith("Bot") or t.startswith("Main"):
            logging.debug(t)
            if t not in bot_list:
                bot_list.append(t)

    bot_count = len(bot_list)
    logging.info(f"Number of bots detected: {bot_count}")

    # Catch time up
    scenario._sleep_to_now()

    if bot_count != number_of_bots:
        logging.error(f"Expected {number_of_bots} bots, but found {bot_count} bots.")
        raise Exception("Could Not Locate All Bots In Meeting, Failing Scenario")