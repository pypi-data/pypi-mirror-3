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
from string import printable
from StringIO import StringIO
import re
import time
from random import random, randint, choice, sample
from itertools import repeat, izip

USAGE = """
%prog is a tool which comes with the Python HWIT distribution

Use it to generate potentially problematic HWIT files

eg:
    cd tools
    happenstance.py -n100   create a fuzz corpus of 100 files
"""

THIS_DIR = os.path.dirname(__file__)
DIR_DFLT = "fuzz"
NR_DFLT = 6
WORDS = None

sys.path.append(os.path.abspath(os.path.join(THIS_DIR,"..")))
from hwit.core.generator import Generator

def load_words():
    global WORDS
    try:
        words = open("/usr/share/dict/words", 'r')
        WORDS = [i.strip().replace("'",'').lower() for i in words.readlines()]
        words.close()
    except:
        sys.stderr.write("couldn't load words.\n")

def get_word(fromWords = True):
    if WORDS and fromWords:
        return choice(WORDS) + time.strftime("-%M%S")
    else:
        return hex(int(random() * sys.maxint))[2:]

def generate(count):
    nameGen = mutate("fieldname", 0.1)
    for n in range(count):
        rv = StringIO()
        gen = Generator()
        tags = []
        for i in range(randint(1,12)):
            group = "group%02d" % i
            name = nameGen.next()
            data = [
            "heading%02d" % i,  # heading
            group,              # group_id
            "head",             # fillany
            name,               # name
            "TRUE",             # editable
            "head",             # mandatory
            "check",            # validator
            "note"              # note
            ]
            tags.append((group, name))
            try:
                gen.process(data)
            except StopIteration:
                break
        for gp, fld in tags:
            gen.tag(gp, fld)
        gen.write(rv)
        yield rv.getvalue()

def mutator(template):
    """ Generates a mutated version of the template string.
    Send the generator a float value to set the probability
    of any one character changing """
    def select(c):
        if random() > prob:
            return c
        else:
            return choice(printable)
    prob = 0.0
    while True:
        nProb = yield ''.join(map(select,template))
        if type(nProb) == type(0.0):
            prob = nProb

def mutate(template, prob = None):
    """ Returns a mutator generator which is primed and has
    its probability set to the passed parameter 'prob' """
    m = mutator(template)
    m.send(None)
    m.send(prob)
    return m

def padding(n):
    """ Returns a string of random characters, length n """
    return ''.join(sample(printable,n))

def parser():
    rv = OptionParser(USAGE)
    rv.add_option("-o", "--output", default=DIR_DFLT,
    help="name the directory in which to put the output [%s]" % DIR_DFLT)
    rv.add_option("-n", "--num", default=NR_DFLT, type="int",
    help="the number of files required [%s]" % NR_DFLT)
    return rv

def main(opts, args):
    load_words()
    if not os.path.isdir(opts.output):
        os.makedirs(opts.output)
    for t in generate(opts.num):
        chars = list(t)
        matches = list(re.finditer("<\S+(\s+([^=/>]+?)=(\S+?)\s*)+>",t))
        m = choice(matches)
        sys.stderr.write("mutating %s\n" % ''.join(chars[m.start():m.end()]))
        chars[m.start(3):m.end(3)] = mutate(m.group(3),0.1).next()
        chars[m.start(2):m.end(2)] = mutate(m.group(2),0.1).next()
        fP = os.path.join(opts.output,get_word() + ".hwit")
        fObj = open(fP, 'w')
        fObj.write(''.join(chars))
        fObj.close()
        sys.stderr.write("wrote to %s\n" % fP)
    return 0

def example():
    # Pattern: I want a string with a random length, and a
    # (slightly fuzzy) checksum:
    # 1. Generate an interesting length
    # 2. Generate a string to length with optional front and back
    # 3. Generate a checksum
    l = choice((24,32,256))
    template = "antimony"
    p = 'X' * (l - len(template))
    g = mutator(template)
    #sys.stdout.write("%s%s\n" % (p,g.send(None)))
    #sys.stdout.write("%s%s\n" % (p,g.send(0.8)))
    f = izip(
    repeat("CONNECT"),
    mutate("\nlogin: "), mutate("siegfried", 0.1),
    mutate("\npasscode: "), mutate("canine", 0.1))
    print ''.join(f.next())
    print ''.join(f.next())

if __name__ == "__main__":
    p = parser()
    opts, args = p.parse_args()
    rv = main(opts, args)
    sys.exit(rv)
