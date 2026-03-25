import logging

def run(scenario):
    logging.debug('Switching to Microsoft Word (MacOS)')
    
    try:
        # Use AppleScript to bring Word to foreground
        applescript = '''
        tell application "Microsoft Word"
            activate
        end tell
        '''
        scenario._call(["osascript", "-e", applescript])
    except Exception as e:
        logging.error(f"Failed to switch to Word: {e}")
