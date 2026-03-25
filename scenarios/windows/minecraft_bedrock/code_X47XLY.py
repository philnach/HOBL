import logging
import time
import os

def run(scenario):
    logging.debug('Executing code block: code_X47XLY.py')
    try:
        logging.debug("Killing minecraft")
        scenario._kill("Minecraft.Windows.exe")
    except:
        pass
        
    logging.info("Resetting map for next run.")
    userprofile = scenario._call(["cmd", "/C echo %USERPROFILE%"])
    # scenario._call(["cmd.exe", "/c del /Q /S /F " + userprofile + "\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\Minecraftworlds\\*.*"], expected_exit_code="")
    scenario._call(["cmd.exe", '/c del /Q /S /F "' + userprofile + '\\AppData\\Roaming\\Minecraft Bedrock\\Users\\Shared\\games\\com.mojang\\minecraftWorlds"'], expected_exit_code="")
    time.sleep(1)
    # scenario._upload(os.path.join("scenarios", "minecraft_resources", "TestMap"), userprofile + "\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\Minecraftworlds\\")
    scenario._upload(os.path.join("scenarios", "windows", "minecraft_bedrock", "minecraftWorlds"), userprofile + "\\AppData\\Roaming\\Minecraft Bedrock\\Users\\Shared\\games\\com.mojang")
    scenario._call([scenario.dut_exec_path + "\\WindowsApplicationDriver\\WinAppDriver.exe", scenario.dut_ip + " " + scenario.app_port + " /forcequit"], blocking=False)
    time.sleep(3)
    logging.info("Map Reset Finished")
    logging.info("Launching Minecraft")


    scenario._call(["cmd.exe", '/C start minecraft:'])