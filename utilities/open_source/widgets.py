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
from PyQt6 import QtWidgets
import requests
from urllib.parse import urlparse, urlunparse

from core.parameters import Params


class Widgets:
    dashboard_url     = Params.get('global', 'dashboard_url')
    dashboard_plan_id = Params.get('global', 'dashboard_plan_id')


    def __init__(self):
        if self.dashboard_url == "":
            self.app = QtWidgets.QApplication([])


    def _call_widget(self, path, data):
        data["planId"] = self.dashboard_plan_id

        url = urlunparse(
            urlparse(self.dashboard_url)._replace(
                path=path
            )
        )

        while True:
            try:
                response = requests.post(
                    url,
                    data,
                    timeout=10
                )

                if response.status_code == 200:
                    break
            except Exception as e:
                pass


    def about(self, title, text):
        if self.dashboard_url == "":
            QtWidgets.QMessageBox.about(None, title, text)
        else:
            self._call_widget(
                "/plan/Widget",
                {
                    "title": title,
                    "text": text
                }
            )
