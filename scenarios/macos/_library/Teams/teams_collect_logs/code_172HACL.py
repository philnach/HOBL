import logging

def run(scenario):
    logging.debug('Executing code block: code_172HACL.py')
    # Remove Any Downloads of previous logs from download folder on mac
    # open msteams:
    # scenario._call(["rm", "-rf ~/Downloads/*MSTeams*"])
    scenario._call(["bash", "-c \"rm -rf ~/Downloads/*MSTeams*\""])
    scenario._call(["bash", "-c \"rm -rf ~/Downloads/*PROD*\""])
    scenario._call(["open", "msteams:"])