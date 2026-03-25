import logging
from core.parameters import Params
import os

def run(scenario):
    logging.debug('Executing code block: code_YRE1PY.py')
    game_location = Params.get('cyberpunk', 'game_location')
    cyberpunk_executable = os.path.join(game_location, "bin", "x64", "Cyberpunk2077.exe")

    # Check if Cyberpunk executable exists using cmd.exe
    check_result = scenario._call(["cmd.exe", f'/C if exist "{cyberpunk_executable}" (echo EXISTS) else (echo NOT_FOUND)'], expected_exit_code="")
    
    if "NOT_FOUND" in check_result:
        logging.error(f"Cyberpunk executable not found at: {cyberpunk_executable}")
        raise Exception(f"Cyberpunk2077.exe not found at {cyberpunk_executable}, confirm that game has been installed. ")

   
    scenario._call(["cmd.exe", f'/C "{cyberpunk_executable}"'], blocking=False)
    #    scenario._call(["cmd.exe", '/C "C:\\Program Files (x86)\\GOG Galaxy\\Games\\Cyberpunk 2077\\bin\\x64\\Cyberpunk2077.exe"'], blocking=False)
    #scenario._call(["cmd.exe", '/C "C:\\Program Files (x86)\\GOG Galaxy\\Games\\Cyberpunk 2077\\Launch Cyberpunk 2077.exe"'], blocking=False)