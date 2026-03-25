"""
//--------------------------------------------------------------
//
// parse_socwatch
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
import collections

arg_parser = argparse.ArgumentParser(description = "Summarizes socwatch results into a list of key-vals.")
arg_parser.add_argument('-input', '-i', help='Path to socwatch summary .csv file.')
arg_parser.add_argument('-output', '-o', help='Path of output file .csv file.')
args = arg_parser.parse_args()

section_list = [
    "Package C-State Summary: Residency (Percentage and Time)",
    "Core C-State Summary: Residency (Percentage and Time)"
]

print("Reading: ",args.input)

metrics = collections.OrderedDict()
socwatch_list = []
row = 0

# Function to skip to the specified string in the source .csv
def skip_to(search_str, start_row):
    for r in range(start_row, len(socwatch_list)):
        if search_str in socwatch_list[r]:
            return r
    return 0

# Functino to grab key value pairs and put in metrics dictionary
def grab(prefix, start_row, num_rows = 1, key_col = 0, val_col = 1, until_blank = True):
    r = start_row
    line = socwatch_list[r]
    while len(line) != 0:
        metrics[prefix + line[key_col].strip()] = line[val_col].strip()
        r += 1
        line = socwatch_list[r]
    return r

# Read in source csv file to socwatch_list list
with open(args.input, encoding="utf8") as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    socwatch_list = list(reader)

# Parse
row = skip_to("PCH SLP-S0 State Summary: Residency (Percentage and Time)", row)
if row != 0:
    row = grab(prefix = "", start_row = row + 3)

row = skip_to("Package C-State Summary: Residency (Percentage and Time)", row)
if row != 0:
    row = grab(prefix = "Package C-State ", start_row = row + 3)

row = skip_to("Core C-State Summary: Residency (Percentage and Time)", row)
if row != 0:
    row = grab(prefix = "Core C-State ", start_row = row + 3)

row = skip_to("Core P-State/Frequency Summary: Residency (Percentage and Time)", row)
if row != 0:
    cores = []
    weighted_freq_list = []
    row += 1
    col = 0
    # Get number of cores and column number for each
    for header in socwatch_list[row]:
        if "Residency (%)" in header:
            cores.append(col)
            weighted_freq_list.append([])
        col += 1
    row += 2
    line = socwatch_list[row]
    # Produce list of frequency * residency for each core
    while len(line) != 0:
        core = 0
        for col in cores:
            weighted_freq = float(line[1]) * float(line[col])/100
            weighted_freq_list[core].append(weighted_freq)
            core += 1
        row += 1
        line = socwatch_list[row]
    # Sum each list
    for core in range(len(cores)):
        key = "Core " + str(core) + " Average Freq (MHz)"
        val = sum(weighted_freq_list[core])
        metrics[key] = val

row = skip_to("Graphics C-State  Summary: Residency (Percentage and Time)", row)
if row != 0:
    row = grab(prefix = "Graphics C-State ", start_row = row + 3)

row = skip_to("PCIe LPM Summary - Sampled: Residency (Percentage)", row)
if row != 0:
    row += 1
    states = socwatch_list[row][1:]
    row += 2
    line = socwatch_list[row]
    while len(line) != 0:
        key = line[0].strip()
        for known_device in ['Wireless', 'CardReader', 'NVM', 'Bridge', 'GPU', 'NVIDIA']:
            if known_device in key:
                key = known_device
                break
        col = 1
        for state in states:
            val = line[col].strip()
            metrics[key + " " + state.strip()] = val
            col += 1
        row += 1
        line = socwatch_list[row]

row = skip_to("Panel Self-Refresh Summary - Sampled: Residency (Percentage)", row)
if row != 0:
    row = grab(prefix = "", start_row = row + 3)

# Write to output csv
print("Writing: ", args.output)
with open(args.output, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    for key in metrics:
        print(key, metrics[key])
        writer.writerow([key, metrics[key]])

