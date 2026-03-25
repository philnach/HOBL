import logging
import os
import csv

def run(scenario):
    logging.debug('Executing code block: code_195LUPA.py')
    call_health = scenario._call(["pbpaste", ""])
        
    sectionKey = ""
    callHealthSections = ["Network", "Audio", "Video", "Screen Sharing"]
    callHealthDictionary = {}
    for line in call_health.splitlines():
        if line in callHealthSections:
            sectionKey = line
        if sectionKey != "":
            if ":" in line:
                key, value = line.split(":")
                combinedKey = sectionKey + " " + key.strip()
                callHealthDictionary[combinedKey] = value.strip()

    #convert dictionary into csv format
    file_path_csv  = os.path.join(scenario.result_dir, "teams_call_health_info_rollup.csv")
    with open(file_path_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for key, value in callHealthDictionary.items():
            writer.writerow([key, value])