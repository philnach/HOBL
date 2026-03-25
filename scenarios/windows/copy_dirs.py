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

##
# Copy the specified files/directories to a new location
##

import re
import logging
import os
import sys

import core.app_scenario
from core.parameters import Params


class CopyDirs(core.app_scenario.Scenario):
    module = __module__.split('.')[-1]

    is_prep = True

    Params.setOverride('global', 'local_execution',    '1')
    Params.setOverride('global', 'post_run_delay', '0')

    Params.setDefault(module, 'from_dir',  '')
    Params.setDefault(module, 'to_dir',    '')
    Params.setDefault(module, 'paths',     '')
    Params.setDefault(module, 'patterns',  '*')

    Params.setDefault(module, 'share_username', '')
    Params.setDefault(module, 'share_password', '')

    # Get parameters
    from_dir  = Params.get(module, 'from_dir')
    to_dir    = Params.get(module, 'to_dir')
    paths     = Params.get(module, 'paths')
    patterns  = Params.get(module, 'patterns')

    share_username = Params.get(module, 'share_username')
    share_password = Params.get(module, 'share_password')


    def get_share_path(self, path):
        r = re.search(
            r"^\\\\([^\\]+)\\([^\\]+)",
            path
        )

        return r.group(0) if r else ""


    def perform_copy(self, relpath):
        abspath = os.path.join(self.from_dir, relpath)

        if os.path.isfile(abspath):
            src  = self.from_dir
            dst  = self.to_dir
            file = relpath

            cmd = f"cmd.exe /c robocopy {src} {dst} {file} /r:0 /im /is /it > nul"

            logging.info(f"Copying {os.path.join(src, file)} to {dst}")

            try:
                self._host_call(cmd, expected_exit_code="1")
            except:
                raise Exception(f"Copying failed")
        else:
            for pattern in self.patterns.split(" "):
                src  = abspath
                dst  = os.path.join(self.to_dir, relpath)
                file = pattern

                cmd = f"cmd.exe /c robocopy {src} {dst} {file} /s /r:0 /im /is /it > nul"

                logging.info(f"Copying {os.path.join(src, file)} to {dst}")

                try:
                    self._host_call(cmd, expected_exit_code="1")
                except:
                    raise Exception(f"Copying failed")


    def setUp(self):
        # Don't call base setUp so that we don't interact with DUT
        return


    def runTest(self):
        # app = QtWidgets.QApplication(sys.argv)

        if self.from_dir == "":
            raise Exception("Source directory path is invalid")

        if self.to_dir == "":
            raise Exception("Destination directory path is invalid")
            # self.to_dir = QtWidgets.QFileDialog.getExistingDirectory(
            #     None,
            #     "Enter destination directory path",
            #     "c:\\",
            #     QtWidgets.QFileDialog.ShowDirsOnly
            # )

            # if self.to_dir == "":
            #     raise Exception("Destination directory path is invalid")

        if self.paths == "":
            # Only copy the base directory specified by from_dir
            self.from_dir, self.paths = os.path.split(self.from_dir)

        # Avoid net use if copying to the same file system
        from_root = self.from_dir.lstrip(os.sep).split(os.sep)[0]
        to_root = self.to_dir.lstrip(os.sep).split(os.sep)[0]
        logging.debug(f"from_root: {from_root}, to_root: {to_root}")

        if self.share_username and self.share_password and from_root != to_root:
            share_path = self.get_share_path(self.to_dir)

            if share_path:
                self._host_call(
                    f"cmd.exe /c net use {share_path} {self.share_password} /user:{self.share_username}",
                    expected_exit_code=""
                )

        for relpath in self.paths.split(" "):
            self.perform_copy(relpath)


    def tearDown(self):
        # Don't call base tearDown so that we don't interact with DUT
        return


    def kill(self):
        from_root = self.from_dir.lstrip(os.sep).split(os.sep)[0]
        to_root = self.to_dir.lstrip(os.sep).split(os.sep)[0]

        if self.share_username and self.share_password and from_root != to_root:
            share_path = self.get_share_path(self.to_dir)

            if share_path:
                self._host_call(
                    f"cmd.exe /c net use {share_path} /delete",
                    expected_exit_code=""
                )

        # Prevent base kill routine from running
        return 0
