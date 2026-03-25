"""
//--------------------------------------------------------------
//
// Generate HOBL Trend
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
import xlwings as xw
import csv
import collections
import time


def process(path, active_target, hobl_target):
    # Get directory to work with
    dirpath = os.path.abspath(path)
    basepath = "*study_report.xlsx"

    # Initialize data structures
    study_table = collections.OrderedDict()
    header = ["Study", "ABL Active On", "ABL Active On Target", "HOBL", "HOBL Target", "ABL Telemetry", "Standby Telemetry", "Timestamp"]

    # Read in any existing trend_data CSV file
    csv_name = dirpath + os.sep + "trend_data.csv"
    if os.path.exists(csv_name):
        with open(csv_name) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            first_row = True
            for r in reader:
                if first_row:
                    first_row = False
                    continue
                study_name = r[0]
                study_table[study_name] = collections.OrderedDict()
                study_table[study_name]["ABL Active On"] = r[1]
                study_table[study_name]["ABL Active On Target"] = r[2]
                study_table[study_name]["HOBL"] = r[3]
                study_table[study_name]["HOBL Target"] = r[4]
                study_table[study_name]["ABL Telemetry"] = r[5]
                study_table[study_name]["Standby Telemetry"] = r[6]
                study_table[study_name]["Timestamp"] = r[7]

        # Print table
        print (u'\t'.join(header))
        for study_name in study_table:
            line = study_name + '\t'
            for key in header[1:]:
                line += study_table[study_name][key] + '\t'
            print (line)

    # Process study_report files
    excel = xw.App(visible = False)
    print (u"Processing dir: " + dirpath + u", file spec: " + basepath)
    for root, dirs, files in os.walk(dirpath):
        if os.path.exists(root + os.sep + "ignore_trend.txt"):
            print (u"Ignoring " + root)
            continue
        for file in files:
            if glob.fnmatch.fnmatch(file, basepath):
                if file[0] == "~":
                    continue
                inputfile = root + os.sep + file
                print (u"Reading Run Report file:  " + inputfile)
                mtime = os.path.getmtime(inputfile)
                time_str = time.strftime(" %Y-%m-%d %H:%M:%S", time.localtime(mtime))
                print (time_str)
                time_secs = time.mktime(time.strptime(time_str, " %Y-%m-%d %H:%M:%S"))
                study_name = inputfile.split('\\')[-2]

                # Compare file modified time with timestamp in CSV file.  Only process if newer.
                if study_name in study_table:
                    csv_time_str = study_table[study_name]["Timestamp"]
                    csv_secs = time.mktime(time.strptime(csv_time_str, " %Y-%m-%d %H:%M:%S"))
                    if (csv_secs + 1) > mtime:
                        print (u"Study: " + study_name + u" Not modified.")
                        continue

                # Read in Run Report file
                print ("OPENING WB " + inputfile)
                wb = excel.books.open(inputfile)
                sheet = wb.sheets["HOBL"]
                # Get study report version
                study_report_version = sheet.range('A1').value
                if study_report_version == None or study_report_version == "":
                    # Search for keys in column B, values in F
                    for y in range(20,40):
                        if sheet.range('B' + str(y)).value == "Screen On Battery Life Prediction":
                            break
                    print (u"Found Active On at row " + str(y))
                    active_val = sheet.range('F'+ str(y)).value
                    hobl_val = sheet.range('F'+ str(y+2)).value
                    lvp_val = sheet.range('F'+ str(y+3)).value
                elif int(study_report_version) == 2:
                    # Search for keys in column C, values in G
                    for y in range(20,40):
                        if sheet.range('C' + str(y)).value == "Screen On Battery Life Prediction (h)":
                            break
                    print (u"Found Active On at row " + str(y))
                    active_val = sheet.range('G'+ str(y)).value
                    hobl_val = sheet.range('G'+ str(y+4)).value
                    lvp_val = sheet.range('G'+ str(y+5)).value
                elif int(study_report_version) == 3:
                    # Search for keys in column C, values in G
                    for y in range(20,40):
                        if sheet.range('C' + str(y)).value == "Screen On Battery Life Prediction (h)":
                            break
                    print (u"Found Active On at row " + str(y))
                    active_val = sheet.range('G'+ str(y)).value
                    hobl_val = sheet.range('G'+ str(y+5)).value
                    lvp_val = sheet.range('G'+ str(y+6)).value
                elif int(study_report_version) == 4:
                    # Search for keys in column C, values in G
                    for y in range(20,40):
                        if sheet.range('C' + str(y)).value == "Screen On Battery Life Prediction (h)":
                            break
                    print (u"Found Active On at row " + str(y))
                    active_val = sheet.range('G'+ str(y)).value
                    hobl_val = sheet.range('G'+ str(y+4)).value
                    lvp_val = sheet.range('G'+ str(y+7)).value
                elif int(study_report_version) == 5:
                    # Search for keys in column C, values in G
                    for y in range(20,40):
                        if sheet.range('C' + str(y)).value == "HOBL Active On (h)":
                            break
                    print (u"Found Active On at row " + str(y))
                    active_val = sheet.range('G'+ str(y)).value
                    hobl_val = sheet.range('G'+ str(y+5)).value
                elif int(study_report_version) >= 6:
                    # Search for keys in column C, values in G
                    for y in range(20,40):
                        if sheet.range('C' + str(y)).value == "HOBL Active On (h)":
                            break
                    print (u"Found Active On at row " + str(y))
                    active_val = sheet.range('G'+ str(y+7)).value
                    hobl_val = sheet.range('G'+ str(y+5)).value

                print ("CLOSING WB")
                wb.close()
                print(hobl_val)
                study_table[study_name] = collections.OrderedDict()
                try:
                    study_table[study_name]["ABL Active On"] = "%.1f" % float(active_val)
                except:
                    study_table[study_name]["ABL Active On"] = "%.1f" % 0
                study_table[study_name]["ABL Active On Target"] = "%.1f" % float(active_target)
                # try:
                #     study_table[study_name]["Telemetry"] = "%.1f" % float(telemetry_val)
                # except:
                #     study_table[study_name]["Telemetry"] = "%.1f" % 0
                # study_table[study_name]["Telemetry Target"] = "%.1f" % float(telemetry_target)
                try:
                    study_table[study_name]["HOBL"] = "%.1f" % float(hobl_val)
                except:
                    study_table[study_name]["HOBL"] = "%.1f" % 0
                study_table[study_name]["HOBL Target"] = "%.1f" % float(hobl_target)
                # study_table[study_name]["ABL Telemetry"] = "%.1f" % float(0)
                # study_table[study_name]["Standby Telemetry"] = "%.1f" % float(0)
                study_table[study_name]["ABL Telemetry"] = ""
                study_table[study_name]["Standby Telemetry"] = ""
                study_table[study_name]["Timestamp"] = time_str
                print (u"Study: " + study_name + u" Updated.")

    print ("QUITTING EXCEL")
    excel.quit()

    # Output .csv file of subsystem power data
    print (u"Writing CSV file: " + csv_name)
    with open(csv_name, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        writer.writerow(header)
        for study_name in study_table:
            row = [study_name]
            for key in header[1:]:
                row.append(study_table[study_name][key])
            writer.writerow(row)

    # Print table
    print (u'\t'.join(header))
    for study_name in study_table:
        line = study_name + '\t'
        for key in header[1:]:
            line += study_table[study_name][key] + '\t'
        print (line)


if __name__ == "__main__":
    # Parse command line arguments
    arg_parser = argparse.ArgumentParser(description = "Generate Run Report.")
    arg_parser.add_argument('path', nargs='?', default='.', help='Path to studies.')
    arg_parser.add_argument('-active_target', '-a', nargs='?', default='0', help='Active Target in hours.')
    # arg_parser.add_argument('-telemetry_target', '-tt', nargs='?', default='0', help='HOBL Telemetry Target in hours.')
    # arg_parser.add_argument('-telemetry_value', '-tv', nargs='?', default='0', help='HOBL Telemetry Value in hours.')
    arg_parser.add_argument('-hobl_target', '-o', nargs='?', default='0', help='HOBL Target in hours.')
    args = arg_parser.parse_args()

    process(args.path, args.active_target, args.hobl_target)
