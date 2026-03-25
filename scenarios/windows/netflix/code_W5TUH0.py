import logging
import core.call_rpc as rpc

def run(scenario):
    logging.debug('Executing code block: code_W5TUH0.py')
    rpc.plugin_call(scenario.dut_ip, scenario.rpc_port, "InputInject", "MoveTo", 0, 510, scenario.current_screen)