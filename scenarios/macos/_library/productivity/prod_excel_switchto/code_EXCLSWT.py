import logging

def run(scenario):
    logging.debug('Executing code block: code_EXCLSWT.py - Switch to Microsoft Excel')
    
    # Use AppleScript to activate Microsoft Excel
    applescript = 'tell application "Microsoft Excel" to activate'
    scenario._call(["osascript", "-e", applescript])
