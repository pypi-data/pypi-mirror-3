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
import unittest
import datetime
import difflib

from StringIO import StringIO

from hwit.core.test import HWITSourceLoader
from hwit.core.model import Container

class TestHWITContents(HWITSourceLoader):

    """
    TODO: Iñtërnâtiônàlizætiøn
    """
    def test_001(self):
        """
            Test that we can read a blank container, and that it contains
            no groups, but has metadata
        """
        c = Container(self.srcData["blank"])
        c.read()
        self.assertEqual(c.state, "")
        # check number of elements
        self.assertEqual(len(c.meta),4)
        self.assertEqual(len(c.groups),0)
        # check access to meta data
        self.assertTrue(c.meta.get("hwit_originator")=="hwit.core")
        self.assertTrue(c.meta.get("hwit_validto")=="2010-06-28")
        self.assertTrue(c.meta.get("hwit_keywords")=="test, blank")

    def test_002(self):
        """
            Test that we can write out a blank container 
        """
        c = Container(self.srcData["blank"])
        c.read()
        self.assertEqual(c.state, "")
        s = StringIO()
        c.write(s)
        # Get the magic number with `wc -m ref/blank.hwit`
        self.assertEqual(len(s.getvalue())+1, 2168)

    def test_003(self):
        """
            Test that we can read an empty container, and that it contains
            no groups, but has metadata
        """
        c = Container(self.srcData["empty"])
        c.read()
        self.assertEqual(c.state, "")
        # check number of elements
        self.assertEqual(len(c.meta),3)
        self.assertEqual(len(c.groups),0)
        # check access to meta data
        self.assertTrue(c.meta.get("hwit_originator")=="hwit.core")
        self.assertTrue(c.meta.get("hwit_validto")=="2010-06-30")
        self.assertTrue(c.meta.get("hwit_keywords")=="test, empty")

    def test_004(self):
        """
            Test that we can write out an empty container 
        """
        c = Container(self.srcData["empty"])
        c.read()
        self.assertEqual(c.state, "")
        s = StringIO()
        c.write(s)
        # Get the magic number with `wc -m ref/empty.hwit`
        self.assertEqual(len(s.getvalue())+1, 2203)

    def test_005(self):
        """
            Test that we can read a basic container, which contains
            a group, and has metadata
        """
        c = Container(self.srcData["basic"])
        c.read()
        self.assertEqual(c.state, "_")
        # check number of elements
        self.assertEqual(len(c.meta),5)
        self.assertEqual(len(c.groups),1)
        # check access to meta data
        self.assertTrue(c.meta.get("hwit_originator")=="hwit.core")
        self.assertTrue(c.meta.get("hwit_validto")=="2010-06-30")
        self.assertTrue(c.meta.get("hwit_serial")=="0123456789")
        self.assertTrue(c.meta.get("hwit_keywords")=="test, basic")

    def test_006(self):
        """
            Test that we can write out a basic container 
        """
        c = Container(self.srcData["basic"])
        c.read()
        self.assertEqual(c.state, "_")
        s = StringIO()
        c.write(s)
        # Get the magic number with `wc -m ref/basic.hwit`
        self.assertEqual(len(s.getvalue())+1, 2578)

    def test_007(self):
        """
            Test that we can read a small container, which contains
            groups and interleaved text, and has metadata
        """
        c = Container(self.srcData["small"])
        c.read()
        self.assertEqual(c.state, "_ _00")
        # check number of elements
        self.assertEqual(len(c.meta),4)
        self.assertEqual(len(c.groups),2)
        # check access to meta data
        self.assertTrue(c.meta.get("hwit_originator")=="hwit.core")
        self.assertTrue(c.meta.get("hwit_validto")=="2010-07-01")
        self.assertTrue(c.meta.get("hwit_keywords")=="test, small")

    def test_008(self):
        """
            Test that we can write out a small container 
        """
        c = Container(self.srcData["small"])
        c.read()
        self.assertEqual(c.state, "_ _00")
        s = StringIO()
        c.write(s)
        # There have been whitespace differences. Best effort:
        self.srcData["small"].seek(0)
        a = self.srcData["small"].read()
        b = s.getvalue()
        m = difflib.SequenceMatcher( None, a, b)
        self.assertFalse( m.ratio() < 0.988 )
        # Get the magic number with `wc -m ref/small.hwit`
        fudge = 1
        self.assertEqual(len(s.getvalue())+ 1 + fudge, 3126)

    def test_009(self):
        """
            Test that we can write multiple definitions from a field
        """
        c = Container(self.srcData["partial"])
        c.read()
        self.assertEqual(c.state, "0100 0110 _1_1_ 1_")
        s = StringIO()
        c.write(s)
        # There have been whitespace differences. Best effort:
        self.srcData["partial"].seek(0)
        a = self.srcData["partial"].read()
        b = s.getvalue()
        m = difflib.SequenceMatcher( None, a, b)
        self.assertFalse( m.ratio() < 0.988 )
        # Get the magic number with `wc -m ref/hewit-partial.hwit`
        fudge = 3
        self.assertEqual(len(s.getvalue())+1 + fudge, 4498)

