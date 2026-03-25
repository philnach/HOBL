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
# Dump scenarios
##

import os
import json
import ast

scenario_docs = {}

def extract_docstrings(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            if hasattr(node, "name"):
                docstring = ast.get_docstring(node)
                if docstring:
                    return docstring
    return None


def get_parent_modules(parent_modules):
    scenarios = "scenarios"

    entries = sorted(
        os.listdir(scenarios),
        key=lambda x: (x.lower() != "windows", x.lower())
    )

    for name in entries:
        if name.endswith("_resources") or name == "__pycache__":
            continue

        path = os.path.join(scenarios, name)
        if os.path.isdir(path):
            parent_modules.append(path)

    return parent_modules


def main(print_json=True, short=True):

    scenarios_dir = os.path.join(os.getcwd(), 'scenarios')

    for subdir in ["windows", "common", "macos"]:
        scenarios_dir_sub = os.path.join(scenarios_dir, subdir)
        # print(f"Inspecting directory: {scenarios_dir_sub}")

        for filename in os.listdir(scenarios_dir_sub):
            path = os.path.join(scenarios_dir_sub, filename)
            # if filename is a directory
            if os.path.isdir(path):
                path = os.path.join(path, filename + ".py")
                filename = filename + ".py"
            if not os.path.isfile(path):
                continue
            if filename.endswith('.py') and filename != '__init__.py':
                docstring = extract_docstrings(path)
                if short and docstring is not None:
                    # get first paragraph only
                    docstring = docstring.split('\n\n')[0]
                # remove '.py' extension
                module_name = filename[:-3]
                scenario_docs[module_name] = docstring

    if print_json:
        print(json.dumps(scenario_docs))


if __name__ == '__main__':
    main()
