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
The module allows clients of the hwit.core library to use it in their own
choice of *context*. For example, a GUI editor of HWIT containers may
want to be as permissive as it can in loading files which may contain
formatting errors. There is a context for that.

A HWIT validating program or a security scanner may want to be as strict
as possible in loading containers, forbidding any minor inconsistency.
There is a context for that.
"""

import warnings

class StrictReadContext(object):
    """
    This context enforces the syntax rules of HWIT rigorously, and
    may throw any of the following exceptions:

    * `SyntaxWarning`
    * `RuntimeWarning`
    * `HTMLParser.HTMLParseError`

    It should be used when a HWIT file comes from an untrusted source.
    The errors should be explicity handled. Here is a typical example::

        try:
            with StrictReadContext(container) as doc:
                doc.read()
        except (RuntimeWarning, SyntaxWarning), w:
            error = w.message
        except HTMLParseError, e:
            error = "%s line %d, pos %d" % (e.msg, e.lineno, e.offset)

    """
    
    def __init__(self, container):
        self._container = container

    def __enter__(self):
        warnings.resetwarnings()
        warnings.simplefilter("error", SyntaxWarning)
        warnings.simplefilter("error", RuntimeWarning)
        return self._container

    def __exit__(self, exc_type, exc_val, exc_tb):
        # revive any exceptions
        warnings.resetwarnings()
        warnings.simplefilter("always")
        return False

class PermissiveReadContext(StrictReadContext):
    """
    This context will tolerate errors in HWIT files. It's appropriate
    when you want to make a *best effort* to read the data::

        with PermissiveReadContext(container) as doc:
            doc.read()
    """
    
    def __init__(self, container):
        StrictReadContext.__init__(self, container)

    def __enter__(self):
        warnings.resetwarnings()
        warnings.simplefilter("ignore", SyntaxWarning)
        warnings.simplefilter("ignore", RuntimeWarning)
        return self._container

    def __exit__(self, exc_type, exc_val, exc_tb):
        # suppress any exceptions
        warnings.resetwarnings()
        warnings.simplefilter("always")
        return True
