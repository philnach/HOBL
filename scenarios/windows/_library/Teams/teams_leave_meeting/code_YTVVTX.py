import logging
import json
import requests
import time
from core.parameters import Params

def run(scenario):

    bot_uris = Params.get("teams", "bot_uris")
    # decode the JSON string to a Python object
    if isinstance(bot_uris, str):
        bot_uris = json.loads(bot_uris)
    
    server_url = Params.get("teams", "server_url")
    access_key = Params.get("teams", "access_key")

    # Log final parameters
    logging.info("FINAL PARAMETERS:")
    logging.info("==========================================")
    logging.info("server_url: " + server_url)
    logging.info("access_key: " + access_key)
    logging.info("bot_uris: " + json.dumps(bot_uris, sort_keys=True))
    logging.info("==========================================")


    # Build Stop request string
    bot_data = json.dumps({"botUris" : bot_uris}, sort_keys=True)
    stop_request = server_url + "/StopMeeting" + "?code=" + access_key

    r = requests.post(stop_request, data=bot_data) 
    logging.info(r.status_code)

    # Check and try again on bad response
    attempts = 1
    while (r.status_code != 200 and attempts < 5):
        logging.info("Bad server response, re-sending request")
        time.sleep(90)
        attempts += 1
        r = requests.post(stop_request, data=bot_data) 
        logging.info(r.status_code)
        logging.info(r.text)

    # Advance time counter to current time
    scenario._sleep_to_now()

    # Check that good meeting was returned
    if r.status_code != 200:
        logging.error("Unable to Stop Meeting! Server Side Error")
        raise Exception("Unable to Stop Meeting! Server Side Error")