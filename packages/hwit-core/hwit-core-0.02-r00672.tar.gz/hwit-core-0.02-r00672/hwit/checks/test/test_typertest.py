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
from hwit.checks.common import scaletyper, datetimetyper

class TestSevenValuedVote(HWITSourceLoader):

    def test_001(self):
        s = scaletyper()
        self.assertFalse(s.isSevenValuedVote("-4"))
        self.assertFalse(s.isSevenValuedVote("-3"))
        self.assertFalse(s.isSevenValuedVote("-2"))
        self.assertFalse(s.isSevenValuedVote("-1"))
        self.assertFalse(s.isSevenValuedVote("0"))
        self.assertFalse(s.isSevenValuedVote("1"))
        self.assertFalse(s.isSevenValuedVote("2"))
        self.assertFalse(s.isSevenValuedVote("3"))
        self.assertFalse(s.isSevenValuedVote("4"))

    def test_002(self):
        s = scaletyper()
        self.assertTrue(s.isSevenValuedVote("strongly disagree"))
        self.assertTrue(s.isSevenValuedVote("disagree"))
        self.assertTrue(s.isSevenValuedVote("partially disagree"))
        self.assertTrue(s.isSevenValuedVote("undecided"))
        self.assertTrue(s.isSevenValuedVote("partially agree"))
        self.assertTrue(s.isSevenValuedVote("disagree"))
        self.assertTrue(s.isSevenValuedVote("strongly agree"))

    def test_003(self):
        s = scaletyper()
        self.assertEqual(s.isSevenValuedVote.min, -3)
        self.assertEqual(s.isSevenValuedVote.max, 3)

    def test_004(self):
        s = scaletyper()
        self.assertEqual(
        s.isSevenValuedVote.labels[-3],"Strongly disagree".lower())
        self.assertEqual(
        s.isSevenValuedVote.labels[-2],"Disagree".lower())
        self.assertEqual(
        s.isSevenValuedVote.labels[-1],"Partially disagree".lower())
        self.assertEqual(
        s.isSevenValuedVote.labels[0],"Undecided".lower())
        self.assertEqual(
        s.isSevenValuedVote.labels[1],"Partially agree".lower())
        self.assertEqual(
        s.isSevenValuedVote.labels[2],"Agree".lower())
        self.assertEqual(
        s.isSevenValuedVote.labels[3],"Strongly agree".lower())

class TestDateTimeTyper(HWITSourceLoader):

    def test_001(self):
        t = datetimetyper()
        self.assertFalse(t.isISOTime(""))
        self.assertFalse(t.isISOTime("None"))
        self.assertFalse(t.isISOTime("30"))
        self.assertFalse(t.isISOTime("30:"))
        self.assertFalse(t.isISOTime("30:2"))
        self.assertFalse(t.isISOTime("2:30:2"))
        self.assertFalse(t.isISOTime("2:30:02"))
        self.assertFalse(t.isISOTime("32:30:02"))
        self.assertTrue(t.isISOTime("02:30:02"))

    def test_002(self):
        t = datetimetyper()
        self.assertFalse(t.isISODate(""))
        self.assertFalse(t.isISODate("None"))
        self.assertFalse(t.isISODate("30"))
        self.assertFalse(t.isISODate("30-"))
        self.assertFalse(t.isISODate("30-2"))
        self.assertFalse(t.isISODate("2-03-2"))
        self.assertFalse(t.isISODate("2-03-02"))
        self.assertFalse(t.isISODate("20-03-02"))
        self.assertFalse(t.isISODate("200-03-02"))
        self.assertFalse(t.isISODate("2000-30-02"))
        self.assertTrue(t.isISODate("2000-03-02"))

    def test_003(self):
        t = datetimetyper()
        self.assertFalse(t.isISODateTime(""))
        self.assertFalse(t.isISODateTime("None"))
        self.assertFalse(t.isISODateTime("30"))
        self.assertFalse(t.isISODateTime("30-"))
        self.assertFalse(t.isISODateTime("30-2"))
        self.assertFalse(t.isISODateTime("2-03-2"))
        self.assertFalse(t.isISODateTime("2-03-02"))
        self.assertFalse(t.isISODateTime("20-03-02"))
        self.assertFalse(t.isISODateTime("200-03-02"))
        self.assertFalse(t.isISODateTime("2000-30-02"))
        self.assertFalse(t.isISODateTime("2000-03-02 30"))
        self.assertFalse(t.isISODateTime("2000-03-02 30:"))
        self.assertFalse(t.isISODateTime("2000-03-02 30:2"))
        self.assertFalse(t.isISODateTime("2000-03-02 2:30:2"))
        self.assertFalse(t.isISODateTime("2000-03-02 2:30:02"))
        self.assertFalse(t.isISODateTime("2000-03-02 32:30:02"))
        self.assertTrue(t.isISODateTime("2000-03-02 02:30:02"))
        # current limitation
        self.assertFalse(t.isISODateTime("2000-03-02 02:30:02Z"))

def load_tests(ldr=unittest.TestLoader(), suite=None, pttrn=None):
    testCases = (TestSevenValuedVote, TestDateTimeTyper)
    rv = unittest.TestSuite()
    for i in testCases:
        tests = ldr.loadTestsFromTestCase(i)
        rv.addTests(tests)
    return rv

def run():
    unittest.TextTestRunner(verbosity=2).run(load_tests())
