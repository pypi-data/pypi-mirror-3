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

import logging
import warnings
from string import Template
import textwrap
from xml.sax.saxutils import quoteattr, escape, unescape
import functools

import hwit.core.settings
from hwit.core.parser import Reader
from hwit.core.parser import isTrue
from hwit.core.parser import validators

def seq_tail_has_attr(name, attr):
    """
    Checks that an attribute has been defined on the latest item
    in a sequence. Best used on meeting an end-tag.
    """
    def wrapper(func):
        @functools.wraps(func)
        def inner(obj, pos, text):
            item = obj
            try:
                for i in name.split('.'):
                    item = getattr(item, i)
                if hasattr(item[-1],attr):
                    # Test has passed, so the method call is allowed
                    return func(obj, pos, text)
            except:
                pass
            # Test has failed. Handle according to context
            warnings.warn("%s undefined down to line %d, pos %d" % 
            (attr, pos[0], pos[1]), RuntimeWarning, stacklevel=2)
        return inner
    return wrapper

class Ordered(object):

    """
    Classes in the Data Model must able to sort themselves
    in order. Ordered is a superclass which provides this
    functionality.
    """

    def __init__(self, ordinal=0):
        """
        A ranking object must be passed its ordinal in its initialiser
        """
        self._ordinal = ordinal

    def __cmp__(self, other):
        return self.ordinal.__cmp__(other.ordinal)

    @property
    def ordinal(self):
        return self._ordinal

class Section(Ordered):

    def __init__(self, lineNo, charPos):
        """ expects zero-based line numbers and positions """
        self.startPos = (lineNo, charPos)
        self.endPos = (None,None)
        Ordered.__init__(self)

    def build(self, lines):
        """ reconstruct this section from the lines of the file """
        sL, sC, eL, eC = self.span
        eS = len(lines[eL]) + 1 - eC # last line surplus
        return ''.join(lines[sL:eL+1])[sC:-eS]

    @property
    def span(self):
        return self.startPos + self.endPos

class Definition(dict, Ordered):

    def __init__(self, lineNo, charPos, attrs, ordinal=0):
        self.startPos = (lineNo, charPos)
        self.endPos = (None,None)
        self.typ = "dd"
        self.update(attrs)
        self._data = ""
        Ordered.__init__(self, ordinal)

    def isEditable(self):
        return isTrue(self.get("hwit_edit","")) 

    def isMandatory(self):
        return isTrue(self.get("hwit_fill","")) 

    def set_data(self, val):
        self._data = escape(val)

    def get_data(self):
        return unescape(self._data)
    content = property(get_data, set_data)

    def parse(self, lines):
        """ reconstruct the contents from the lines of the file """
        sL, sC, eL, eC = self.startPos + self.endPos
        eS = len(lines[eL]) + 1 - eC # last line surplus
        openTagPlusData = ''.join(lines[sL:eL+1])[sC:-eS+1]
        self._data = openTagPlusData[openTagPlusData.index('>')+1:]

    def build(self, lines):
        """ reconstruct this element from contents """
        if not len(self):
            return "<%s>%s</%s>" % (self.typ, self._data, self.typ)
        return "<%s %s>%s</%s>" % (self.typ,
        ' '.join(sorted(['%s=%s' % (k,quoteattr(v)) for k,v in
        self.items()])) , self._data, self.typ)

class Field(Ordered):
    """
    A Field has a name and can contain a value. It applies checks to
    this value to determine validity.
    """
    
    _template = """\
    <dt>${NAME}</dt>
    ${DEFNS}"""

    def __init__(self, name="", ordinal=0):
        self._name = name
        self._defns = []
        self._checks = {}
        Ordered.__init__(self, ordinal)

    @property
    def name(self):
        """ The name of the Field """
        return self._name

    @property
    def checks(self):
        """
        A dictionary mapping strings to callable objects. Each pair
        defines a validator which is applied to the Field contents.
        """
        # This implementation is dumb.
        if not self._checks:
            self._checks.update(dict(
            validators([i.get("hwit_check","") for i in self._defns])))
        return self._checks

    def isEditable(self):
        return len(self._defns) and self._defns[0].isEditable()

    def isMandatory(self):
        return len(self._defns) and self._defns[0].isMandatory()

    def isValid(self):
        rv = True
        for val, data in [(i.get("hwit_check",""), i.content) for
        i in self._defns]:
            rv = rv and self.checks.get(val,str)(data)
        return rv

    def get(self):
        """ Return a copy of the Field content """
        # This implementation is lazy.
        editables = [i for i in self._defns if i.isEditable()]
        if not editables:
            return self._defns[0].content.strip()
        else:
            return editables[-1].content.strip()
    
    def set(self, val):
        """
        Set the Field value. This will return False if the
        Field is not editable, and True otherwise (even if 
        `val` is invalid content for the field).
        """
        # This implementation is lazy.
        editables = [i for i in self._defns if i.isEditable()]
        if not editables:
            return False
        else:
            editables[-1].content = val
            return True
    
    def build(self, lines):
        """ reconstruct this section from contents """
        bits = [i.build(lines) for i in self._defns]
        return Template(textwrap.dedent(self._template)).substitute(
        {"NAME": self.name, "DEFNS": '\n'.join(bits)})

