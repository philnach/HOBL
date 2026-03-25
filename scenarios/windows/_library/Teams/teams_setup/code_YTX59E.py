import logging
import requests
import json
from core.parameters import Params

def run(scenario):
    bots_force_subscribe_resolution = Params.get("teams", "bots_force_subscribe_resolution")
    server_url = Params.get("teams", "server_url")
    access_key = Params.get("teams", "access_key")
    
    bot_uris = Params.get("teams", "bot_uris")
    # decode the JSON string to a Python object
    if isinstance(bot_uris, str):
        bot_uris = json.loads(bot_uris)
    
    bot_names = Params.get("teams", "bot_names")
    # decode the JSON string to a Python object
    if isinstance(bot_names, str):
        bot_names = json.loads(bot_names)



    # Build the request URL
    subscribe_request = server_url + "/ForceSubscription" + "?code=" + access_key + "&resolution=" + bots_force_subscribe_resolution    
    bot_data = json.dumps({"botUris" : bot_uris, "botNames" : bot_names}, sort_keys=True)

    logging.debug(bot_data)

    r = requests.post(subscribe_request, data=bot_data) 
    logging.debug(r.status_code)
    logging.debug(r.text)

    # Check and try again on bad response
    attempts = 1
    while (r.status_code != 200 and attempts < 10):
        logging.debug("Bad server response, re-sending request")
        scenario.time.sleep(30)
        attempts += 1
        r = requests.post(subscribe_request, data=bot_data) 
        logging.debug(r.status_code)
        logging.debug(r.text)

    # End if bad meeting request return
    if r.status_code != 200:
        logging.error("Unable to Force Video Subscribe! Server Side Error, See Logs for Details")
        # self.hangup()
        # self.tearDown()
        # raise Exception("Unable to Force Video Subscribe! Server Side Error, See Logs for Details")