import logging

def run(scenario):
    logging.debug('Executing code block: code_12MYEMV.py')
    # scenario._call(["mv", "-f ~/Downloads/*MSTeams* " + scenario.dut_data_path + "/MSTeamsLogs"])
    scenario._call(["bash", "-c \"mv -f ~/Downloads/*MSTeams* '" + scenario.dut_data_path + "/MSTeamsLogs'\""])