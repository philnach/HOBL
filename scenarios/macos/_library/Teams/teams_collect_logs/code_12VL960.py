import logging
import os, re, csv
from core.parameters import Params

def run(scenario):
    parser_location = Params.get("teams", "parser_location")
    if os.path.exists(parser_location + "\\log2text.exe"):
       # You can do any post processing of data here.
        logging.info("Teams Decoder " + scenario.result_dir + "\\MSTeamsLogs\\sc-tfw\\mediastack\\")
        # Directory where your files are located
        directory = scenario.result_dir + "\\MSTeamsLogs\\sc-tfw\\mediastack\\"
        # List all files in the directory
        if os.path.exists(directory):
            files = os.listdir(directory)
            # Filter the files to find the one starting with "Media.msrtc-0"
            target_file = next((f for f in files if f.startswith("Media.msrtc-0")), None)

            if target_file:
                logging.info("Processing log")
                # Now we use log2text with the logmap decoder and save as a csv:
                scenario._host_call(parser_location + "\\log2text.exe -i " + directory + target_file + " -l " + parser_location + "\\full.logmap -o " + scenario.result_dir + "\\teamsdecode.txt", expected_exit_code="", output=False)
                decoded_text = scenario.result_dir + "\\teamsdecode.txt"

                encoding = {"hw":0, "sw":0}
                width_sum = 0
                height_sum = 0
                fps_sum = 0
                count = 0

                pattern = re.compile(r'h264 layout\s*\((hw|sw)\).*?\((\d+),(\d+),([\d.]+)\)')

                with open(decoded_text, errors="ignore") as f:
                    for line in f:
                        match = pattern.search(line.lower())
                        if match:
                            hw_or_sw, width, height, fps = match.groups()
                            width_sum += int(width)
                            height_sum += int(height)
                            fps_sum += float(fps)
                            count += 1
                            encoding[hw_or_sw] += 1
                if count > 0:
                    avg_width = width_sum / count
                    avg_height = height_sum / count
                    avg_fps = fps_sum / count
                    hw_percent = int(encoding["hw"] / count * 100)
                    sw_percent = 100 - hw_percent
                    output = {
                    "Teams HW Encoding (%)": hw_percent,
                    "Teams SW Encoding (%)": sw_percent,
                    "Teams Avg Horizontal Resolution": avg_width,
                    "Teams Avg Vertical Resolution": avg_height,
                    "Teams Avg FPS": avg_fps
                    }
                    with open(scenario.result_dir + "\\teamsdecode.csv", "w", newline='') as f:
                        writer = csv.writer(f)
                        for key, value in output.items():
                            writer.writerow([key, value])
                else:
                    logging.warning("Did not find anything to parse")


            else:
                logging.info("File not found")
                return
    else:
        logging.warning("could not find location of teams log parser")


    