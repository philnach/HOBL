'''
//--------------------------------------------------------------
//
// HOBL
// Copyright(c) Microsoft Corporation
// All rights reserved.
//
// MIT License
//
// Permission is hereby granted, free of charge, to any person obtaining
// a copy of this software and associated documentation files(the ''Software''),
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
'''

##
# Build tools documentation
##

import os
import argparse
from core.parameters import Params
from utilities.open_source.dump_tools import main as dump_tools_main
import importlib

def main():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-path', '-p', default='docs\\support\\docs')
    args = arg_parser.parse_args()
    doc_path = os.path.join(args.path, "HOBL_Tools.md")

    # Run utiliites/open_source/dump_tools.py to get scenario docs
    dump_tools_main(print_json=False, short=False)
    from utilities.open_source.dump_tools import scenario_docs

    with open(doc_path, "w", encoding="utf-8") as doc_file:
        doc_file.write("# HOBL Tools\n\n")
        for tool, docstring in scenario_docs.items():
            if docstring is not None:
                # write tool heading and docstring
                doc_file.write(f"## {tool}\n\n")
                doc_file.write(f"{docstring}\n\n")

                # import tool
                Params.clear()
                module = "tools." + tool
                importlib.import_module(module)

                # get parameters for tool
                Params.dumpDefaultWithInfo(print_json=False)

                if len(Params.defaultsInfo) == 0:
                    continue
                # write parameters to doc
                doc_file.write(f"\n<u>Parameters:</u>\n\n")
                for section in Params.defaultsInfo:
                    for key in Params.defaultsInfo[section]:
                        valOptions = Params.defaultsInfo[section][key]["valOptions"]

                        if len(valOptions) == 1 and valOptions[0].startswith("@\\"):
                            pass
                        else:
                            desc = Params.defaultsInfo[section][key]["desc"]
                            default = Params.get(section, key, log=False)
                            options = ""
                            if len(valOptions) > 0:
                                options = f" **Options:** `{', '.join(valOptions)}`"
                            doc_file.write(f"`{key}` - {desc} **Default:** `{default}` {options}\n\n")

if __name__ == '__main__':
    main()
