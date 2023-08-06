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

import unittest
import csv
from StringIO import StringIO

from hwit.core.test import HWITSourceLoader
from hwit.core.generator import Generator

class TestHWITGenerator(HWITSourceLoader):

    def setUp(self):
        self.srcFiles["template"] = "ref/scout_camp.tsv"
        HWITSourceLoader.setUp(self)

    def test_001(self):
        gen = Generator()
        rdr = csv.reader(self.srcData["template"], delimiter = '\t')
        while True:
            try:
                gen.process(rdr.next())
            except StopIteration:
                break

        output = StringIO()
        gen.write(output)
        self.assertTrue(len(gen.columns) == 8)

        # Get the magic number with `wc -m ref/scout_camp.hwit`
        self.assertEqual(len(output.getvalue())+1, 3173)

    def test_002(self):
        gen = Generator()
        rdr = csv.reader(self.srcData["template"], delimiter = '\t')
        while True:
            try:
                gen.process(rdr.next())
            except StopIteration:
                break

        self.assertTrue(len(gen.groups) == 2)

    def test_003(self):
        tagVal = "${REQ_LIFEJACKET}"
        gen = Generator()
        rdr = csv.reader(self.srcData["template"], delimiter = '\t')
        while True:
            try:
                gen.process(rdr.next())
            except StopIteration:
                break

        output = StringIO()
        self.assertFalse(gen.tag("req","Umbrella"))
        self.assertTrue(gen.tag("req","Lifejacket"))
        gen.write(output)

        # Get the magic number with `wc -m ref/scout_camp.hwit`
        self.assertEqual(len(output.getvalue())+1, 3173+len(tagVal))


def suite():
    load = unittest.TestLoader().loadTestsFromTestCase
    suite = load(TestHWITGenerator)
    return suite
            
def run():
    unittest.TextTestRunner(verbosity=2).run(suite())
    def test_002(self):
        tagVal = "${REQ_LIFEJACKET}"
        gen = Generator()
        rdr = csv.reader(self.tsv, delimiter = '\t')
        while True:
            try:
                gen.process(rdr.next())
            except StopIteration:
                break

        output = StringIO()
        self.assertFalse(gen.tag("req","Umbrella"))
        self.assertTrue(gen.tag("req","Lifejacket"))
        gen.write(output)

        # Get the magic number with `wc -m ref/scout_camp.hwit`
        self.assertEqual(len(output.getvalue())+1, 3145+len(tagVal))

    def tearDown(self):
        self.tsv.close()

def load_tests(ldr=unittest.TestLoader(), suite=None, pttrn=None):
    testCases = (TestHWITGenerator,)
    rv = unittest.TestSuite()
    for i in testCases:
        tests = ldr.loadTestsFromTestCase(i)
        rv.addTests(tests)
    return rv

def run():
    unittest.TextTestRunner(verbosity=2).run(load_tests())
