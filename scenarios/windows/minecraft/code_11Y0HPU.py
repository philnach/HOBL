import logging
import time
import os

def run(scenario):
    logging.debug('Executing code block: code_11Y0HPU.py')
    
    logging.info("Resetting map for next run.")
    userprofile = scenario._call(["cmd", "/C echo %USERPROFILE%"])
    # scenario._call(["cmd.exe", "/c del /Q /S /F " + userprofile + "\\AppData\\Roaming\\.minecraft\\saves\\*.*"], expected_exit_code="")
    time.sleep(1)
    scenario._upload(os.path.join("scenarios", "windows", "minecraft", "Demo_World"), userprofile + "\\AppData\\Roaming\\.minecraft\\saves\\")
    # scenario._call([scenario.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe", scenario.dut_ip + " " + scenario.app_port + " /forcequit"], blocking=False)
    time.sleep(3)
    logging.info("Map Reset Finished")
    
    logging.info("Attempting to change options for reducing frames from afk -> minimized")
    options_file = userprofile + "\\AppData\\Roaming\\.minecraft\\options.txt"
    scenario._call(["powershell.exe", "\"(Get-Content '" + options_file + "') -replace 'inactivityFpsLimit:\\\"afk\\\"', 'inactivityFpsLimit:\\\"minimized\\\"' | Set-Content '" + options_file + "'\""], expected_exit_code="")

    logging.info("Launching Game")
    scenario._call(["cmd.exe", "/C \"C:\\Program Files (x86)\\Minecraft Launcher\\MinecraftLauncher.exe\""], blocking=False)
