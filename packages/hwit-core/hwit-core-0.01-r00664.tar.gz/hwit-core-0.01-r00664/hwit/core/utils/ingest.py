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

Use it to analyse HWIT files

eg:
    %prog <directory>
"""

import os
import sys
from optparse import OptionParser
import logging
import glob
import sqlite3

THIS_DIR = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(THIS_DIR,"..")))
from hwit.core.model import Container

def register(fN, c, survey):
    log = logging.getLogger("register")
    survey.setdefault(c.rule, []).append((fN, c))
    
def archetype(survey):
    log = logging.getLogger("archetype")
    results = [(len(v),k) for k, v in survey.iteritems()]
    log.info("found %d rule variant(s)" % len(results))
    return max(results)[1]

class ConsistencyError(Exception):
    pass

def enforce(seq):
    log = logging.getLogger("enforce")
    groupInfo = {}
    for fN, c in seq:
        for n, g in enumerate(c.groups):
            if groupInfo.setdefault(n, (g.id, g.note)) != (g.id, g.note):
                log.error("%s, group %d (%s) has inconsistent data"
                % (fN, n+1, g.id))
                raise ConsistencyError
    log.info("no inconsistencies detected")

def create(cursor):
    sql = """
    drop table if exists file;
    drop table if exists section;
    drop table if exists field;

    create table file
    (
    name text not null,
    key text,
    value text,
    unique(name, key, value) on conflict ignore
    );

    create table section
    (
    file_name text not null,        -- local file name
    id text not null,
    nr integer not null,
    state text not null,
    note text,
    primary key (file_name, id) on conflict ignore
    );

    create table field
    (
    file_name text not null,        -- local file name
    section_nr integer not null,    -- foreign key to section
    nr integer not null,
    name text,
    value,
    unique (file_name, section_nr, nr)
    );
    """
    cursor.executescript(sql)

def populate(cursor, seq):
    fields = []
    fileSql = "insert into file values(?,?,?)"
    sectionSql = "insert into section values(?,?,?,?,?)"
    fieldSql = "insert into field values(?,?,?,?,?)"
    for cN, (fP, c) in enumerate(seq):
        fN = os.path.basename(fP)
        for k,v in c.meta.items():
            cursor.execute(fileSql, (fN,k,v))
        for sN, g in enumerate(c.groups):
            cursor.execute(sectionSql, (fN, g.id, sN, g.state, g.note))
            for n, f in enumerate(g.get()):
                fields.append((os.path.basename(fP), sN, n, f.name, f.get()))
    cursor.executemany(fieldSql,fields)

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
    log = logging.getLogger("ingest")
    try:
        dP = os.path.abspath(args[0])
    except IndexError:
        return 2

    survey = {}
    for fP in glob.glob(os.path.join(dP, "*.hwit")):
        log.info("scanning %s ..." % fP)
        fObj = open(fP, 'r')
        c = Container(fObj)
        c.read()
        register(fObj.name, c, survey)
        fObj.close()
    
    rule = archetype(survey)
    try:
        enforce(survey[rule])
    except ConsistencyError:
        return 1

    dbP = os.path.join(dP, os.path.basename(dP) + ".sqlite")
    log.info("creating %s ..." % dbP)
    conn = sqlite3.connect(dbP)
    cursor = conn.cursor()
    create(cursor)

    conn.commit()
    populate(cursor, survey[rule])
    conn.commit()
    return 0

if __name__ == "__main__":
    p = parser()
    opts, args = p.parse_args()
    rv = main(opts, args)
    if rv == 2: p.print_usage()
    sys.exit(rv)
