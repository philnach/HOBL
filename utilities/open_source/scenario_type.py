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
# Determine if scenario is a prep or not.
##

import os
import json
import ast
import argparse
from utilities.open_source.modules import get_parent_modules

def is_prep(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())

    for node in ast.walk(tree):
        if isinstance(node, (ast.Name)):
            if hasattr(node, "id"):
                if (node.id == "is_prep"):
                    return True
    return False

def scenario_type(scenarios, hobl_ext_paths):
    parent_modules = get_parent_modules(
        ["scenarios", *[os.path.join(p, "scenarios") for p in hobl_ext_paths]],
        return_path=True, ext_paths=hobl_ext_paths
    )

    scenario_type_dict = {}

    for scenario in scenarios:
        found = False

        for parent_path in parent_modules:
            # Pure python scenario may be at the top level
            scenario_path1 = os.path.join(parent_path, scenario + ".py")
            # ScenarioMaker scenarios are in subfolder of same name as scenario
            scenario_path2 = os.path.join(parent_path, scenario, scenario + ".py")
            # Check for existence of either path
            if os.path.exists(scenario_path1):
                found = True
                is_prep_result = is_prep(scenario_path1)
                scenario_type_dict[scenario] = is_prep_result
                break
            elif os.path.exists(scenario_path2):
                found = True
                is_prep_result = is_prep(scenario_path2)
                scenario_type_dict[scenario] = is_prep_result
                break

        if not found:
            scenario_type_dict[scenario] = False

    return scenario_type_dict

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-scenarios', '-s', default='')
    arg_parser.add_argument('-hobl_external', '-he', default='')
    args = arg_parser.parse_args()
    scenarios = args.scenarios.split()
    hobl_ext_paths = args.hobl_external.split()

    print(json.dumps(scenario_type(scenarios, hobl_ext_paths)))


if __name__ == '__main__':
    main()
