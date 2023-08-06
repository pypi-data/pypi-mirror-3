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

USAGE = """
%prog is a tool which comes with the Python HWIT distribution

Use it to visualise a HWIT dataset

eg:
    %prog <directory>
"""

import os
import sys
from optparse import OptionParser
import logging
import glob
from math import sqrt, ceil
from string import Template
from itertools import izip, chain, repeat

THIS_DIR = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(THIS_DIR,"..")))
from hwit.core.model import Container

def limits(data):
    maxGLen = 0
    vals = []
    for fN, c in data.items():
        for g in c.groups:
            for n, f in enumerate(g.get()):
                vals.append(int(f.get()))
            maxGLen = max(maxGLen, n)
    vals.sort()
    cols = sqrt(len(data))
    rows = ceil(len(data)/cols)
    return int(rows), int(cols), maxGLen+1, vals[len(vals)/2]

def heatmap(c, nFields, dflt):
    for nG, g in enumerate(c.groups):
        for nF, f in izip(range(nFields), chain(g.get(), repeat(None))):
            yield "%d\t%d\t%s\n" % (
            nG + 1, nF + 1, dflt if f is None else f.get())
        yield "\n"

gPlotHdr = """
# multiple heatmap for gnuplot written by cluster.py from the HeWIT project
set xrange [ 0 : * ]
set xtics border in scale 0,0 nomirror norotate offset character 0, 0, 0
set noxtics
set yrange [ * : * ] reverse
set ytics border in scale 0,0 nomirror norotate offset character 0, 0, 0
set noytics
set cbrange [ -3 : 3 ]
set palette rgbformulae -7, 2, -7
set nocbtics
set multiplot title "${title}" layout ${rows},${cols}
""".lstrip()

def parser():
    rv = OptionParser(USAGE)
    rv.add_option("-v", "--verbose", action="store_true",
    default=False, help="increase the verbosity of log messages")
    return rv

def main(opts, args):
    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("cluster")
    try:
        dP = os.path.abspath(args[0])
    except IndexError:
        return 2

    data = {}
    for fP in glob.glob(os.path.join(dP, "*.hwit")):
        log.debug("scanning %s ..." % fP)
        fObj = open(fP, 'r')
        c = Container(fObj)
        c.read()
        data[fP] = c

    rows, cols, groupLen, nullVal = limits(data)
    sys.stdout.write(
    Template(gPlotHdr).substitute(
    {"title":"Visualisation of %s" % dP, "rows":rows, "cols":cols})
    )
    for n, (fP, c) in enumerate(data.items()):
        dFP = os.path.join(
        dP, os.path.splitext(os.path.basename(fP))[0]
         + ".dat")
        log.debug("creating %s ..." % dFP)
        dFObj = open(dFP, 'w')
        dFObj.writelines(heatmap(c,groupLen,nullVal))
        dFObj.close()
        dFN = os.path.basename(dFP)
        dN = os.path.basename(dP)
        sys.stdout.write("set title \"%s_%04d\"\n"
        "plot '%s' using 2:1:3 with image notitle\n"
        % (dN,n+1,dFN))
    
    sys.stdout.write("unset multiplot\n")
    return 0

if __name__ == "__main__":
    p = parser()
    opts, args = p.parse_args()
    rv = main(opts, args)
    if rv == 2: p.print_usage()
    sys.exit(rv)
