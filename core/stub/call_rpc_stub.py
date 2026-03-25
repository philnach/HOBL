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

def call_rpc(host, port, method, params, host_ip=None, rpc_callback_port=None, log = True, timeout = 1800, priority="Normal"):
    return ""

def _call_rpc(host, port, payload, log = True, timeout = 1800):
    return ""

def upload(host, port, source, dest):
    pass

def download(host, port, source, dest):
    pass

def plugin_load(host, port, dll_id, dll_class, dll_path):
    return ""

def plugin_call(host, port, dll_id, method, *arg):
    return ""

def plugin_screenshot(host, port, dll_id, x=0.0, y=0.0, w=1.0, h=1.0, screenIndex=0):
    return ""

def plugin_screen_info(host, port, dll_id):
    return []

def get_job_result(host, port, jobid, log=True):
    return ""
