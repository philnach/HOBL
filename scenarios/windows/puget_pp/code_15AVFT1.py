import logging

def run(scenario):
    logging.debug('Executing code block: code_15AVFT1.py')

    scenario._call(["cmd.exe", """/C netsh.exe advfirewall firewall add rule name="Adobe Premiere Pro" program="C:\\program files\\adobe\\adobe premiere pro 2025\\cephtmlengine\\cephtmlengine.exe" dir=in action=allow enable=yes localport=any protocol=TCP profile=public,private,domain"""])
    scenario._call(["cmd.exe", """/C netsh.exe advfirewall firewall add rule name="Adobe Premiere Pro" program="C:\\program files\\adobe\\adobe premiere pro 2025\\cephtmlengine\\cephtmlengine.exe" dir=in action=allow enable=yes localport=any protocol=UDP profile=public,private,domain"""])