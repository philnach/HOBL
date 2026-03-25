"""
// Convert the Apple powermetric output to our power_data.csv for rollup into a study report
"""

import sys
import argparse
import glob
import os
import fnmatch
import pandas as pd

arg_parser = argparse.ArgumentParser(description = "Generate Run Report.")
arg_parser.add_argument('-recurse', '-r', help='Search directories recursively.', action="store_true")
arg_parser.add_argument('path', nargs='?', default='.\\*.txt', help='Path to txt output file(s)')
args = arg_parser.parse_args()


# Get directory to process
abspath = os.path.abspath(args.path)
basepath = os.path.basename(abspath) 
if os.path.isdir(abspath):
    dirpath = abspath
    basepath = "*.txt"
else:
    dirpath = os.path.dirname(abspath)

# Set the test name to the leaf directory name of the path
testname = dirpath.split("\\")[-1]

# These need to match the metrics in the source file
metric_list = ['Package Power', 'Clusters Total Power', 'GPU Power', 'DRAM Power']

print("Processing dir: " + dirpath + ", file spec: " + basepath)
# Process DAQ files
for root, dirs, files in os.walk(dirpath):
    for file in files:
        if glob.fnmatch.fnmatch(file, basepath):
            inputfile = root + os.sep + file          

            # Read in powermetrics text file and store in metrics data frame
            # Example block we are parsing.  Using "Package Power" as a marker for the end of the sample period, indicating when to add the row to the table.
            """
            ANE Power: 0 mW
            DRAM Power: 4 mW
            Clusters Total Power: 15 mW
            GPU Power: 1 mW
            Package Power: 21 mW
            """

            new_row = {}
            df = pd.DataFrame(columns = metric_list)
            with open(inputfile) as f:
                for line in f:
                    for metric in metric_list:
                        if metric in line:
                            first_part = metric + ": "
                            last_part = " mW"
                            value = line.replace(first_part, "").replace(last_part, "")
                            new_row[metric] = int(value.strip())
                    if "Package Power" in line:
                        # End of sample, add new_row to data frame
                        df = df.append(new_row, ignore_index=True)
                        new_row = {}

            # print(df)
            print("\nAverages:")
            dfA = df.mean()
            print(dfA)
            summary_file = root + os.sep + "power_data.csv"
            print("\nWriting to: " + summary_file)
            dfA.to_csv(summary_file, sep=',', header=False, float_format='%0.1f')

    if not args.recurse:
        break

