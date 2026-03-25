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

import hashlib
import importlib
import os
from pathlib import Path

def get_parent_modules(parent_modules, return_path=False, ext_paths=[]):
    scenarios = "scenarios"

    entries = [p for p in Path(scenarios).iterdir() if p.is_dir()]

    for ext_path in ext_paths:
        try:
            base  = Path(ext_path) / scenarios
            paths = [p for p in base.iterdir() if p.is_dir()]
            entries.extend(paths)
        except FileNotFoundError:
            pass

    entries = sorted(
        entries,
        key=lambda p: (p.name.lower() != "windows", p.name.lower())
    )

    mods_added = set()

    for p in entries:
        name = p.name
        if name.endswith("_resources") or name == "__pycache__":
            continue

        if return_path:
            mod = str(p)
        else:
            mod = f"{scenarios}.{name}"

        if mod in mods_added:
            continue
        mods_added.add(mod)
        parent_modules.append(mod)

    return parent_modules

def import_file(rel, here):
    here = os.path.abspath(here)

    if os.path.isdir(here):
        path = os.path.join(here, rel)
    else:
        path = os.path.join(os.path.dirname(here), rel)

    path = os.path.abspath(path)

    name = "mod_" + hashlib.md5(path.encode()).hexdigest()

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None

    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except FileNotFoundError:
        return None

def import_run_user_only(rel, here=None):
    if not here:
        here = os.getcwd()

    attr   = "run_user_only"
    module = import_file(os.path.join(rel, "default_params.py"), here)

    f = getattr(module, attr, None)
    if callable(f):
        f()
