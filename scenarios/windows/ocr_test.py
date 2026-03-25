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

import core.app_scenario
from core.parameters import Params
import logging
import time
import cv2 as cv
import easyocr

# Tutorial for creating a scenario:
#   - Launch Notepad, type, and exit
#   - Kill routine to clean up after failure or termination

class OCRTest(core.app_scenario.Scenario):
    # Set default parameters
    Params.setDefault('ocr', 'duration', '30')  # Seconds

    # Get parameter values
    duration = Params.get('ocr', 'duration')


    def setUp(self):
        # this needs to run only once to load the model into memory
        self.reader = easyocr.Reader(['en'], gpu = False)

        # Call base class setUp() to start power measurment
        core.app_scenario.Scenario.setUp(self)
            # Create hobl_data folder
            # Tool init callback
            # Config_check
            # Tool begin callback
            # Start tracing
            # Test begin callback


    def runTest(self):
        bot_count = 0
        logging.info("Reading image")
        img = cv.imread('c:\\temp\\teams.png', cv.IMREAD_GRAYSCALE)
        img = cv.Canny(img, 5, 30)

        result = self.reader.readtext(img, detail = 0)
        for t in result:
            if t.startswith("Bot"):
                bot_count += 1
                logging.info(t)
        logging.info(f"Bot count: {bot_count}")



    def tearDown(self):
        # Call base class tearDown() to stop power measurment
        core.app_scenario.Scenario.tearDown(self)
            # Test end callback
            # Tool end callback
            # Stop tracing
            # Post config_check
            # Copy data back from DUT
            # Tool data ready callback
            # Test data ready callback
            # Tool report callback

