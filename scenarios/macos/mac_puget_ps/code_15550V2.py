import logging
import os

def run(scenario):
    logging.debug('Executing code block: code_15550V2.py')
    
    try:
        # scenario._kill('"Adobe Photoshop 2025"')
        scenario._call(["killall", '"Adobe Photoshop 2025"'], expected_exit_code="", timeout=10)
    except:
        pass

    log_path = os.path.join(scenario.result_dir, 'photoshop_output.log')

    if not os.path.exists(log_path):
        raise Exception(f"Log file not found: {log_path}. Photoshop possibly errored out.")

    score = 0
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("Overall Score"):
                parts = line.strip().split(",")
                score = parts[2]
                break
        else:
            raise Exception('Overall Score Not Found. Photoshop possibly errored out.')
        
    if score != 0:
        # write score to csv file
        output_csv_path = os.path.join(scenario.result_dir, 'benchmark_result.csv')
        with open(output_csv_path, "w") as f:
            f.write(f"Overall Score,{score}")
