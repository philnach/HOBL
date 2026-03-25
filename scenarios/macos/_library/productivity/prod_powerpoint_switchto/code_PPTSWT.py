import logging

def run(scenario):
    logging.debug('Executing code block: code_PPTSWT.py - Switch to Microsoft PowerPoint')
    
    # Use AppleScript to activate Microsoft PowerPoint
    applescript = 'tell application "Microsoft PowerPoint" to activate'
    scenario._call(["osascript", "-e", applescript])
