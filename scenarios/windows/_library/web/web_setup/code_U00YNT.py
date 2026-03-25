import logging

def run(scenario):
    logging.debug('Executing code block: code_U00YNT.py')
    # Initiate Web Page Record or Replay
    logging.info("Web Replay Delay Disabled")
    scenario._web_replay_start(disable_delay=True)
    scenario._sleep_to_now()
