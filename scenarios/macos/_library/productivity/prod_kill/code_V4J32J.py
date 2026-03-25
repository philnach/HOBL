import logging

def run(scenario):
    logging.debug('Executing code block: code_V4J32J.py (MacOS)')
    
    try:
        apps = ["Microsoft Excel", "Microsoft PowerPoint", "Microsoft Word", "Microsoft OneNote"]
        logging.debug(f"Killing {', '.join(apps)}")
        scenario._kill(apps)
    except:
        pass
