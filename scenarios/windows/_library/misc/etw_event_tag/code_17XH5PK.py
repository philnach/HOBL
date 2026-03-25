import logging
import core.call_rpc as rpc
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_17XH5PK.py')
    event_tag = Params.get("etw_event_tag", "event_tag")
    rpc.plugin_call(scenario.dut_ip, scenario.rpc_port, "InputInject", "EventTag", event_tag)
