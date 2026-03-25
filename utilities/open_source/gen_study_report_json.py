"""
//--------------------------------------------------------------
//
// gen_study_report_json_2024
//
// Copyright(c) Microsoft Corporation
// All rights reserved.
//
// MIT License
//
// Permission is hereby granted, free of charge, to any person obtaining
// a copy of this software and associated documentation files(the ""Software""),
// to deal in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies
// of the Software, and to permit persons to whom the Software is furnished to do so,
// subject to the following conditions :
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
// FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS
// OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
// OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//
//--------------------------------------------------------------
"""

import sys
import argparse
import glob
import os
import csv
import pandas as pd
import numpy as np
import json
from datetime import datetime


# CURRENT REPORT VERSION
STUDY_REPORT_VERSION = 3.0
RUN_REPORT_VERSION = 2.0

def main():
    arg_parser = argparse.ArgumentParser(description = "Generate Study Report.")
    arg_parser.add_argument('-goals', '-g', help='Path to scenario goals .csv file for populating goals in table.')
    arg_parser.add_argument('-name', '-n', default='', help='Name of the report file.')
    arg_parser.add_argument('-adders', '-d', help='Path to scenario adders .csv file for populating touch and keyboard adders in table.')
    arg_parser.add_argument('-study_type', '-s', default='', help='Type of study (copied to config sheet)')
    arg_parser.add_argument('-device_name', '-dn', help='Name of the device (copied to config sheet)')
    arg_parser.add_argument('-comments', '-c', default="", help='Comments about this study (copied to config sheet)')
    arg_parser.add_argument('-active_target', '-a', nargs='?', type= float, default=0, help='Active Target in hours.')
    arg_parser.add_argument('-hobl_target', '-o', nargs='?', type= float, default=0, help='HOBL Target in hours.')
    arg_parser.add_argument('-battery_capacity', '-b', nargs='?' , type= float, default=0, help='Typical battery capacity.')
    arg_parser.add_argument('-battery_reserve', '-r', nargs='?', type= float, default=0, help='Fraction of battery capacity not able to be consumed.')
    arg_parser.add_argument('-battery_derating', '-bd', nargs='?', type= float, default=0, help='Fraction of battery capacity not able to be consumed.')
    arg_parser.add_argument('-os_shutdown_reserve', '-sr', nargs='?', type= float, default=0.03, help='The shutdown reserve')
    arg_parser.add_argument('-hibernate_budget_target', '-hbt', nargs='?', type= float, default=0, help='Hibernate Budget Target in percent.')
    arg_parser.add_argument('-dashboard_url', help='Hobl Dashboard URL')
    arg_parser.add_argument('-template', nargs='?', default='', help='Template of study report json. Placed in hobl\\docs folder')
    arg_parser.add_argument('-enable_phase_report', '-pr', nargs='?', default='1', help='Enable or disable phase reports.') 
    arg_parser.add_argument('-current_run', '-cr', nargs='?', default='', help='Current scenario run.')
    arg_parser.add_argument('path', nargs='?', default='.\\*metrics.json', help='Path to metrics.csv files')
    args = arg_parser.parse_args()

    # The directory path and the basepath which is used to figure out what file to parse out. 
    # Get directory to process
    abspath = os.path.abspath(args.path)
    basepath = os.path.basename(abspath)
    if os.path.isdir(abspath):
        dirpath = abspath
        basepath = "*metrics.json"
    hobl_url = args.dashboard_url.split('/')[0] + "//" + args.dashboard_url.split('/')[2] + '/'

    study_name = dirpath.split('\\')[-1]
    print (u"Study name: " + study_name)
    print (u"Data directory: " + dirpath)
    # if args.device_name != "" and args.device_name != None :
    #     study_name = study_name + "_" + args.device_name
    # if args.name == "study_report.json":
    #     args.name = study_name + "_study_report.json"
    # args.name = args.name.replace(".xlsx", ".json")
    if args.name == '':
        print("Study report name cannot be left blank", file=sys.stderr)
        sys.exit(1)
    json_file_path = dirpath + os.sep + args.name
    latest_timestamp = -1
    report_file = json_file_path
    print (u"Study Report file: " + json_file_path)


    '''
    ==================================
    Section: HOBL Score Variables
    ==================================
    Setting up all the variables/data structure needed to calculate the hobl score
    '''
    usage_time_percent = {}
    scenario_category = {}
    scenario_information = {}
    template_data = {}

    # Get the directory of where gen_study_report_json
    # script_path = os.path.abspath(__file__)
    # script_dir = os.path.dirname(script_path)
    # weight_path = os.path.join(script_dir, "..", "docs", args.template)
    weight_path = args.template
    if args.template != '' and os.path.exists(weight_path):
        with open(weight_path, mode='r') as file:
            print("Loading template data from " + weight_path)
            template_data = json.load(file)

        screen_on_categories = template_data["weights"]["system on"]["activity"]["screen on"]["categories"]
        screen_off_categories = template_data["weights"]["system on"]["activity"]["screen off"]["categories"]


        
        # initializing all the required data structures.
        for category in screen_on_categories.keys():
            usage_time_percent[category] = (template_data["weights"]["system on"]["activity"]["screen on"]["percent"]/100) * (screen_on_categories[category]["percent"]/100)
            scenario_category[category] = list(screen_on_categories[category]["scenarios"].keys())
            for key, value in screen_on_categories[category]["scenarios"].items():
                scenario_information[key] = {"weight": value/100, "total_power": 0}
        for category in screen_off_categories.keys():
            usage_time_percent[category] = (template_data["weights"]["system on"]["activity"]["screen off"]["percent"]/100) * (screen_off_categories[category]["percent"]/100)
            scenario_category[category] = list(screen_off_categories[category]["scenarios"].keys())
            for key, value in screen_off_categories[category]["scenarios"].items():
                scenario_information[key] = {"weight": value/100, "total_power": 0}



    '''
    ==================================
    Section: Score Card Variables
    ==================================
    Setting up all the variables/data structure needed to calculate the score card
    '''
    scorecard_builder = {}
    scorecard_final = []
    #goals_dir = "C:\\Users\\Yoon Kim\\Documents\\study_report_json\\Denali_OLED_goals.csv"
    goals_targets = {}
    all_runs = []
    goals_sub_system_names = []

    # Variable/data structures for the final result for study report
    study_report = {}
    
    if args.goals != None and os.path.exists(args.goals):
        # Parsing the goals file to get all the subsystems needed for the score card as well as the target power value. 
        with open(args.goals, mode='r') as file:
            csv_reader = csv.reader(file)
            data = list(csv_reader)

        transposed_data = list(zip(*data))
        goals_sub_system_names = transposed_data.pop(0)
        if "Record Time (Min)" not in goals_sub_system_names:
            goals_sub_system_names = goals_sub_system_names + ("Record Time (Min)",)
            for x in range(0, len(transposed_data)):
                transposed_data[x] = transposed_data[x] + ('',)

        for row in transposed_data:
            scenario_name = row[0]
            #scenario_name = scenario_name.replace("teams", "teams2")
            goals_targets[scenario_name] = {}
            for x in range(1, len(row)):
                if row[x] == "":
                    goals_targets[scenario_name][goals_sub_system_names[x]] = 0
                else:
                    goals_targets[scenario_name][goals_sub_system_names[x]] = row[x]

    # Making scorecard_builder which is used to collect all the data from the runs 
    # and using that to average out power value for each subsystem
    if template_data: # Check if we have weighting/scorecard template provided
        # print("Creating scorecard builder from template data")
        for header, scenario in template_data["score card headers"].items():
            scorecard_builder[scenario] = {"scenario": header, "runs": 0, "sub_system": {}}
            for sub_sys in range(1, len(goals_sub_system_names)):
                scorecard_builder[scenario]["sub_system"][goals_sub_system_names[sub_sys]] = 0

    '''
    ==================================
    Section: Result Parsing
    ==================================
    Walking through the result directory to read and parse the json file to populate the information for the scorecard.
    The score card information will be used to calcaulate the hobl score.
    '''
    # walk through the directories of runs and read the metrics.json files to add to runs and build the scorecard information. 
    for root, dirs, files in os.walk(dirpath):
        parent = os.path.abspath(root + os.sep + "..")
        parent_parent = os.path.abspath(parent + os.sep + "..")
        # if not os.path.exists(root + os.sep + ".PASS") or os.path.exists(root + os.sep + ".FAIL"):
        #     continue
        if report_file == json_file_path:
            for file in files:
                # for file in (root, file):
                path = os.path.join(root,file)
                # Check if a excel study report is in the directories were parsing to link the json study report to an excel. Otherwise, just use the json file path as the report name. 
                if "study_report.xlsx" in path:
                    report_file = path
        if args.current_run == '' or args.current_run not in root:
            if not os.path.exists(root + os.sep + ".PASS") and not os.path.exists(parent + os.sep + ".PASS") and not os.path.exists(parent_parent + os.sep + ".PASS"):
                #and not os.path.exists(root + os.sep + ".RUNNING")
                continue

        if args.enable_phase_report is None:
            args.enable_phase_report = "1"

        if os.path.exists(parent_parent + os.sep + ".PASS") and (args.enable_phase_report).lower() == "0":
            continue 

        for file in files:
            # for file in (root, file):
            path = os.path.join(root,file)
            if glob.fnmatch.fnmatch(file, basepath):
                if "config_check" in os.path.dirname(path) or "training" in os.path.dirname(path) or "misc" in os.path.dirname(path) or "prep" in os.path.dirname(path) or "fail" in os.path.dirname(path):
                    continue
                if "phase_report" not in path:
                    # Open the json file
                    inputfile = root + os.sep + file
                    with open(inputfile, 'r') as file:
                        print (u"Reading: " + inputfile)
                        data = json.load(file)
                    if "Run Report Version" not in data or data["Run Report Version"] < RUN_REPORT_VERSION:
                        print(inputfile + " does not have latest report version. Not generating JSON study report.")
                        print("Closing gracefully")
                        sys.exit(0)
                    # Save file path of metrics to use for phase_report:
                    phase_report_scenario = inputfile
                    
                    # Collect the run type and scenario name. Run type is needed to check if it's power and scenario name is needed to key to scorecard builder
                    run_type = data["Run Type"]
                    scenario = data["Test Name"]
                    try:
                        timestamp = datetime.strptime(data["Config"]["Run Start Time"], "%Y-%m-%d %H:%M:%S")
                    except:
                        try:
                            timestamp = datetime.strptime(data["Config"]["Capture Time"], "%Y-%m-%d %H:%M:%S")
                        except:
                            timestamp = -1
                    # Update the study type if not provided
                    if args.study_type == '':
                        if "Study Type" in data["Config"]:
                            args.study_type = data["Config"]["Study Type"]
                    if timestamp != -1 and (latest_timestamp == -1 or timestamp > latest_timestamp):
                        latest_timestamp = timestamp
                    if run_type.lower() == "power" and scenario in scorecard_builder.keys():
                        scorecard_builder[scenario]["runs"] += 1
                        # Add DAQ rails
                        for subsystem, power in data["DAQ"]["Summary"].items():
                            # print("Adding " + str(power) + " to " + subsystem + " for " + scenario)
                            if subsystem in scorecard_builder[scenario]["sub_system"].keys():
                                if power != '' and not isinstance(power, str):
                                    # print("Adding2 " + str(power) + " to " + subsystem + " for " + scenario)
                                    scorecard_builder[scenario]["sub_system"][subsystem] += power
                            # Case where goals is not provided so we will use the sub_systems from. Initializing subsystem
                            elif len(goals_sub_system_names) == 0 and ("(w)" in subsystem.lower() or "(min)" in subsystem.lower()):
                                # print("Initializing " + subsystem + " for " + scenario)
                                scorecard_builder[scenario]["sub_system"][subsystem] = power
                        # Add PM rails if no DAQ rails
                        if len(data["DAQ"]["Summary"]) == 0 and "PM" in data and "Summary" in data["PM"]:
                            for subsystem, power in data["PM"]["Summary"].items():
                                if subsystem in scorecard_builder[scenario]["sub_system"].keys():
                                    if power != '' and not isinstance(power, str):
                                        scorecard_builder[scenario]["sub_system"][subsystem] += power
                                # Case where goals is not provided so we will use the sub_systems from. Initializing subsystem
                                elif len(goals_sub_system_names) == 0 and ("(w)" in subsystem.lower() or "(min)" in subsystem.lower()):
                                    scorecard_builder[scenario]["sub_system"][subsystem] = power
                    all_runs.append(data)
                
                # Parse the phase report information if seen. 
                elif "phase_report" in path: 
                    with open(phase_report_scenario) as main_scenario:
                        run_info = json.load(main_scenario)

                    inputfile = root + os.sep + file
                    with open(inputfile, 'r') as file:
                        data = json.load(file)
                    # The check is it to make sure that the phase_report and the main scenario it's under is the same name. As well as checking that it's a power run. 
                    #if run_info["Run Type"].lower() == "power":
                        scenario = data["Test Name"]
                        phase_name = scenario.split(".")[-1]
                        if scenario in scorecard_builder.keys() and run_info["Run Type"].lower() == "power":
                            scorecard_builder[scenario]["runs"] += 1
                            for subsystem, power in data.items():
                                if subsystem in scorecard_builder[scenario]["sub_system"].keys():
                                    if power != '' and not isinstance(power, str):
                                        scorecard_builder[scenario]["sub_system"][subsystem] += power
                                # Case where goals is not provided so we will use the sub_systems from. Initializing subsystem
                                elif len(goals_sub_system_names) == 0 and ("(w)" in subsystem.lower() or "(min)" in subsystem.lower()):
                                    scorecard_builder[scenario]["sub_system"][subsystem] = power
                        
                        # if "L1" not in all_runs[-1]["DAQ"]["Phase"].keys():
                        #     all_runs[-1]["DAQ"]["Phase"]["L1"] = {}
                        all_runs[-1]["DAQ"]["Phase"][phase_name] = data
                    
                
    '''
    ==================================
    Section: Score Card
    ==================================
    Creating the final score card which will be used for the study report.
    '''
    # Create the final score card result that will be used for study report
    scenario_index = 0
    if template_data: # If blank template then no score card and hobl score
        for scenario_name in scorecard_builder.keys():
            subsys_index = 0
            runs = scorecard_builder[scenario_name]["runs"]
            for key, value in scorecard_builder[scenario_name]["sub_system"].items():
                target_value, delta = None, None
                if runs != 0:
                    #measured_value = float("{:.3f}".format(value/runs))
                    try:
                        measured_value = float(value/runs)
                    except:
                        measured_value = None
                    if scenario_name in goals_targets.keys(): 
                        target_value = float(goals_targets[scenario_name][key])
                        try:
                            delta = "%.2f" % (measured_value / target_value)
                            delta = float(delta)
                        except:
                            pass

                    scorecard_template = {
                        "Scenario Name": scenario_name, 
                        "Scenario": scorecard_builder[scenario_name]["scenario"], 
                        "Sub-system": key, 
                        "Target": target_value, 
                        "Measured": measured_value, 
                        "Delta": delta,
                        "Scenario Index": scenario_index,
                        "Subsystem Index": subsys_index
                        }
                else:
                    scorecard_template = {
                        "Scenario Name": scenario_name, 
                        "Scenario": scorecard_builder[scenario_name]["scenario"], 
                        "Sub-system": key, 
                        "Target": target_value, 
                        "Measured": value, 
                        "Delta": delta,
                        "Scenario Index": scenario_index,
                        "Subsystem Index": subsys_index
                        }
                scorecard_final.append(scorecard_template)
                subsys_index += 1
            scenario_index += 2


    '''
    ==================================
    Section: HOBL Score
    ==================================
    Calculating the hobl score
    '''
    hobl_summary = {}
    adders_values = {}
    if template_data:
        if args.adders != None and os.path.exists(args.adders):
            # Parse through the adders csv file and collect the adder power datas
            with open(args.adders, mode='r') as file:
                csv_reader = csv.reader(file)
                data = list(csv_reader)

            transposed_data = list(zip(*data))
            transposed_data.pop(0)
            for row in transposed_data:
                scenario_name = row[0].lower()
                adders_values[scenario_name] = 0
                for x in range(1, len(row)):
                    if row[x] == '':
                        adders_values[scenario_name] += 0
                    else:
                        adders_values[scenario_name] += float(row[x])
            if "abl_active" in adders_values:
                adders_values["abl_active"] = 0

        # Parsing through the scorecard builder to populate the hobl score scenario informatio. Also adding the adders to the total power to get the HOBL Power.
        for scenario_name in scorecard_builder.keys():
            runs = scorecard_builder[scenario_name]["runs"]
            try:
                total_power = scorecard_builder[scenario_name]["sub_system"]["Total Power (W)"]
            except:
                try:
                    total_power = scorecard_builder[scenario_name]["sub_system"]["PM Total Power (W)"]
                except:
                    total_power = 0
            if scenario_name in scenario_information.keys():
                if runs != 0:
                    hobl_pwr = total_power/runs
                    if scenario_name in adders_values.keys(): 
                        hobl_pwr += adders_values[scenario_name]
                    scenario_information[scenario_name]["total_power"] = hobl_pwr
                else:
                    hobl_pwr = 0 
                    if scenario_name in adders_values.keys(): 
                        hobl_pwr += adders_values[scenario_name]
                    scenario_information[scenario_name]["total_power"] = hobl_pwr

        # Get the total power for each category before we calculate the weighted power. 
        category_power = {}
        for key, value in scenario_category.items():
            if key not in category_power.keys():
                category_power[key] = 0.0
            for scenario_name in value:
                category_power[key] += scenario_information[scenario_name]["total_power"] * scenario_information[scenario_name]["weight"]

        # Calculate the screen on/off category weighted power. Screen off - Modern standby | Screen on - ABL Active, Communications, Entertainment
        weighted_category_pwr = {}
        total_screen_on_pwr = 0
        total_weighted_pwr = 0 # Total screen off + screen on power. 
        for key, value in usage_time_percent.items():
            total_category_weighted_pwr = value * category_power[key]
            # Check if it's a screen on category to compare the total screen on vs screen off to get correct weighted power for screen off(modern standby)
            if key in screen_on_categories:
                total_screen_on_pwr += total_category_weighted_pwr
            if key == "modern standby":
                total_category_weighted_pwr = total_category_weighted_pwr if total_category_weighted_pwr < (.05674 * total_screen_on_pwr) else (.05674 * total_screen_on_pwr)
                weighted_category_pwr[key] = total_category_weighted_pwr
            else:
                weighted_category_pwr[key] = total_category_weighted_pwr
            
            # Calculating the total screen off + screen on weighted power. 
            total_weighted_pwr += total_category_weighted_pwr



        # Calculating the HOBL summary
        battery_derating = args.battery_capacity * args.battery_derating
        battery_reserve = args.battery_capacity * args.battery_reserve
        shutdown_reserve = (args.battery_capacity - battery_derating) * args.os_shutdown_reserve
        total_battery_capacity = args.battery_capacity - battery_derating - battery_reserve - shutdown_reserve
        modern_standby_budget = divide_check(weighted_category_pwr["modern standby"], total_weighted_pwr) 
        if modern_standby_budget is not None:
            modern_standby_budget *= total_battery_capacity
        hibernate_budget = 0.00 # Not sure where this number is coming from. Current excel study report is linked to blank cell
        modern_standby_budget_check =  modern_standby_budget if modern_standby_budget is not None else 0 # Handling case if modern_standby_budget is None
        active_battery_capacity = total_battery_capacity - modern_standby_budget_check - hibernate_budget

        screen_on_burnrate = divide_check(total_screen_on_pwr, (template_data["weights"]["system on"]["activity"]["screen on"]["percent"]/100))
        screen_off_burnrate = category_power["modern standby"]

        hobl_active_on = divide_check(active_battery_capacity, screen_on_burnrate)
        hobl_screen_off = divide_check(modern_standby_budget, screen_off_burnrate)
        hibernate_budget_target = args.hibernate_budget_target * 100
        hibernate_timeout = divide_check((args.battery_capacity - battery_derating) * args.hibernate_budget_target, screen_off_burnrate)
        hobl_lab_prediction = divide_check(total_battery_capacity, total_weighted_pwr)
        
        # Any of these values can be None so making sure they are not a None value before subtracting. 
        hobl_lab_prediction_check =  hobl_lab_prediction if hobl_lab_prediction is not None else 0
        hobl_active_on_check =  hobl_active_on if hobl_active_on is not None else 0
        hobl_screen_off_check = hobl_screen_off if hobl_screen_off is not None else 0
        hobl_screen_off_hibernate = hobl_lab_prediction_check - hobl_active_on_check - hobl_screen_off_check

        abl_active_pwr = 0
        if "abl_active" not in scenario_information:
            try:
                runs = scorecard_builder["abl_active"]["runs"]
                total_power = scorecard_builder["abl_active"]["sub_system"]["Total Power (W)"]
                abl_active_pwr = total_power/runs
            except:
                try:
                    runs = scorecard_builder["abl_active"]["runs"]
                    total_power = scorecard_builder["abl_active"]["sub_system"]["PM Total Power (W)"]
                    abl_active_pwr = total_power/runs
                except:
                    pass
        else:
            abl_active_pwr = scenario_information["abl_active"]["total_power"]
        
        abl_lab_daq_measurement = divide_check(total_battery_capacity, ((abl_active_pwr + scenario_information["abl_standby"]["total_power"])/2))
        abl_active_on_lab_daq_measurement = divide_check(total_battery_capacity, abl_active_pwr)
        abl_lab_performance = None
        lvp_value = divide_check(total_battery_capacity, scenario_information["lvp"]["total_power"])

        hobl_active_target = args.hobl_target * template_data["weights"]["system on"]["percent"] / 100

        hobl_summary = {
            "HOBL Active" : hobl_active_on,
            "HOBL Active Target" :hobl_active_target,
            "HOBL" : hobl_lab_prediction,
            "HOBL Target": args.hobl_target,
            "ABL" : abl_lab_daq_measurement,
            "ABL Active" : abl_active_on_lab_daq_measurement,
            "ABL Active Target" : args.active_target,
            "ABL Perf" : abl_lab_performance,
            "Standby" : hibernate_timeout,
            "Battery Typical Charge Capacity (Wh)" : args.battery_capacity,
            "Derating (Wh)" : battery_derating,
            "Reserve (Wh)" : battery_reserve,
            "OS shutdown Reserve (Wh)" : shutdown_reserve,
            "Total Available Battery Capacity (Wh)" : total_battery_capacity,
            "Modern Standby Budget (Wh)" : modern_standby_budget,
            "Hibernate Budget (Wh)" : hibernate_budget, 
            "Available Active Battery Capacity (Wh)" : active_battery_capacity,
            "Screen On burnrate (W)" : screen_on_burnrate,
            "Screen Off burnrate (W)" : screen_off_burnrate,
            "HOBL Active On (h)" : hobl_active_on,
            "HOBL Screen Off (h)" : hobl_screen_off,
            "HOBL Screen Off Hibernate (h)" : hobl_screen_off_hibernate,
            "Hibernate Budget Target (%)" : hibernate_budget_target,
            "Hibernate Timeout (h)" : hibernate_timeout,
            "HOBL Lab Prediction (h)" : hobl_lab_prediction,
            "ABL Lab DAQ Measurement (h)" : abl_lab_daq_measurement,
            "ABL Active On Lab DAQ Measurement (h)" : abl_active_on_lab_daq_measurement,
            "ABL Lab Performance (MOS)" : None,
            "LVP (h)" : lvp_value
        }

    # Going through hobl_summary and checking for None values and removing them from entry
    # List all keys with None values
    keys_with_none = [k for k, v in hobl_summary.items() if v is None]

    # Remove entries with None values
    for key in keys_with_none:
        del hobl_summary[key]
    
    for key, val in hobl_summary.items():
        hobl_summary[key] = round(val, 2)

    '''
    ==================================
    Section: Create Final Study Report
    ==================================
    Combining all the results (Study information, hobl summary, runs) together for the final study report
    '''
    scorecard_final = sorted(scorecard_final, key=lambda x: (x["Subsystem Index"], x["Scenario Index"])) # The code to sort the scorecard. 
    if latest_timestamp == -1:
        latest_timestamp =  datetime.now()
    if len(all_runs) == 0:
        print("No runs found. Exiting gracefully.")
        sys.exit(0)

    study_info = {
        "Study Report Version": STUDY_REPORT_VERSION,
        "Study Path" : dirpath,
        "Study URL" : hobl_url + "result/Results?path=" + dirpath,
        "Study Type" : args.study_type,
        "Study Notes" : args.comments,
        "Study Timestamp": latest_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    }

    study_report = {
        "Report" : report_file,
        "Study" : study_info,
        "HOBL" : hobl_summary,
        "Scorecard" : scorecard_final,
        "Runs" : all_runs
    }
    with open(json_file_path, 'w') as json_file:
        json.dump(study_report, json_file, indent=4)

def divide_check(numerator, denominator):
    try:
        val = numerator/denominator
        return val
    except:
        return None

if __name__ == "__main__":
    main()