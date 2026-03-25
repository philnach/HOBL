import logging
import os
from core.parameters import Params
def run(scenario):
    logging.debug('Executing code block: code_1556VR9.py')
    benchmark_version = Params.get('mac_puget_dr', 'benchmark_version')
    # license_key = Params.get('mac_puget_dr', 'puget_license')
    loops = Params.get('mac_puget_dr', 'loops')

    iteration = 0
    benchmark_exe = "/Applications/PugetBench for Creators.app/Contents/MacOS/PugetBench for Creators"
    # scenario._call(["cmd.exe", "/C " + benchmark_exe + " --license " + license_key])

    arguments = f'--app resolve --benchmark_version {benchmark_version} --preset standard --timeout 600 --copy_log '
    output_file = scenario.dut_data_path + f'/davinci_output.log'


    while iteration < int(loops):
        # output_file = os.path.join(scenario.dut_data_path, f'davinci_output_{iteration}.log')
        benchmark_output = scenario._call([benchmark_exe, arguments + output_file])
        if "Benchmark passed:" in benchmark_output:
            raise Exception(benchmark_output)
        iteration += 1