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

__doc__ = """
`hwit-console` takes command line options to control its operation.
To see what options are available, do::

    hwit-console -h

Currently, the following is implemented:
    *   `Reading a form from the command line`_
    *   `Making your own form`_
    *   Interactive text console client

"""

import csv
import logging
import os.path
from optparse import OptionParser
import sys

from hwit.core.console import HWITTerm
from hwit.core.generator import Generator

USAGE = """
%prog is an application which comes with the Python HWIT library

Use it to manipulate HWIT files

examples:
    %prog container.hwit                opens the form in a text console
    %prog --tag=gp:fld container.hwit   prints the contents of a field
    %prog -g --tag=gp:fld < my_template.tsv
                                        generates a new HWIT form and
                                        creates a template tag in field
                                        'fld' of group 'gp'
""" 

def parser():
    rv = OptionParser(USAGE)
    rv.add_option("-g", "--generate", action="store_true",
    default=False, help="generate a new HWIT form")
    rv.add_option("--tag", action="append", default=[],
    help="create a tag for group:field (with -g option)")
    rv.add_option("-v", "--verbose", action="store_true",
    default=False, help="increase the verbosity of log messages")
    rv.add_option("--version", action="store_true",
    default=False, help="print the version number of this program")
    return rv

def main(opts, args):

    if opts.version:       
        from hwit.core.about import version_info
        sys.stdout.write(
        "HWIT editor 0.%d (beta)\n" % version_info["revno"])
        return 0

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
 
    if opts.generate:
        gen = Generator()
        rdr = csv.reader(sys.stdin, delimiter = '\t')
        sys.stderr.write("expecting configuration on standard input...\n")
        sys.stderr.write("%s\n" % " <tab> ".join(gen.columns))
        while True:
            try:
                gen.process(rdr.next())
            except StopIteration:
                break
        for i in opts.tag:
            gp, fld = i.split(':')
            sys.stderr.write("adding tag %s" % i)
            if not gen.tag(gp, fld):
                sys.stderr.write(" failed\n")
            else:
                sys.stderr.write("\n")
        gen.write(sys.stdout)
        return 0

    if not args:
        sys.stderr.write("arguments or options are required\n")
        return 2

    wrtr = csv.writer(sys.stdout, delimiter = '\t')
    for fN in args:
        try:
            input_ = open(fN, 'r')
        except IOError:
            sys.stderr.write("file %s cannot be found\n" % fN)
            return 2
        term = HWITTerm(input_)

        if not opts.tag:
            term.cmdloop()
        else:
            term.postcmd(False, "")
            for tag in opts.tag:
                try:
                    gp, fld = tag.split(':')
                except ValueError:
                    continue
                else:
                    wrtr.writerows(
                        [(os.path.abspath(fN), gp, fld, f.get())
                        for g in term.contents.groups if g.id == gp
                        for f in g.get() if f.name == fld]
                    )
    return 0
        
def run():
    p = parser()
    opts, args = p.parse_args()
    rv = main(opts, args)
    if rv == 2:
        p.print_usage()
    sys.exit(rv)

if __name__ == "__main__":
    run()