class Group(Section):

    """
    A Group is a container for Field objects. It has an
    optional `note` which can store contextual information,
    and an `id` which is unique within the Container.
    """

    _template = """\
    <div id="${ID}" class="hwit_group"${FILL}>
    ${NOTE}<dl>
    ${FIELDS}
    </dl>
    </div>"""

    def __init__(self, id, lineNo, charPos):
        self.id = id
        self.note = ""
        self.heading = ""
        self._fields = {}
        Section.__init__(self,lineNo,charPos)

    @property
    def state(self):
        """
        A string which represents the state of the
        group. Each character corresponds to a field
        in the group. The status of each field is
        represented as follows:

        **!**
            *Broken*. The field content is invalid
        **1**
            *Filled*. The field has content which is valid
        **0**
            *Empty*. The field has no content, but this is
            permitted by its attributes
        **_**
            *Missing*. The field has no content, and a
            value is mandatory            
        """
        def fieldState(f):
            blank = f.get() == ""
            mandated = f.isMandatory()
            valid = f.isValid()
            if not blank:
                if not valid:
                    return '!'  # broken
                else:   
                    return '1'  # filled
            elif not mandated:
                return '0'      # empty
            else:
                return '_'      # missing
            
        return ''.join([fieldState(f) for f in self.get()])

    @property
    def rule(self):
        """
        A string which represents the validity rule for the
        group.

        The string is a regular expression. When applied
        to the `state` string, a match indicates that
        the group is valid.
        """
        if getattr(self, "fillany", False):
            return "((?:0*10*){%s})" % self.fillany
        else:
            return "([10]{%d})" % len(self._fields)

    def get(self, select=None):
        """
        Return a sequence of fields satisfying the predicate `select`.
        `Select` must be a callable returning True for qualifying
        fields. If not supplied, all fields are returned.
        """
        def selected(item):
            return True
        if select == None:
            select = selected
        return sorted([i for i in self._fields.values() if select(i)])

    def build(self, lines):
        """ reconstruct this section from contents """

        def byOrdinal(item):
            return getattr(item,"ordinal",0)

        fields = sorted(self._fields.itervalues(), key=byOrdinal)
        bits = [i.build(lines) for i in fields]
        fillStr = "" if self.fillany is None else (' hwit_fillany="%s" '
        % self.fillany)
        return Template(textwrap.dedent(self._template)).substitute(
        {"ID": self.id, "FILL": fillStr, 
        "NOTE": ("<p>%s</p>\n" % self.note if self.note else ""),
        "FIELDS": '\n'.join(bits)})

