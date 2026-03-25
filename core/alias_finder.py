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

import sys, importlib, importlib.abc, importlib.util

script_map = {
    "parameters":         "core.parameters",
    "arguments":          "core.arguments",
    "action_list":        "core.action_list",
    "utilities.call_rpc": "core.call_rpc",

    "scenarios.app_scenario": "core.app_scenario",

    "utilities.modules":       "utilities.open_source.modules",
    "utilities.dump_tools":    "utilities.open_source.dump_tools",
    "utilities.scenario_type": "utilities.open_source.scenario_type",
    "utilities.device_ping":   "utilities.open_source.device_ping",

    "utilities.remote":              "utilities.third_party.remote",
    "utilities.remote.start_remote": "utilities.third_party.remote.start_remote",
}

if "-d" in sys.argv or "-dv" in sys.argv:
    script_map["core.app_scenario"] = "core.stub.app_scenario_stub"
    script_map["core.parameters"]   = "core.stub.parameters_stub"
    script_map["core.call_rpc"]     = "core.stub.call_rpc_stub"

class _AliasLoader(importlib.abc.Loader):
    def __init__(self, fullname, realname):
        self.fullname = fullname
        self.realname = realname

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        real_module = importlib.import_module(self.realname)
        sys.modules[self.fullname] = real_module

class AliasFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        real = script_map.get(fullname)
        if not real:
            return None

        return importlib.util.spec_from_loader(
            fullname,
            _AliasLoader(fullname, real),
            origin=f"Alias of {real}"
        )

sys.meta_path.insert(0, AliasFinder())
