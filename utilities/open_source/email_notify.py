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
import json
import requests
import logging
import inspect
import urllib

from urllib.parse import (
    urlparse,
    urlunparse,
    urlencode
)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.parameters import Params


def get_params():
    global sender_email_addr
    global sender_email_password

    global notify_email_list
    global fail_email_list

    global dashboard_url
    global dashboard_plan_id

    global run_type

    sender_email_addr      = Params.get('global', 'sender_email_addr')
    sender_email_password  = Params.get('global', 'sender_email_password')

    notify_email_list = Params.get('global', 'notify_email_list').split(" ")
    fail_email_list   = Params.get('global', 'fail_email_list').split(" ")

    dashboard_url     = Params.get('global', 'dashboard_url')
    dashboard_plan_id = Params.get('global', 'dashboard_plan_id')


def get_summary_data(plan_run_type=""):
    url = urlunparse(
        urlparse(dashboard_url)._replace(
            path="/plan/SummaryDataById"
        )
    )

    data = requests.post(
        url,
        {
            "planId": int(dashboard_plan_id),
            "runType": plan_run_type
        }
    ).json()

    return data


def send_email(subject, rcpt_list, body):
    message = MIMEMultipart()
    rcpt_string = ",".join(rcpt_list)
    message["Subject"] = subject
    message["From"]    = f"Surface Power Notification <{sender_email_addr}>"
    message["To"]      = rcpt_string

    message.attach(
        MIMEText(
            body,
            "html"
        )
    )

    with smtplib.SMTP("smtp-mail.outlook.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender_email_addr, sender_email_password)

        smtp.sendmail(
            sender_email_addr,
            rcpt_list,
            message.as_string()
        )


def send_fail_email(test_case, run_dir, result):
    get_params()

    if not dashboard_url:
        print("Dashboard url not present")
        return

    if not fail_email_list[0]:
        print("Fail email list not present")
        return

    try:
        data = get_summary_data()
    except:
        print("Error sending POST request")
        return

    scenarios_url = urlunparse(
        urlparse(dashboard_url)._replace(
            path="/plan/Scenarios",
            query=urlencode({
                "PlanID": dashboard_plan_id
        }))
    )

    results_url = urlunparse(
        urlparse(dashboard_url)._replace(
            path="/result/Results",
            query=urlencode({
                "path": run_dir
        }))
    )

    body = inspect.cleandoc(f"""
        <html>
        <body>

        <div style="margin-bottom:12px">
            For plan <b>{data["Plan"]}</b>
        </div>

        <div style="margin-bottom:12px">
            Scenarios page: <a href="{scenarios_url}">scenarios</a>
        </div>

        <div style="margin-bottom:12px">
            Results page: <a href="{results_url}">results</a>
        </div>
    """)

    if len(result.errors) > 0:
        body += (
            "<pre>"
            "<code>"
            f"{result.errors[0][1]}"
            "</code>"
            "</pre>"
            "</body>"
            "</html>"
        )
    elif len(result.failures) > 0:
        body += (
            "<pre>"
            "<code>"
            f"{result.failures[0][1]}"
            "</code>"
            "</pre>"
            "</body>"
            "</html>"
        )
    else:
        body += (
            "</body>"
            "</html>"
        )

    subject = f"{data['Profile']} scenario {test_case} has failed"

    try:
        send_email(subject, fail_email_list, body)

        print("Fail email successfully sent")
    except:
        print("Unable to send fail email")


def get_email_body(data):
    summary_url = urlunparse(
        urlparse(dashboard_url)._replace(
            path="/plan/Summary",
            query=urlencode({
                "profile_filter": data["Profile"],
                "run_dir_filter": data["ResultDir"],
                "plan_filter":    data["Plan"]
        }))
    )

    summary_data = json.loads(data["SummaryDataStr"])
    print(summary_data)

    if "Stats" in summary_data:
        summary_data = summary_data["Stats"]

    tag_th_list = []

    try:
        for header in summary_data[0]:
            tag_th_list.append(f"""\
                <th>
                    <div style="margin: 0 4px 0 4px">
                        {header}
                    </div>
                </th>
            """)
    except:
        return f"""\
            <html>
                <body>
                    <div style="margin: 12px 0 8px 0">
                        Job Notification
                    </div>
                </body>
            </html>
        """

    tag_tr_list = []

    for row in summary_data:
        if row["Scenario"] == "notify":
            continue

        tag_td_list = []

        tag_td_list.append(f"""
            <td>
                {row["Scenario"]}
            </td>
        """)

        for scenario, result in row.items():
            if result == None:
                continue
            if scenario == "Scenario":
                continue

            result = result.split(',')

            td_div_common_style = "width:38px; margin-right:4px; border-radius:7px; display:inline-block;"

            div_0 = ""
            div_1 = ""
            div_2 = ""
            div_3 = ""

            if int(result[0]) > 0:
                div_0 = f"""
                    <div
                        style="{td_div_common_style} background-color:grey"
                    >
                        {result[0]}
                    </div>
                """

            if int(result[1]) > 0:
                div_1 = f"""
                    <div
                        style="{td_div_common_style} background-color:blue"
                    >
                        {result[1]}
                    </div>
                """

            if int(result[2]) > 0:
                div_2 = f"""
                    <div
                        style="{td_div_common_style} background-color:green"
                    >
                        {result[2]}
                    </div>
                """

            if int(result[3]) > 0:
                div_3 = f"""
                    <div
                        style="{td_div_common_style} background-color:red"
                    >
                        {result[3]}
                    </div>
                """

            tag_td_list.append(f"""\
                <td>
                    {div_0}
                    {div_1}
                    {div_2}
                    {div_3}
                </td>
            """)

        tag_tr_list.append(f"""\
            <tr>
                {"".join(tag_td_list)}
            </tr>
        """)

    return f"""\
        <html>
            <body>
                <div style="margin-bottom:12px">
                    Summary page: <a href="{summary_url}">summary</a>
                </div>

                <div style="margin: 12px 0 8px 0">
                    Summary highlights:
                </div>

                <table border="1" style="width:100%; text-align:center">
                    <thead>
                        <tr>
                            {"".join(tag_th_list)}
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(tag_tr_list)}
                    </tbody>
                </table>
            </body>
        </html>
    """


def send_plan_complete_email(plan_run_type):
    get_params()

    if not dashboard_url:
        logging.error("Dashboard url not present")
        return

    if not notify_email_list[0]:
        logging.error("Notify email list not present")
        return

    try:
        data = get_summary_data(plan_run_type)
    except:
        logging.error("Error sending POST request")
        return

    subject = f"{data['Profile']} plan {data['Plan']} has completed"
    body    = get_email_body(data)

    try:
        send_email(subject, notify_email_list, body)

        logging.info("Plan complete email successfully sent")
    except:
        logging.error("Unable to send plan complete email")
