import logging

def run(scenario):
    logging.debug('Executing code block: code_WORDSWT.py - Switch to Microsoft Word')
    
    # Use AppleScript to activate Microsoft Word
    applescript = 'tell application "Microsoft Word" to activate'
    scenario._call(["osascript", "-e", applescript])
