#--------------------------------------------------------------
#
# HOBL
# Copyright(c) Microsoft Corporation
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files(the ""Software""),
# to deal in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions :
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF
# OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#--------------------------------------------------------------

##
# Invoke lvp scenario with video_file set to JB2_0.mp4
##

from core.parameters import Params
Params.setOverride("lvp_jeita", "title", "JB3_0-MOVIE")
Params.setOverride("lvp_jeita", "airplane_mode", "0")
import scenarios.windows.lvp

Params.setAssociatedSections("lvp_jeita", ["lvp"])

class LvpJeitaPrep(scenarios.windows.lvp.LVP):
    """
    Plays a video in full screen mode in accordance with reqirements set by the Japan Electronics and Information Technology Industries Association for battery operated electronic devices being released in Japan.

    Please do not alter parameters as they have been set to meet the requirements of that governing body
    """
    module = __module__.split('.')[-1]

