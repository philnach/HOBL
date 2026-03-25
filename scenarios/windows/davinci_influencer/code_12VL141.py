import logging
import os
import time

def run(scenario):
    logging.debug('Executing code block: code_12VL141.py')

    userprofile = scenario._call(["cmd", "/C echo %USERPROFILE%"])

    # Check if bench.mp4 is in temp folder and if so then delete it
    scenario._call(['cmd.exe', '/C del /Q /F "%TEMP%\\bench.mp4"'], expected_exit_code="")
                        
    scenario._upload('scenarios\\windows\\davinci_influencer\\davinci_resources', scenario.dut_exec_path, check_modified=True)
    
    #upload to %appdata%\\Blackmagic Design\\DaVinci Resolve\\Preferences\\Keyboard Shortcuts
    scenario._upload('scenarios\\windows\\davinci_influencer\\davinci_resources\\keyboard.preset.xml', userprofile + "\\AppData\\Roaming\\Blackmagic Design\\DaVinci Resolve\\Preferences", check_modified=False)

    scenario._upload('scenarios\\windows\\davinci_influencer\\davinci_resources\\shortcuts.fu', userprofile + "\\AppData\\Roaming\\Blackmagic Design\\DaVinci Resolve\\Support\\Fusion\\Profiles\\Default", check_modified=True)

