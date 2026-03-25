import logging
import os
from core.parameters import Params

def run(scenario):
    logging.debug('Executing code block: code_11VATC7.py')
    benchmark_option = Params.get('mac_blender', 'benchmark_option')
    output = scenario._call(["/Users/Shared/hobl_bin/benchmark-launcher-cli", " benchmark --blender-version 4.4.0 --device-type " + benchmark_option + " --json monster junkshop classroom"])

    file_path = os.path.join(scenario.result_dir, "blender_result.txt")

    # Write the output to a text file
    with open(file_path, "w") as file:
        file.write(output)
