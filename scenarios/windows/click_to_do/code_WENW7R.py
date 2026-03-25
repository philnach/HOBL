import logging
import os

def run(scenario):
    logging.debug('Executing code block: code_WENW7R.py')
    try:
        scenario._kill("Photos.exe")
    except:
        pass
    try:
        scenario._kill("msedge.exe")
    except:
        pass
        
    preferences_file = os.path.join("$env:userprofile", "AppData", "local", "Microsoft", "Edge", "User Data", "Default", "Preferences")
    scenario._call(["powershell.exe", '((Get-Content -path """' + preferences_file + '""" -Raw) -replace """Crashed""","""Normal""") | Set-Content -Path """' + preferences_file + '"""'], expected_exit_code="", fail_on_exception=False)

