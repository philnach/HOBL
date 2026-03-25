import logging
import json
import requests
import qoi
import cv2 as cv
import utilities.call_rpc as rpc
from parameters import Params
import easyocr, io, contextlib

def run(scenario):
    duration = Params.get("teams", "duration")
    number_of_bots = int(Params.get("teams", "number_of_bots"))
    scenario.bots_send_video = Params.get("teams", 'bots_send_video')
    scenario.bots_send_audio = Params.get("teams", 'bots_send_audio')
    scenario.bots_share_screen = Params.get("teams", 'bots_share_screen')
    scenario.meeting_time = Params.get("teams", 'meeting_time')
    scenario.meeting_url = Params.get("teams", 'meeting_url')
    scenario.access_key = Params.get("teams", 'access_key')
    scenario.bots_test_server = Params.get("teams", 'bots_test_server')
    scenario.join_meeting_uri = Params.get("teams", 'join_meeting_uri')
    scenario.bots_force_subscribe_resolution = Params.get("teams", 'bots_force_subscribe_resolution')
    scenario.bot_index = int(Params.get("teams", 'bot_index'))
    
    scenario.bot_uris = Params.get("teams", "bot_uris")
    # decode the JSON string to a Python object
    if isinstance(scenario.bot_uris, str):
        scenario.bot_uris = json.loads(scenario.bot_uris)

    logging.debug("Bot URIs: " + str(scenario.bot_uris))
    
    scenario.bot_names = Params.get("teams", "bot_names")
    # decode the JSON string to a Python object
    if isinstance(scenario.bot_names, str):
        scenario.bot_names = json.loads(scenario.bot_names)
    
    logging.debug("Bot Names: " + str(scenario.bot_names))

    # Select bots server instance
    if scenario.bots_test_server == '0':
        scenario.server_url = "https://teamsbotorchestrator.azurewebsites.net/api"
    else:
        scenario.server_url = "https://teamsbotorchestrator-testing.azurewebsites.net/api"

    # Let play for specified duration
    logging.info("Calling for " + str(duration) + " seconds")

    # TODO: Enable with parameters
    # period = 600
    period = 45
    loops = int(float(duration) / period)
    logging.info("Checking Loops: " + str(loops))

    # Initialize OCR
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        # We need to suppress model download output
        scenario.reader = easyocr.Reader(['en'], gpu = False)

    # TODO: REMOVE THIS; FOR TESTING ONLY
    # number_of_bots += 1  # Add one for the DUT bot FOR TESTING ONLY

    for i in range(loops):
        bot_count = 0
        screen_data = rpc.plugin_screenshot(scenario.dut_ip, scenario.rpc_port, "InputInject", x=0, y=0, w=1, h=1)
        img = qoi.decode(screen_data)
        # Convert array format for opencv
        rgb_image = cv.cvtColor(img, cv.COLOR_RGB2BGR)

        result = scenario.reader.readtext(rgb_image, detail = 0)
        check_bot_list = []
        for t in result:
            if t.startswith("Bot") or t.startswith("Main"):
                bot_count += 1
                check_bot_list.append(t)
                logging.debug(t)

        bot_count = len(check_bot_list)

        # if bot_count == 0:
        #     # Call dropped or something else catastrophic, fail the test.
        #     logging.error(f"All bot have disappeared!")
        #     # scenario.hangup()
        #     # scenario.tearDown()
        #     raise Exception("Could not locate any bots in meeting, failing scenario.")
        #     return

        bots_needed = number_of_bots - bot_count
        logging.info(f"Current bot count: {bot_count}")
        if bots_needed > 0:
            logging.error(f"Unexpected number of bots in call: {bot_count}")
            logging.info(f"Bots needed: {bots_needed}")
            main_needed = False
            if "Main" not in check_bot_list:
                main_needed = True
            scenario.new_bot_list = []
            bot_screen = False
            if scenario.bots_send_video == "1":
                bot_video = True
            else:
                bot_video = False

            for x in range(bots_needed):
                if main_needed:
                    name = "Main"
                    bot_audio = True
                else:
                    logging.debug(f"Adding bot {scenario.bot_index}")
                    name = "Bot" + str(scenario.bot_index)
                    bot_audio = False
                    scenario.bot_index += 1
                bot_instance = {"BotDisplayName" : name, "StreamVideo" : bot_video, "StreamAudio" : bot_audio, "ScreenShare" : bot_screen}
                
                scenario.new_bot_list.append(bot_instance)
                bot_audio = False   # Set only first bot to send audio, prevents crowded mess
                bot_screen = False  # Set only first bot to screen share
            bot_data = json.dumps(scenario.new_bot_list, sort_keys=True)

            request_string = ""
            request_string += scenario.server_url # Add the URL to the request string

            # Debugging info
            logging.debug("Adding new bots to meeting")
            logging.debug("Server URL: " + scenario.server_url)
            logging.debug("Code: " + scenario.access_key)
            logging.debug("Meeting Duration: " + scenario.meeting_time)
            logging.debug("Join Meeting URL: " + scenario.meeting_url)
            logging.debug("bot_data: " + bot_data)
            
            # Add bots to meeting
            request_string += ("/AddBotsToMeeting" + "?code=" + scenario.access_key + "&meetingDurationInMinutes=" + scenario.meeting_time + "&joinMeetingUrl=" + scenario.meeting_url)

            # Send Request to the bot server. Retry as needed.
            attempts = 1
            while attempts < 5:
                r = requests.post(request_string, data=bot_data)
                logging.debug(r.status_code)
                logging.debug(r.text)

                # Good Status return
                if r.status_code == 200:
                    break

                elif r.status_code == 401:
                    logging.error("Error. 401 Unauthorized. You are not authorized to access the Teams Bots server. Please confirm you have entered your access key correctly.")
                    logging.error("Access key entered:" + scenario.access_key)
                    break

                logging.debug("Bad server response, re-sending request")
                scenario.time.sleep(90)
                attempts += 1

            # End if bad meeting request return
            if r.status_code != 200:
                logging.error("Unable to Start Meeting! Server Error")
                # scenario.hangup()
                # scenario.tearDown()
                # raise Exception("Unable to Start Meeting! Server Error")

            
            # Get new meeting info
            return_data = json.loads(r.content)
            logging.debug(type(return_data))

            # Log bot names and uris for later
            logging.debug("Bot URIs Returned Type: " + str(type(return_data))) 
            logging.debug("Bot URIs Type: " + str(type(scenario.bot_uris)))
            scenario.bot_uris.extend(return_data["botUris"])
            logging.debug(json.dumps({"botUris" : scenario.bot_uris}, sort_keys=True))

            try:
                scenario.bot_names.extend(return_data["botNames"])
                logging.debug(json.dumps({"botNames" : scenario.bot_names}, sort_keys=True))
            except:
                pass

            # Log bot names and uris for later 
            # json stringify the bot uris for storage
            bot_uris_json = json.dumps(scenario.bot_uris, sort_keys=True)
            Params.setParam("teams", "bot_uris", bot_uris_json)
            logging.info(bot_uris_json)

            try:
                # json stringify the bot names for storage
                bot_names_json = json.dumps(scenario.bot_names, sort_keys=True)
                Params.setParam("teams", "bot_names", bot_names_json)
                logging.info(bot_names_json)
            except:
                pass

            # Force the bots to subscribe to DUT video stream
            if scenario.bots_force_subscribe_resolution != "0":
                # Create force subscribe request string
                subscribe_request = scenario.server_url + "/ForceSubscription" + "?code=" + scenario.access_key + "&resolution=" + scenario.bots_force_subscribe_resolution
                bot_data = json.dumps({"botUris" : scenario.bot_uris, "botNames" : scenario.bot_names}, sort_keys=True)

                logging.debug(bot_data)

                r = requests.post(subscribe_request, data=bot_data) 
                logging.debug(r.status_code)
                logging.debug(r.text)

                # Check and try again on bad response
                attempts = 1
                while (r.status_code != 200 and attempts < 5):
                    logging.debug("Bad server response, re-sending request")
                    scenario.time.sleep(90)
                    attempts += 1
                    r = requests.post(subscribe_request, data=bot_data) 
                    logging.debug(r.status_code)
                    logging.debug(r.text)

                # End if bad meeting request return
                if r.status_code != 200:
                    logging.error("Unable to Force Video Subscribe! Server Side Error, See Logs for Details")
                    # scenario.hangup()
                    # scenario.tearDown()
                    # raise Exception("Unable to Force Video Subscribe! Server Side Error, See Logs for Details")

        scenario._sleep_by(period)