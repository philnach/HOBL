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
# Device ping
##

import core.parameters
import argparse
import requests
import json

from urllib.parse import (
    urlparse,
    urlunparse
)

import core.call_rpc as rpc


def get_battery_status(code):
    return {
        1:  'Battery Discharging',
        2:  'AC Power',
        3:  'Fully Charged',
        4:  'Low',
        5:  'Critical',
        6:  'Charging',
        7:  'Charging and High',
        8:  'Charging and Low',
        9:  'Charging and Critical',
        10: 'Undefined',
        11: 'Partially Charged'
    }.get(code, 'Undefined')


def call(command):
    global dut_ip
    i = 0

    try:
        res = json.loads(
            rpc.call_rpc(
                dut_ip,
                8000,
                'RunWithResultAndExitCode',
                command,
                timeout=20
            )
        )

        if res and 'result' in res:
            return [
                int(res['result'][0]),
                res['result'][1].strip('\r\n')
            ]
    except:
        pass

    return [1, '']


def main():
    global dut_ip

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-profile', '-p')
    arg_parser.add_argument('overrides', nargs=argparse.REMAINDER)

    args = arg_parser.parse_args()

    if args.profile is None:
        print('Missing profile')
        return

    parameters.Params(args.profile)
    parameters.Params.setOverrides(args.overrides)

    dashboard_url = parameters.Params.get('global', 'dashboard_url')
    dut_name      = parameters.Params.get('global', 'dut_name')
    dut_ip        = parameters.Params.get('global', 'dut_ip')

    battery_status = 'Unavailable'
    battery_charge = -1

    result = call(['powershell.exe',
        '(Get-WmiObject -Class Win32_Battery -ea 0).BatteryStatus'
    ])

    if result[0] == 0:
        battery_status = get_battery_status(int(result[1]))

    result = call(['powershell.exe',
        'Add-Type -Assembly System.Windows.Forms; ' +
        '[Math]::round(([System.Windows.Forms.SystemInformation]::PowerStatus.BatteryLifePercent) * 100, 2)'
    ])

    if result[0] == 0:
        battery_charge = int(result[1])

    print(f'Battery info: {battery_status} {battery_charge}%')

    # try:
    url = urlunparse(
        urlparse(dashboard_url)._replace(
            path='/plan/DeviceUpdate'
        )
    )

    requests.post(
        url,
        {
            'deviceName':    dut_name,
            'batteryStatus': battery_status,
            'batteryCharge': battery_charge
        }
    )
    # except:
    #     print('Failed to upload battery info')


if __name__ == '__main__':
    main()
