import logging

def run(scenario):
    logging.debug('Executing code block: code_11RY088.py')

    scenario._call(["cmd.exe", '/C "C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"'], blocking=False)