class Container(object):
    """
    A Container is the top level object representing an entire
    HWIT file.

    Because of the close coupling between class and file format,
    most methods of Container are concerned with parsing. These
    are used by :class:`hwit.core.parser.Reader`, and are not
    explicitly documented here.

    Access to internal objects is provided through properties of
    the Container class.

    """

    _keywords = set(["hwit_check", "hwit_edit", "hwit_fill",
    "hwit_fillany", "hwit_group"])

    _template = """\
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML+RDFa 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    ${META}
    ${TITLE}
    <style type="text/css">
    ${STYLING}</style>
    </head>
    <body>${BODY}</body>
    </html>"""

    def __init__(self, stream):
        """
        Create a new Container by passing a Python file
        object (read mode) to the constructor
        """
        self._log = logging.getLogger("container")
        self._rdr = Reader(self, stream.name)
        # Keep in order to reconstruct template
        self._lines = stream.readlines()
        self._title = ""
        self._heading = ""
        self._bodySections = []
        self._meta = {}
        self._groups = {}
        self._latestField = None

    def _fmt_meta(self):
        return "\n".join(sorted(['<meta name="%s" content="%s" />' %
        (k,v) for k,v in self._meta.items()]))

    def _fmt_title(self):
        return "<title>%s</title>" % self._title

    def _fmt_body(self):
        return "%s\n" % '\n'.join(
        [s.build(self._lines)for s in self._bodySections])

    @property
    def title(self):
        """ The title of the HWIT container """
        return self._title

    @property
    def meta(self):
        """ A dictionary of container metadata"""
        return self._meta

    @property
    def groups(self):
        """ A sequence of all the Group objects"""
        return sorted(self._groups.values())

    @property
    def state(self):
        """
        A string representing the overall state of
        the container. This is a concatenation of
        the `state` strings for all groups, each one
        separated by a space
        """
        return ' '.join([g.state for g in self.groups])

    @property
    def rule(self):
        """
        A string which is a rule by which the
        validity of the entire Container may be
        tested. This is the concatenation of the
        `rule` strings for all groups, each one
        separated by a space
        """
        return ' '.join([g.rule for g in self.groups])

    def read(self):
        """
        Read the Container's stream, until the object
        is configured
        """
        self._rdr.feed(''.join(self._lines))

    def write(self, stream):
        """
        Serialise the Container to HWIT file format.
        `stream` must be a file object opened in write
        mode.
        """
        t = Template(textwrap.dedent(self._template))
        d = {
        "META": self._fmt_meta(),
        "TITLE": self._fmt_title(),
        "STYLING": hwit.core.settings.style,
        "BODY": self._fmt_body()
        }
        stream.write(t.substitute(d))

    def on_doctype(self, pos):
        pass

    def on_meta_start(self, attrs, pos):
        map = dict(attrs)
        if "name" in map and "content" in map:
            self._meta[map["name"]] = map["content"]

    def on_meta_end(self, pos, text):
        pass
        
    def on_title_start(self, attrs, pos):
        self._rdr.requestData(self.on_title)

    def on_title(self, data):
        self._title = data
        
    def on_title_end(self, pos, text):
        self._rdr.requestData(None)

    def on_body_start(self, attrs, pos, text):
        s = Section(pos[0]-1, pos[1]+len(text))
        self._bodySections.append(s)
        self._rdr.requestEnd(self.on_any_end)
    
    def on_body_end(self, pos, text):
        self.on_any_end(pos, text)
        # Stop tracking end tags
        self._rdr.requestEnd(None)
        self._log.debug(self._bodySections)
        
    def on_group_start(self, attrs, pos, text):
        """
        ..  todo::
            *   handle no id
            *   handle duplicate id

        """
        self._bodySections[-1].endPos = (pos[0]-1, pos[1])
        # Start a new group
        attrMap = dict(attrs)
        id = attrMap["id"]
        g = Group(id, pos[0]-1, pos[1])
        # fillany syntax: m m, m,n ,n
        fillTest = attrMap.get("hwit_fillany","").split(',')
        g.fillany = ','.join(fillTest) if (len(fillTest) < 3 and
        all([i.isdigit() for i in fillTest])) else None
        self._bodySections.append(g)
        self._rdr.requestEnd(None)
    
    @seq_tail_has_attr("_bodySections","id")
    def on_group_end(self, pos, text):
        self.on_any_end(pos, text)
        g = self._bodySections[-1]
        g._ordinal = len(self._bodySections)
        g.heading = self._heading
        self._groups[g.id] = g
        self._rdr.requestEnd(self.on_any_end)
        #TODO: Assume a section will follow
        
    def on_element_start(self, tag, attrs, pos, text):
        if len(self._bodySections):
            thisSect = self._bodySections[-1]
            if isinstance(thisSect, Group):
                if thisSect is self._groups.get(
                getattr(thisSect,"id",""),None):
                    # The preceding group has been fully parsed
                    # so we need a section for this element
                    s = Section(pos[0]-1, pos[1])
                    self._bodySections.append(s)
                    self._rdr.requestEnd(self.on_any_end)
                elif tag == "p":
                    # This is a note inside a group
                    self._rdr.requestData(self.on_note)

    def on_note(self, data):
        thisSect = self._bodySections[-1]
        if isinstance(thisSect, Group):
            thisSect.note = data
        self._rdr.requestData(None)

    def on_heading(self, data):
        self._heading = data
        self._rdr.requestData(None)

    def on_element_end(self, tag, pos, text):
        pass

    def on_list_start(self, attrs, pos, text):
        thisSect = self._bodySections[-1]
        if isinstance(thisSect, Group):
            thisSect.listStartPos = (pos[0]-1, pos[1])

    @seq_tail_has_attr("_bodySections","ordinal")
    def on_list_end(self, pos, text):
        thisSect = self._bodySections[-1]
        if isinstance(thisSect, Group):
            thisSect.listEndPos = (pos[0]-1, pos[1])

    def on_term_start(self, attrs, pos, text):
        thisSect = self._bodySections[-1]
        if isinstance(thisSect, Group):
            self._rdr.requestData(self.on_term)

    def on_term(self, data):
        thisSect = self._bodySections[-1]
        rank = len(thisSect._fields)
        thisSect._fields[data] = Field(name=data,ordinal=rank)
        self._latestField = thisSect._fields[data]
        assert(len(self._latestField._defns) == 0)
        self._rdr.requestData(None)

    def on_term_end(self, pos, text):
        pass

    def on_defn_start(self, attrs, pos, text):
        thisSect = self._bodySections[-1]
        if isinstance(thisSect, Group):
            defn = Definition(pos[0]-1, pos[1], attrs)
            self._latestField._defns.append(defn)
            self._rdr.requestData(self.on_defn)

    def on_defn(self, data):
        self._rdr.requestData(None)

    @seq_tail_has_attr("_latestField._defns","endPos")
    def on_defn_end(self, pos, text):
        self._latestField._defns[-1].endPos = (pos[0]-1, pos[1])
        self._latestField._defns[-1].parse(self._lines)

    @seq_tail_has_attr("_bodySections","endPos")
    def on_any_end(self, pos, text):
        self._bodySections[-1].endPos = (pos[0]-1, pos[1])
