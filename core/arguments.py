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

import argparse

args = None

class Arguments(object):
    def __init__(self, args_to_parse = None):
        # Command line arguments
        global args
        arg_parser = argparse.ArgumentParser(description = "HOBL test framework.")
        arg_parser.add_argument('-execute', '-e', help='Execute another Python script.')
        arg_parser.add_argument('-dump', '-d', help='Dump the default parameters.')
        arg_parser.add_argument('-dump_verbose', '-dv', help='Dump the default parameters verbosely.')
        arg_parser.add_argument('-profile', '-p', help='File that specifies test parameters.')
        arg_parser.add_argument('-scenarios', '-s', help='Test scenarios to run.  For multiple scenarios, separate with space and surround with quotes.')
        arg_parser.add_argument('-attempts', '-a', help='How many times to re-attempt a scenario that fails')
        arg_parser.add_argument('-kill', '-k', help='kill/cleanup specified scenario')
        arg_parser.add_argument('overrides', nargs=argparse.REMAINDER, help='Specify test parameter overrides in the format: <scenario>:<key>=<val>')
        if args_to_parse:
            # args_to_parse should be a list
            args = arg_parser.parse_args(args_to_parse)
        else:
            args = arg_parser.parse_args()
