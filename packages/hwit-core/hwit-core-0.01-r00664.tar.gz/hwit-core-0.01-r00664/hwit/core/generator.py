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
from StringIO import StringIO
from xmlrpclib import boolean
from hwit.core.model import Container, Section, Group, Field, Definition

__doc__ = """
Make a spreadsheet which describes your form
--------------------------------------------

The spreadsheet must have the following columns:

heading
    The HTML heading to precede the group. Every time this value
    changes from row to row, HWIT will generate a new group. A blank
    cell means the field belongs to the current group.
group_id
    The unique id to attach to the current group.
fillany
    A digit which specifies exactly how many fields in this group must
    be completed for the group to be considered valid. May be blank.
name
    The name of the field. In the case of questionnaires, this is the
    text of the question.
editable
    May be TRUE or FALSE. Specifies whether the field is editable by
    the user.
mandatory
    May be TRUE or FALSE. Specifies whether the field must be filled
    by the user.
validator
    May be blank, but if supplied, this is the name of one of the typer
    classes or methods in the module `hwitlib.checks`. This specifies
    how the content of the field is to be checked. The table below shows
    which ones to use. See the documentation for hwit.checks_
    for a complete explanation.
note
    A note to attach to the current group to explain its context.

Export the spreadsheet to a tab-separated values (TSV) file
-----------------------------------------------------------

Use your spreadsheet program to export the worksheet as a
tab-separated values (TSV) file.

"""

def str2bool(val):
    return val.lower() in ("y", "yes", "t", "true")

class Generator(object):

    _fields = (
    ("heading",str),
    ("group_id",str),
    ("fillany",int),
    ("field_name",str),
    ("editable",str2bool),
    ("mandatory",str2bool),
    ("validator",str),
    ("note",str)
    )

    def __init__(self):
        empty = StringIO()
        empty.name = None
        self._c = Container(empty)
        self._c._lines = []
        self._heading = ""
        self._groupId = ""
        self._fillany = None
        self._fldCount = 0

    @property
    def columns(self):
        return [i[0] for i in self._fields]

    @property
    def groups(self):
        return self._c.groups

    def process(self, row):
        fields = {}
        if len(row) and not row[0].startswith('#'):
            for (k,v),i in zip(self._fields, row):
                try:
                    val = v(i.strip())
                except ValueError:
                    val = None
                fields[k] = val
            heading = "<h2>%s</h2>\n" % fields["heading"] 
            if len(heading) > 10 and heading != self._heading:
                self._heading = heading
                self._c._lines.append(heading)
                sect = Section(len(self._c._lines)-1,0)
                sect.endPos = (len(self._c._lines)-1,len(heading))
                self._c._bodySections.append(sect)
                
            groupId = fields["group_id"] 
            if groupId and groupId != self._groupId:
                # new group
                self._fldCount = 0
                self._groupId = groupId
                gp = Group(self._groupId,0,0)
                self._fillany = fields["fillany"]
                gp.fillany = self._fillany
                gp.heading = self._heading
                gp.note = fields["note"] 
                self._c._bodySections.append(gp)
                self._c._groups[gp.id] = gp

            fld = Field(fields["field_name"],ordinal=self._fldCount)
            attributes = { "hwit_edit": str(fields["editable"]).lower(),
            "hwit_fill": str(fields["mandatory"]).lower() }
            if fields["validator"]:
                attributes["hwit_check"] = str(fields["validator"])
            fld._defns.append(Definition(0,0, attributes))
            self._fldCount += 1
            self._c._bodySections[-1]._fields[fld.name] = fld

    def tag(self, group, field):
        def byName(item):
            return getattr(item, "name", "") == field

        grp = [i for i in self._c.groups if i.id == group]
        if grp:
            flds = grp[0].get(byName)
            if flds and getattr(flds[0], "_defns", []):
                flds[0]._defns[0].content = "${%s_%s}" % (
                group.replace(' ','_').upper(),
                field.replace(' ','_').upper())
                return True
        return False

    def write(self, stream):
        self._c.write(stream)

