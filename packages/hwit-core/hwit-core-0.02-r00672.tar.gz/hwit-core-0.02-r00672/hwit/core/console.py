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
import os.path
import textwrap
from string import Template
import re
import uuid
import difflib

from cmd import Cmd

from hwit.core.model import Container
from hwit.core.context import PermissiveReadContext

class HWITTerm(Cmd):
    """
        Defines the interactive environment for editing HWIT containers.

        .. note::   The docstrings for methods of this class provide the
                    interactive help messages
    """
    prompt = "hwit> "

    def __init__(self, input = None, stdout = None):
        self._input = input
        self.intro = "\nStart by trying the 'report' or 'help' commands"
        self.contents = None
        self.filled = None
        self._prev = [0,0]
        self._index = [0,0]
        Cmd.__init__(self, stdout = stdout)
        self.postcmd(stop = False, line = "")

    def postcmd(self, stop, line):
        """
            ..  todo::
                Recalculate statistics after each command
        """
        if self.contents is None and self._input is not None:
            c = Container(self._input)
            with PermissiveReadContext(c) as self.contents:
                self.contents.read()
        return stop

    def do_load(self, line):
        """
            load <file>
                loads a container file
        """
        val = line.strip()
        self.contents = None
        if self._input is not None:
            self._input.close()
        try:
            self._input = open(val, 'r')
        except IOError:
            sys.stderr.write("unable to open file\n")
        return False

    def do_report(self, line):
        """
            report
                prints statistics on the current container
        """
        format = """\
        File:       ${FILE_NAME}
        Expires:    ${VALID_TO}
        State:      ${STATE}
        Rule:       ${RULE}
        Groups:     ${GROUPS}
        """
        if self.contents is None:
            self.stderr.write("no file has been loaded\n")
            return False
        rpt = Template(textwrap.dedent(format))
        self.stdout.write(rpt.substitute({
        "FILE_NAME": self._input.name,
        "VALID_TO":self.contents.meta.get("hwit_validto","no date set"),
        "STATE": self.contents.state,
        "RULE": self.contents.rule,
        "GROUPS": ", ".join([i.id for i in self.contents.groups])
        }))
        return False

    def do_group(self, line):
        """
            group <n>
                selects the nth group (starting at 1)
            group <id>
                selects the group by id
            group up
                selects the previous group
            group down
                selects the following group
            group back
                selects the most recently edited group
            group next
                selects the next uncompleted group
        """
        val = line.strip()
        if val.isdigit():
            if 0 < int(val) < len(self.contents.groups) + 1:
                self._prev = self._index
                self._index = [int(val) - 1,0]
            else:
                self.stdout.write("index '%s' is out of range\n" % val)
        elif val == "up":
            if self._index[0] > 0:
                self._prev = self._index
                self._index = [self._index[0]-1, 0]
        elif val == "down":
            if self._index[0] < len(self.contents.groups) - 1:
                self._prev = self._index
                self._index = [self._index[0]+1, 0]
        elif val == "back":
            self._prev, self._index = self._index, self._prev
        elif val == "next":
            groups = self.contents.groups
            n = self._index[0]
            while True:
                n = (n+1) % len(groups)
                checker = re.compile(groups[n].rule)
                if n == self._index[0]:
                    break
                elif checker.match(groups[n].state) is None:
                    self._prev = self._index
                    self._index = [n,0]
                    break
                
        if len(self.contents.groups) > 0:
            self.stdout.write("group '%s' is selected\n" %
            self.contents.groups[self._index[0]].id)
        else:
            self.stdout.write("the container has no groups\n")
        return False

    def do_details(self, line):
        """
            details
                prints all the information on this group
        """
        format = """\
        Group:      ${ID}
        State:      ${STATE}
        Fill any:   ${FILLANY}
        Note:       ${NOTE}

        ${CONTENTS}
        """
        dtls = Template(textwrap.dedent(format))
        tw = textwrap.TextWrapper(subsequent_indent=' '*12)
        gp = self.contents.groups[self._index[0]]
        self.stdout.write(dtls.substitute({
        "ID": gp.id, "NOTE": tw.fill(gp.note),
        "STATE": gp.state,
        "FILLANY": gp.fillany or '0',
        "CONTENTS": '\n'.join(
        ["%s\t%s" % (f.name,f.get() or '?') for f in gp.get()])
        })) 
        return False

    def do_todo(self, line):
        """
            todo
                summarises actions outstanding on this group
        """
        gp = self.contents.groups[self._index[0]]
        self.stdout.write("the 'todo' command is still to be implemented\n")
        # an idea
        print "rule ", gp.rule
        ruleRE = re.compile(gp.rule)
        mObj = ruleRE.match(gp.state)
        state = gp.state
        strategy = gp.state.replace('!','0').replace('_','1')
        print "state ", state
        print "strategy ", strategy
        if mObj is None:
            s = difflib.SequenceMatcher(None, state, strategy)
            for tag, i1, i2, j1, j2 in s.get_opcodes():
                self.stdout.write(
                "%7s state[%d:%d] (%s) strategy[%d:%d] (%s)\n" %
                (tag, i1, i2, state[i1:i2], j1, j2, strategy[j1:j2]))
 
        return False

    def do_fill(self, line):
        """
            fill
                begins interactively filling this group
        """
        gp = self.contents.groups[self._index[0]]
        for f in gp.get():
            resp = raw_input("%s [%s]:" % (f.name,f.get()))
            if resp:
                f.set(resp)
        return False

    def do_save(self, line):
        """
            save
                writes the container to a new file
            save <file>
                writes the container to a file you specify
        """
        nb = self.contents.meta.get("hwit_namebase")
        fN = self._input.name
        if nb is not None:
            nb = os.path.basename(nb)
            if nb != self.contents.meta.get("hwit_namebase"):
                # contains relative paths?
                self.stdout.write("warning: cannot use hwit_namebase\n")
            else:
                fN = "%s-%s.hwit" % (nb,uuid.uuid4().hex)
        try:
            fObj = open(fN,'w')
            self.contents.write(fObj)
        except IOError:
            self.stdout.write("couldn't save to %s\n" % fN)
        else:
            self.stdout.write("saved to file %s\n" % fN)
            fObj.close()
        return False

    def do_quit(self, line):
        """
            quit
                stops the program
        """
        if self._input is not None:
            self._input.close()
        return True

