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
import os
import os.path
import unittest
import subprocess
import tempfile
import re
from StringIO import StringIO

import hwit.core
from hwit.core.test import HWITSourceLoader
from hwit.core.console import HWITTerm
from hwit.core.parser import package_path

class TestConsoleReport(HWITSourceLoader):

    rptRE = re.compile("([\S]+):[\s]+(.+)")

    def parse_report_for_fields(self, rpt):
        return dict(self.rptRE.findall(rpt))

    def parse_fields_for_stats(self, fields):
        return dict([tuple(reversed(i.strip().split())) for i in
        fields.get("Stats","").split(',')])

    def test_001(self):
        """
            Test that we can read a blank container, and that it contains
            no groups, but has metadata
        """
        out = StringIO()
        term = HWITTerm(self.srcData["blank"], stdout=out)
        term.onecmd("report")
        fields = self.parse_report_for_fields(out.getvalue())
        self.assertTrue(fields.get("File","").endswith(
            os.path.join("ref","blank.hwit")))
        self.assertEqual(fields.get("Expires",""),"2010-06-28")

    def test_002(self):
        """
            Test that we can read an empty container, and that it contains
            no groups, but has metadata
        """
        out = StringIO()
        term = HWITTerm(self.srcData["empty"], stdout=out)
        term.onecmd("report")
        fields = self.parse_report_for_fields(out.getvalue())
        self.assertTrue(fields.get("File","").endswith(
            os.path.join("ref","empty.hwit")))
        self.assertEqual(fields.get("Expires",""),"2010-06-30")

    def test_003(self):
        """
            Test that we can read a basic container, which contains
            a group, and has metadata
        """
        out = StringIO()
        term = HWITTerm(self.srcData["basic"], stdout=out)
        term.onecmd("report")
        fields = self.parse_report_for_fields(out.getvalue())
        self.assertTrue(fields.get("File","").endswith(
            os.path.join("ref","basic.hwit")))
        self.assertEqual(fields.get("Expires",""),"2010-06-30")
        self.assertEqual(
        len(fields.get("Groups","1").strip().split(',')),1)
        self.assertEqual(fields.get("State",""), "_")

    def test_004(self):
        """
            Test that we can read a small container, which contains
            groups and interleaved text, and has metadata
        """
        out = StringIO()
        term = HWITTerm(self.srcData["small"], stdout=out)
        term.onecmd("report")
        fields = self.parse_report_for_fields(out.getvalue())
        self.assertTrue(fields.get("File","").endswith(
            os.path.join("ref","small.hwit")))
        self.assertEqual(fields.get("Expires",""),"2010-07-01")
        self.assertEqual(
        len(fields.get("Groups","1").strip().split(',')),2)
        self.assertEqual(fields.get("State",""), "_ _00")

class TestConsoleGroup(HWITSourceLoader):

    def test_001(self):
        """
            Test selecting groups by ordinal: no groups
        """
        out = StringIO()
        term = HWITTerm(self.srcData["empty"], stdout=out)
        term.onecmd("group 0")
        self.assertTrue("out of range" in out.getvalue())
        term.onecmd("group 1")
        self.assertTrue("no group" in out.getvalue())

    def test_002(self):
        """
            Test selecting groups by ordinal: no group given
        """
        out = StringIO()
        term = HWITTerm(self.srcData["basic"], stdout=out)
        term.onecmd("group")
        self.assertTrue("is selected" in out.getvalue())

    def test_003(self):
        """
            Test selecting groups by ordinal: group out of range
        """
        out = StringIO()
        term = HWITTerm(self.srcData["basic"], stdout=out)
        term.onecmd("group 0")
        self.assertTrue("out of range" in out.getvalue())
        term.onecmd("group 2")
        self.assertTrue("out of range" in out.getvalue())

    def test_004(self):
        """
            Test selecting groups by ordinal: group in range
        """
        out = StringIO()
        term = HWITTerm(self.srcData["basic"], stdout=out)
        term.onecmd("group 1")
        self.assertTrue("is selected" in out.getvalue())

    def test_005(self):
        """
            Test selecting groups with up
        """
        out = StringIO()
        term = HWITTerm(self.srcData["small"], stdout=out)
        term.onecmd("group 2")
        self.assertTrue("2' is selected" in out.getvalue())
        term.onecmd("group up")
        self.assertTrue("1' is selected" in out.getvalue())

    def test_006(self):
        """
            Test selecting groups with down
        """
        out = StringIO()
        term = HWITTerm(self.srcData["small"], stdout=out)
        term.onecmd("group 1")
        self.assertTrue("1' is selected" in out.getvalue())
        term.onecmd("group down")
        self.assertTrue("2' is selected" in out.getvalue())

    def test_007(self):
        """
            Test selecting groups with back
        """
        out = StringIO()
        term = HWITTerm(self.srcData["small"], stdout=out)
        term.onecmd("group 2")
        self.assertTrue("2' is selected" in out.getvalue())
        term.onecmd("group back")
        self.assertTrue("1' is selected" in out.getvalue())
        pos = out.tell()
        term.onecmd("group 2")
        self.assertTrue("2' is selected" in out.getvalue()[pos:])

    def test_008(self):
        """
            Test selecting groups with next
        """
        out = StringIO()
        term = HWITTerm(self.srcData["partial"], stdout=out)
        term.onecmd("group 4")
        self.assertTrue("4' is selected" in out.getvalue())
        pos = out.tell()
        term.onecmd("group next")
        # groups 1 and 2 are done, so it should wrap around to group 3
        self.assertTrue("3' is selected" in out.getvalue()[pos:])

class TestConsoleDetails(HWITSourceLoader):

    def test_001(self):
        """
            Test the reporting of details
        """
        out = StringIO()
        term = HWITTerm(self.srcData["partial"], stdout=out)
        term.onecmd("details")
        self.assertTrue("State:      0100" in out.getvalue())
        term.onecmd("group down")
        pos = out.tell()
        term.onecmd("details")
        self.assertTrue("State:      0110" in out.getvalue()[pos:])
        term.onecmd("group down")
        pos = out.tell()
        term.onecmd("details")
        self.assertTrue("State:      _1_1" in out.getvalue()[pos:])
        term.onecmd("group down")
        pos = out.tell()
        term.onecmd("details")
        self.assertTrue("State:      1_" in out.getvalue()[pos:])

class TestConsoleMisc(unittest.TestCase):

    def test_about(self):
        abt = os.path.join(package_path(hwit.core),"about.py")
        rv = subprocess.call(["python", abt], stdout=tempfile.mkstemp()[0])
        self.assertTrue(rv == 0)

    def test_settings(self):
        abt = os.path.join(package_path(hwit.core),"settings.py")
        rv = subprocess.call(["python", abt], stdout=tempfile.mkstemp()[0])
        self.assertTrue(rv == 0)

def load_tests(ldr=unittest.TestLoader(), suite=None, pttrn=None):
    testCases = (TestConsoleReport, TestConsoleGroup, TestConsoleDetails,
                TestConsoleMisc)
    rv = unittest.TestSuite()
    for i in testCases:
        tests = ldr.loadTestsFromTestCase(i)
        rv.addTests(tests)
    return rv

def run():
    unittest.TextTestRunner(verbosity=2).run(load_tests())