class TestHWITEdit(HWITSourceLoader):
    
    def test_001(self):
        """
            Test that we can edit a basic container, which contains
            a group, and has metadata
        """
        c = Container(self.srcData["basic"])
        c.read()
        self.assertEqual(c.state, "_")
        f = c.groups[0].get()[0]
        self.assertEqual(len(f._defns),1)
        self.assertTrue(f.isEditable())
        self.assertTrue(f.isMandatory())
        self.assertFalse(f.isValid())
        self.assertTrue(all([callable(i) for i in f.checks.values()]))
        self.assertTrue(
        "hwit.checks.common.datetimetyper.isISOTime" in f.checks)
        val = datetime.datetime.now().isoformat()
        self.assertTrue(f.set(val[11:19]))
        self.assertTrue(f.isValid())
        s = StringIO()
        c.write(s)
        self.assertFalse("&nbsp" in s.getvalue())

class TestHWITValidation(HWITSourceLoader):
    
    def test_001(self):
        """
            Test that we can read a small container, which contains
            groups and interleaved text, and has validators, etc
        """
        c = Container(self.srcData["small"])
        c.read()
        self.assertEqual(c.state, "_ _00")
        # There are two groups
        self.assertEqual(len(c.groups),2)
        # The first group has one field ( a date )
        self.assertEqual(len(c.groups[0].get()),1)
        self.assertEqual(c.groups[0].id,"bag_001")
        self.assertEqual(c.groups[0].heading,
        "For completion by staff")
        for n,fUT in enumerate(c.groups[0].get()):
            self.assertEqual(fUT.name,"Date")
            self.assertTrue(fUT._defns[0].get("hwit_fill",False))
            self.assertTrue(fUT._defns[0].get("hwit_edit",False))
            self.assertEqual(fUT._defns[0].get("hwit_check",""),
            "hwit.checks.common.timetyper.isISOTime")
        
        # The second group has three fields
        self.assertEqual(len(c.groups[1].get()),3)
        self.assertEqual(c.groups[1].id,"bag_002")
        self.assertEqual(c.groups[1].heading,
        "For completion by pupil")
        for n,fUT in enumerate(c.groups[1].get()):
            if n == 0:
                self.assertEqual(fUT.name,"Name")
                self.assertTrue(fUT._defns[0].get("hwit_fill",False))
                self.assertTrue(fUT._defns[0].get("hwit_edit",False))
                self.assertEqual(
                fUT._defns[0].get("hwit_check","not_there") ,"not_there")
            elif n == 1:
                self.assertFalse(fUT._defns[0].get("hwit_fill",False))
                self.assertTrue(fUT._defns[0].get("hwit_edit",False))
                self.assertEqual(fUT._defns[0].get("hwit_check",""),
                "hwit.checks.common.emailtyper.isAddr")
            elif n == 2:
                self.assertFalse(fUT._defns[0].get("hwit_fill",False))
                self.assertTrue(fUT._defns[0].get("hwit_edit",False))
                self.assertFalse(fUT._defns[0].get("hwit_check",False))

    def test_002(self):
        """
            Test that we can read a container, and ignore imperfectly
            defined validators. Also interact with non-editable fields
        """
        c = Container(self.srcData["risky"])
        c.read()
        self.assertTrue("risk" in c.title)
        self.assertTrue(c.rule)
        self.assertFalse(c.groups[0].get()[0].checks)
        self.assertFalse(c.groups[0].get()[0].set("non-editable field"))
        self.assertFalse(c.groups[0].get()[0].get())
        self.assertTrue('!' in c.groups[0].state)

def load_tests(ldr=unittest.TestLoader(), suite=None, pttrn=None):
    testCases = (TestHWITContents, TestHWITEdit, TestHWITValidation)
    rv = unittest.TestSuite()
    for i in testCases:
        tests = ldr.loadTestsFromTestCase(i)
        rv.addTests(tests)
    return rv

def run():
    unittest.TextTestRunner(verbosity=2).run(load_tests())
