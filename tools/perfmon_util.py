"""
//--------------------------------------------------------------
//
// HOBL
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

import os
import re
import pandas as pd
from core.parameters import Params
from core.app_scenario import Scenario
import logging
import time
import datetime
import csv

def parse_luid_engine(s):
    m = re.search(
        r"luid_0x([0-9A-Fa-f]+)_0x([0-9A-Fa-f]+).*?engtype_([A-Za-z0-9]+)",
        s
    )

    if not m:
        return ("unknown_unknown", "unknown")

    high    = int(m.group(1), 16)
    low     = int(m.group(2), 16)
    engtype = m.group(3)

    return (f"0x{high:08X}_0x{low:08X}", engtype)

def csv_to_map(csvtext):
    reader = csv.reader(csvtext.split("\n"))
    out = {}

    for row in reader:
        # Expected format: luid,adapter_name,adapter_type
        if len(row) != 3:
            continue

        key = row[0].strip()
        val = row[2].strip() or row[1].strip()

        out[key] = val

    return out

def limit_n(n):
    if 100 < n < 101:
        return 100.0
    if n < 1:
        return float(round(n))
    return n

class Tool(Scenario):
    '''
    Trace specified performance counters that report utilization.
    '''
    module = __module__.split('.')[-1]

    # Set default parameters
    Params.setDefault(module, 'processor_counter', '\\Processor(_Total)\\% Processor Time', desc="Processor counter to use")
    Params.setDefault(module, 'memory_counter', '\\Memory\\Available Bytes', desc="Memory counter to use")
    Params.setDefault(module, 'gpu_counter', '\\GPU Engine(*engtype_3D)\\Utilization Percentage', desc="GPU counter to use (per process, per instance)")
    Params.setDefault(module, 'npu_counter', '\\GPU Engine(*engtype_Compute)\\Utilization Percentage', desc="NPU counter to use (per process, per instance)")

    # Get parameters
    processor_counter = Params.get(module, 'processor_counter')
    memory_counter    = Params.get(module, 'memory_counter')
    gpu_counter       = Params.get(module, 'gpu_counter')
    npu_counter       = Params.get(module, 'npu_counter')

    counters = " ".join(f'"{c}"' for c in [processor_counter, memory_counter, gpu_counter, npu_counter])

    def initCallback(self, scenario):
        # Initialization code

        # Keep a pointer to the scenario that this tools is being run with
        self.scenario = scenario

        blg_filename   = "perfmon_util.blg"
        csv_filename   = "perfmon_util.csv"
        trace_filename = "perfmon_util.trace"

        self.blg_path_dut = os.path.join(self.scenario.dut_data_path, blg_filename)
        self.csv_path_dut = os.path.join(self.scenario.dut_data_path, csv_filename)

        self.blg_path_result   = os.path.join(self.scenario.result_dir, blg_filename)
        self.csv_path_result   = os.path.join(self.scenario.result_dir, csv_filename)
        self.trace_path_result = os.path.join(self.scenario.result_dir, trace_filename)

        luid_to_name_exe           = "map_luid_to_name.exe"
        self.luid_to_name_map_path = os.path.join(self.scenario.dut_exec_path, luid_to_name_exe)

        if self._call(["cmd.exe", "/c echo %PROCESSOR_ARCHITECTURE%"]).strip().lower() == "arm64":
            arch = "arm64"
        else:
            arch = "x64"

        self.scenario._upload(f"utilities\\open_source\\map_luid_to_name\\{arch}\\{luid_to_name_exe}", self.scenario.dut_exec_path)

        self.cleanup()

    def testBeginCallback(self):
        self.total_mem_bytes = int(self._call(["pwsh.exe", "-Command (Get-CimInstance -ClassName Win32_ComputerSystem).TotalPhysicalMemory"]).strip())
        self.luid_to_name_map = csv_to_map(self._call([self.luid_to_name_map_path], log_output=False))
        self._call(["typeperf.exe", f"{self.counters} -si 1 -f bin -o {self.blg_path_dut} -sc 0 -y"], blocking=False)

    def testEndCallback(self):
        self.cleanup()
        self._call(["relog.exe", f"{self.blg_path_dut} -c {self.counters} -f csv -o {self.csv_path_dut} -y"], log_output=False)

    def cleanup(self):
        self._kill("typeperf.exe")

    def dataReadyCallback(self):
        first_line = True
        luid_order, luid_util_map, col_to_luid = [], {}, {}
        df = None

        with open(self.csv_path_result, "r") as f:
            for line in f:
                if "Time" in line:
                    _, _, _, *gpu_entries = line.split(",")

                    for gpu_entry in gpu_entries:
                        luid = parse_luid_engine(gpu_entry)
                        luid_order.append(luid)
                        luid_util_map.setdefault(luid, 0.0)

                    columns = ["Timestamp", "CPU (%)", "Memory (%)"]
                    for k in luid_util_map:
                        col = f"{self.luid_to_name_map.get(k[0], k[0])} {k[1]} (%)"
                        col_to_luid[col] = k
                        columns.append(col)
                    df = pd.DataFrame(columns=columns)

                    continue

                timestamp, cpu_util, mem_util, *gpu_utils = line.split(",")

                luid_util_map_i = dict.fromkeys(luid_util_map, 0.0)
                for i, gpu_util in enumerate(gpu_utils):
                    gpu_util = gpu_util.replace('"', '').strip()
                    gpu_util = float(gpu_util) if gpu_util != "" else 0.0
                    luid_util_map_i[luid_order[i]] += gpu_util

                for k in luid_util_map:
                    luid_util_map[k] += luid_util_map_i[k]

                # Convert timestamp in the format "MM/DD/YYYY HH:MM:SS.MS" to seconds since epoch
                dt = datetime.datetime.strptime(timestamp.strip('"'), '%m/%d/%Y %H:%M:%S.%f')
                timestamp = time.mktime(dt.timetuple()) * 1000.0 + dt.microsecond / 1000.0

                if first_line:
                    first_line = False
                    # Use this as the starting time
                    self.start_time = float(timestamp) / 1000.0
                timestamp = float(timestamp) / 1000.0 - self.start_time

                # Convert available memory to used memory percentage
                mem_util = mem_util.replace('"', '').strip()
                mem_util = float(mem_util) if mem_util != "" else 0.0
                mem_util = 100.0 * (1.0 - (mem_util / self.total_mem_bytes))

                cpu_util = cpu_util.replace('"', '').strip()
                cpu_util = float(cpu_util) if cpu_util != "" else 0.0

                row = [timestamp, cpu_util, mem_util]
                for k in luid_util_map_i:
                    row.append(limit_n(luid_util_map_i[k]))
                df.loc[len(df)] = row

        try:
            os.remove(self.blg_path_result)
        except Exception as e:
            logging.error(f"Error deleting file: {e}")

        if df is None or len(df) <= 0:
            return

        cols_to_drop = df.columns[3:][df.iloc[:, 3:].eq(0).all()]
        df = df.drop(columns=cols_to_drop)

        luid_counts = {}
        for col in df.columns[3:]:
            k = col_to_luid[col]
            luid_counts[k[0]] = luid_counts.get(k[0], 0) + 1

        rename_cols = {}
        for col in df.columns[3:]:
            k = col_to_luid[col]

            if luid_counts[k[0]] == 1:
                rename_cols[col] = f"{self.luid_to_name_map.get(k[0], k[0])} (%)"
        df = df.rename(columns=rename_cols)

        rounding_dict = {df.columns[0]: 1}
        for col in df.columns[1:]:
            rounding_dict[col] = 2
        df = df.round(rounding_dict)

        df.iloc[:, 1:].mean().round(3).reset_index().to_csv(
            self.csv_path_result, header=False, index=False
        )

        df.to_csv(self.trace_path_result, index=False)
