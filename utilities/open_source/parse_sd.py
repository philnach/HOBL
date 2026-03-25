"""
//--------------------------------------------------------------
//
// parse_sd
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
import pandas as pd

arg_parser = argparse.ArgumentParser(description = "Summarizes SystemDeck results into a list of key-vals.")
arg_parser.add_argument('-input', '-i', help='Path to sd summary .csv file.')
arg_parser.add_argument('-output', '-o', help='Path of output .csv file.')
args = arg_parser.parse_args()

df = pd.read_csv(args.input, sep=',', header=0, engine="python")
df = df.filter(regex=r'(?<=CORE\d\s)(Power|Freq\sEff)|((?<=OFF\s)Residency)|(?:Whisper\sMode)|(?:CstateBoost)|(?:GFX\sFreq)|(?:Refresh)|(?:DCE)|(?:IO\sReadsWrites)', axis=1)
s_mean = df.mean()
# grouped = s_mean.groupby(s_mean.index.str.extract(r'(?:CPU\d )?(?:.*CORE\d )?(.*)', expand=False)).mean()
# print(grouped)
s_mean = s_mean.add_prefix("SD ")
print (s_mean)
s_mean.to_csv(args.output, sep=',', float_format='%0.3f', header=False)
