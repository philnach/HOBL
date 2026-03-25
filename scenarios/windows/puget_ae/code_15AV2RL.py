import logging

def run(scenario):
    logging.debug('Executing code block: code_15AV2RL.py')


    scenario._call(["cmd.exe", """/C netsh.exe advfirewall firewall add rule name="Adobe After Effects" program="C:\\program files\\adobe\\adobe after effects 2025\\support files\\cephtmlengine\\cephtmlengine.exe" dir=in action=allow enable=yes localport=any protocol=TCP profile=public,private,domain"""])
    scenario._call(["cmd.exe", """/C netsh.exe advfirewall firewall add rule name="Adobe After Effects" program="C:\\program files\\adobe\\adobe after effects 2025\\support files\\cephtmlengine\\cephtmlengine.exe" dir=in action=allow enable=yes localport=any protocol=UDP profile=public,private,domain"""])
    
    # # Check if After Effects benchmark is installed
    # after_effect_benchmark = "%localappdata%\\com.puget.benchmark\\benchmarks\\aftereffects-benchmark-1.0.0-hobl.json"
    # check_ae_benchmark = scenario._call(["cmd.exe", '/c if exist "' + after_effect_benchmark + '" echo After Effects benchmark exists'], expected_exit_code="")

    # if check_ae_benchmark == "":
    #     logging.info("Didn't find after effects benchmark. Moving from host")
    #     userprofile = scenario._call(["cmd", "/C echo %USERPROFILE%"])
    #     target = userprofile + "\\AppData\\Local\\com.puget.benchmark\\benchmarks"
    #     # scenario._upload("scenarios\\pugetbench_resources\\aftereffects-benchmark-1.0.0-hobl.json", target)
    #     scenario._upload("scenarios\\windows\\puget_ae\\aftereffects-benchmark-1.0.0-hobl.json", target)

