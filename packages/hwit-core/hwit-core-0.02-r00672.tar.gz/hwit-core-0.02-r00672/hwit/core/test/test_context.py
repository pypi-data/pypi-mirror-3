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
from __future__ import with_statement

import sys
import unittest
import datetime

from StringIO import StringIO

from hwit.core.test import HWITSourceLoader
from hwit.core.model import Container
from hwit.core.context import StrictReadContext
from hwit.core.context import PermissiveReadContext

class TestStrictReadContext(HWITSourceLoader):

    def test_001(self):
        """
            Test that we can read a basic container via a context.
            Attribute access is deferred to container.
        """
        c = Container(self.srcData["basic"])
        with StrictReadContext(c) as doc:
            doc.read()
            self.assertEqual(doc.state, "_")
            f = doc.groups[0].get()[0]
            self.assertEqual(len(f._defns),1)
            self.assertTrue(f.isEditable())
            self.assertTrue(f.isMandatory())
            self.assertFalse(f.isValid())
            self.assertTrue(all([callable(i) for i in f.checks.values()]))
            self.assertTrue(
            "hwit.checks.common.datetimetyper.isISOTime" in f.checks)
            val = datetime.datetime.now().isoformat()[:19]
            self.assertTrue(f.set(val[11:19]))
            self.assertTrue(f.isValid())
            s = StringIO()
            doc.write(s)
            self.assertFalse("&nbsp" in s.getvalue())

    def test_002(self):
        """
            Contains forbidden 'script' tag
        """
        c = Container(self.srcData["risky"])
        with StrictReadContext(c) as doc:
            self.assertRaises(Exception, doc.read)

    def test_003(self):
        """
            happenstance made this one.
            triage: AttributeError/NoneType_object_has_no_attribute__defns
        """
        c = Container(self.srcData["osvaldo-3915"])
        with StrictReadContext(c) as doc:
            self.assertRaises(Exception, doc.read)

    def test_004(self):
        """
            happenstance made this one.
            triage: AttributeError/Section_object_has_no_attribute_id
        """
        c = Container(self.srcData["underskirts-3915"])
        with StrictReadContext(c) as doc:
            self.assertRaises(Exception, doc.read)

    def test_005(self):
        """
            happenstance made this one.
            triage: HTMLParseError
        """
        c = Container(self.srcData["corrugation-3003"])
        with StrictReadContext(c) as doc:
            self.assertRaises(Exception, doc.read)

class TestPermissiveReadContext(HWITSourceLoader):
    
    def test_001(self):
        """
            Test that we can read a basic container via a context.
            Attribute access is deferred to container.
        """
        c = Container(self.srcData["basic"])
        with PermissiveReadContext(c) as doc:
            doc.read()
            self.assertEqual(doc.state, "_")
            f = doc.groups[0].get()[0]
            self.assertEqual(len(f._defns),1)
            self.assertTrue(f.isEditable())
            self.assertTrue(f.isMandatory())
            self.assertFalse(f.isValid())
            self.assertTrue(all([callable(i) for i in f.checks.values()]))
            self.assertTrue(
            "hwit.checks.common.timetyper.isISOTime" in f.checks)
            self.assertTrue(f.set(datetime.datetime.now().isoformat()[:19]))
            self.assertTrue(f.isValid())
            s = StringIO()
            doc.write(s)
            self.assertFalse("&nbsp" in s.getvalue())

    def test_002(self):
        """
            Contains forbidden 'script' tag
        """
        c = Container(self.srcData["risky"])
        with PermissiveReadContext(c) as doc:
            doc.read()
            s = StringIO()
            doc.write(s)

    def test_003(self):
        """
            happenstance made this one.
            triage: AttributeError/NoneType_object_has_no_attribute__defns
        """
        c = Container(self.srcData["osvaldo-3915"])
        with PermissiveReadContext(c) as doc:
            doc.read()
            s = StringIO()
            doc.write(s)

    def test_004(self):
        """
            happenstance made this one.
            triage: AttributeError/Section_object_has_no_attribute_id
        """
        c = Container(self.srcData["underskirts-3915"])
        with PermissiveReadContext(c) as doc:
            doc.read()
            s = StringIO()
            doc.write(s)

    def test_005(self):
        """
            happenstance made this one.
            triage: HTMLParseError
        """
        c = Container(self.srcData["corrugation-3003"])
        with PermissiveReadContext(c) as doc:
            doc.read()
            s = StringIO()
            doc.write(s)

def load_tests(ldr=unittest.TestLoader(), suite=None, pttrn=None):
    testCases = (TestStrictReadContext, TestPermissiveReadContext)
    rv = unittest.TestSuite()
    for i in testCases:
        tests = ldr.loadTestsFromTestCase(i)
        rv.addTests(tests)
    return rv

def run():
    unittest.TextTestRunner(verbosity=2).run(load_tests())
