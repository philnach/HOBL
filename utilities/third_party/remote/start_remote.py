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
# Start remote
##

from core.parameters import Params
import argparse

import core.call_rpc as rpc


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-profile', '-p')
    arg_parser.add_argument('overrides', nargs=argparse.REMAINDER)

    args = arg_parser.parse_args()

    if args.profile is None:
        print('Missing profile')
        return

    Params(args.profile)
    Params.setOverrides(args.overrides)

    Params.setDefault('global', 'platform', 'Windows', desc="Operating system platform.", valOptions=["Windows", "Android", "W365", "MacOS"])
    Params.setDefault('global', 'remote_share_path', '')
    Params.setDefault('global', 'remote_share_username', '')
    Params.setDefault('global', 'remote_share_password', '')

    dut_ip   = Params.get('global', 'dut_ip')
    platform = Params.get('global', 'platform')

    def call(cmd):
        rpc.call_rpc(dut_ip, 8000, 'Run', cmd)

    share_path     = Params.get('global', 'remote_share_path')
    share_username = Params.get('global', 'remote_share_username')
    share_password = Params.get('global', 'remote_share_password')

    if share_path != '':
        call(["cmd.exe", f"/C net use z: {share_path} {share_password} /user:{share_username}"])

    args = ""

    if platform.lower() == "w365":
        args = "-topmostWindow"

    call(['C:\\hobl_bin\\remote\\remote.exe', args])


if __name__ == '__main__':
    main()
