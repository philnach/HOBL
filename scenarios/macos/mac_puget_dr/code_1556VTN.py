import logging
import os

def run(scenario):
    logging.debug('Executing code block: code_1556VTN.py')

    try:
        scenario._call(["killall", '"DaVinci Resolve"'], expected_exit_code="", timeout=10)
    except:
        pass

    csv_path = os.path.join(scenario.result_dir, 'davinci_output.log')

    if not os.path.exists(csv_path):
        raise Exception(f"Log file not found: {csv_path}. DaVinci Resolve possibly errored out.")

    score = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("Overall Score"):
                parts = line.strip().split(",")
                score = parts[2]
                break
        else:
            raise Exception('Overall Score Not Found. DaVinci Resolve possibly errored out.')
        
    if score != 0:
        # write score to csv file
        output_csv_path = os.path.join(scenario.result_dir, 'benchmark_result.csv')
        with open(output_csv_path, "w") as f:
            f.write(f"Overall Score,{score}")

