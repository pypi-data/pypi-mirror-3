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
from optparse import OptionParser
import glob
import shutil
import pdb
import traceback

USAGE = """
%prog is a tool which comes with the Python HWIT distribution

Use it to classify problematic HWIT files according to the
errors they produce. %prog will try to match each .hwit file with a
similarly named .txt file in search of code to provoke an error.

eg:
    cd tools
    triage.py ../ref                    create a triage tree

    triage.py -d ../ref/dodgy.hwit      debug a particular error  
"""

THIS_DIR = os.path.dirname(__file__)
DIR_DFLT = "triage"

sys.path.append(os.path.abspath(os.path.join(THIS_DIR,"..")))
import hwit.core
from hwit.core.model import Container

scrap = """
input = open(src, 'r')
contents = Container(input)
contents.read()
input.close()
"""

def get_path_from_traceback(root, excpt, msg):
    return os.path.join( root, excpt.__name__,
    msg.message.replace(' ','_').replace("'",""),
    hex(abs(hash(traceback.format_exc()))))

def run(src, case = ""):
    if not case:
        code = compile(scrap % {"source": "string"}, "<string>", "exec")
        eval(code, globals(), {"src": src})
    else:
        execfile(case, globals(), {"src": src})

def parser():
    rv = OptionParser(USAGE)
    rv.add_option("-d", "--debug", action="store_true",
    default=False, help="launch a debugger on every failure")
    rv.add_option("-v", "--verbose", action="store_true",
    default=False, help="save a traceback with every error")
    rv.add_option("-o", "--output", default=DIR_DFLT,
    help="name the directory in which to put the output [%s]" % DIR_DFLT)
    return rv

def main(opts, args):
    try:
        tgt = args[0]
        if not os.path.isfile(tgt):
            tgts = glob.glob(os.path.join(tgt,"*.hwit"))
        else:
            tgts = [tgt]
    except IndexError:
        return 2
    for fN in tgts:
        try:
            run(src = fN, case = "")
            sys.stdout.write("%s\n" % fN)
        except:
            e, m, tb = sys.exc_info()
            path = get_path_from_traceback(opts.output, e, m)
            if not os.path.isdir(path):
                os.makedirs(path)
            shutil.copy(fN, path)
            sys.stderr.write("error from %s\n" % fN)
            if opts.verbose:
                traceN = os.path.join(path,
                os.path.splitext(os.path.basename(fN))[0] + ".trc")
                trace = open(traceN, 'w')
                traceback.print_exc(file=trace)
                trace.close()
            if opts.debug:
                pdb.post_mortem(tb)

    return 0

if __name__ == "__main__":
    p = parser()
    opts, args = p.parse_args()
    rv = main(opts, args)
    sys.exit(rv)
