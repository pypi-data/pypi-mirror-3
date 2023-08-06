#!/usr/bin/env python
#    -*-    encoding: UTF-8    -*-

#   copyright 2009 D Haynes
#
#   This file is part of the HWIT distribution.
#
#   HWIT is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   HWIT is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with HWIT.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os.path
import unittest

import pkg_resources

class HWITSourceLoader(unittest.TestCase):
       
    srcFiles = {
    "blank": "ref/blank.hwit",
    "empty": "ref/empty.hwit",
    "basic": "ref/basic.hwit",
    "small": "ref/small.hwit",
    "partial": "ref/hwit-partial.hwit",
    "risky": "ref/risky.hwit",
    "osvaldo-3915": "ref/osvaldo-3915.hwit",
    "underskirts-3915": "ref/underskirts-3915.hwit",
    "corrugation-3003": "ref/corrugation-3003.hwit"
    }
 
    srcData = {}

    def setUp(self):
        """ Load sources into memory """
        for k,v in self.srcFiles.items():
            try:
                self.srcData[k] = pkg_resources.resource_stream(__name__, v)
            except pkg_resources.ExtractionError:
                sys.stderr.write("\nCouldn't open %s\n" % v)

    def tearDown(self):
        for fObj in self.srcData.values():
            fObj.close()

