import logging

def run(scenario):
    logging.debug('Executing code block: code_1A76NEH.py')
    try:
        logging.debug("Killing " + "ms-teams.exe")
        if scenario.platform.lower() == "w365":
            scenario._run_with_inputinject("cmd.exe /c tasklist /nh /fo csv /fi \"IMAGENAME eq 'ms-teams.exe'\"")
        else:
            scenario._kill("ms-teams.exe", force = True)
    except:
        pass