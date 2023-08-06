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
The module defines classes to validate strings. Each class is a
callable object, with separate checking methods. The return type
is always a boolean.

The class itself always provides the most permissive validation.
If a particular input format is required then one of the class
methods should specifically be used.
"""

import inspect
from time import strptime
from functools import wraps
from bisect import bisect_right
import email.utils

def likeTyper(typer):
    """
    The **like...** methods permit empty or partial values. They are
    necessary for usability reasons (a user can delete a number and
    replace it with a blank).

    This function locates the **like** method corresponding to a bound
    **is** method.
    """
    info = dict(inspect.getmembers(typer))
    try:
        obj = info["im_self"]
        name = typer.__name__
        name = "like" + name[2:] if name.startswith("is") else name
        return getattr(obj, name)
    except:
        return typer

class AllowsEmptyStrings(object):
    """
    Many of the classes in this module inherit from this one.
    For those, any method they have whose name begins **is**
    implicitly creates another named the same, only starting **like**.
    Eg: :meth:`numbertyper.isPositiveInteger` implies 
    :meth:`numbertyper.likePositiveInteger` .

    """
    def __getattr__(self, name):
        """
        synthesises a set of methods beginning `like`
        for each of the `is` methods. These permit an empty
        string as a match in addition to other checks
        """
        def wrapper(fn):
            @wraps(fn)
            def inner(val):
                return val == "" or fn(val)
            return inner

        if name.startswith("like"):
            call = "is" + name[4:]
            rv = wrapper(getattr(self, call))
            rv.__name__ = name
            return rv
        else:
            raise AttributeError
        
class booltyper(object):
    """
    checks that a value can be loosely interpreted as a
    boolean type (True or False, Yes or No)

    ..  todo:: implement a likeTyper

    """
    patterns = {
    "like": ("","ye","t","tr","tru","f","fa","fal","fals","non"),
    "bool": ("true", "false"),
    "state": ("y", "yes", "n", "no"),
    "none": ("none",)
    }

    def __call__(self, val):
        return self.likeTriState(val)

    def isBiState(self, val):
        """
        checks that a value strictly conforms to a
        binary yes/no, true/false value
        """
        return val.lower() in self.patterns["bool"] + self.patterns["state"]

    def likeBiState(self, val):
        return self.isBiState(val) or val.lower() in self.patterns["like"]

    def isTriState(self, val):
        """
        checks that a value strictly conforms to a
        binary yes/no, true,false or none value
        """
        return val.lower() in self.patterns["bool"]
        + self.patterns["state"] + self.patterns["none"]

    def likeTriState(self, val):
        return self.isTriState(val) or val.lower() in self.patterns["like"]

    def isBiBool(self, val):
        """
        checks that a value strictly conforms to a
        binary boolean value
        """
        return val.lower() in self.patterns["bool"]

    def likeBiBool(self, val):
        return self.isBiBool(val) or val.lower() in self.patterns["like"]

    def isTriBool(self, val):
        """
        checks that a value strictly conforms to a
        binary boolean or none value 
        """
        return val.lower() in self.patterns["bool"] + self.patterns["none"]

    def likeTriBool(self, val):
        return self.isTriBool(val) or val.lower() in self.patterns["like"]

class numbertyper(AllowsEmptyStrings):
    """
    checks that a value can be loosely interpreted as a
    numerical type
    """

    def __call__(self, val):
        return val.isdigit()

    def isPositiveInteger(self, val):
        """
        checks that a value is greater than or equal to zero
        """
        return val.isdigit() and int(val) >= 0

class datetimetyper(object):
    """
    checks that a value can be loosely interpreted as a
    date and time
    """
    patterns = {
    0: ("",),
    4: ("%Y",),
    5: ("%Y-",),
    7: ("%Y-%m",),
    8: ("%Y-%m-",),
    10: ("%Y-%m-%d",),
    11: ("%Y-%m-%dT", "%Y-%m-%d "),
    13: ("%Y-%m-%dT%H", "%Y-%m-%d %H"),
    14: ("%Y-%m-%dT%H:", "%Y-%m-%d %H:"),
    16: ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"),
    17: ("%Y-%m-%dT%H:%M:", "%Y-%m-%d %H:%M:"),
    19: ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S")
    }

    def __call__(self, val):
        return self.likeISOTime(val)

    def likeISODateTime(self, val):
        """ checks a value might conform to ISO 8601 datetime formats,
        eg: ``2010-02-24T19:57:03`` or ``2010-02-24 19:57:03`` 
        """
        keys = self.patterns.keys()
        index = bisect_right(keys, len(val))
        span = keys[(index - 1)]
        for p in self.patterns[span]:
            try:
                strptime(val[:span], p)
            except ValueError:
                continue
            except IndexError:
                break
            else:
                if val and not span:
                    return unicode(val).isdigit()
                else:
                    return True
        return False

    def isISODateTime(self, val):
        """ checks a value conforms to ISO 8601 datetime formats, eg:
            ``2010-02-24T19:57:03`` or ``2010-02-24 19:57:03`` 
        """ 
        rv = (len(val) == max(self.patterns.keys())
        and self.likeISODateTime(val))
        return rv

    def likeISODate(self, val):
        return self.likeISODateTime(val)

    def isISODate(self, val):
        """ checks a value conforms to ISO 8601 date formats, eg:
            ``2010-02-24``
        """ 
        dt = "%s 13:59:59" % val
        return self.isISODateTime(dt)

    def likeISOTime(self, val):
        dt = "1970-01-01 %s" % val
        return self.likeISODateTime(dt)

    def isISOTime(self, val):
        """ checks a value conforms to ISO 8601 time formats, eg:
            ``19:57:03``
        """ 
        dt = "1970-01-01 %s" % val
        return self.isISODateTime(dt)

class emailtyper(object):
    """
    checks that a value can be loosely interpreted as an
    email address
    """
    def __call__(self, val):
        return self.isAddr(val)

    def isAddr(self, val):
        """
        checks that a value strictly conforms to an
        email address format
        """
        return email.utils.parseaddr(val) != ('','')

class scaletyper(object):
    """
    checks that a value can be loosely interpreted as falling
    within one of several well-recognised scales
    """
    def __call__(self, val):
        raise NotImplementedError
    
    def mapped_scale(labels):
        """
        Decorates a method of this class with the attributes ``min``,
        ``max``, and ``labels`` in order to provide the data required
        by GUI elements. Also provides a default implementation for
        the mapped scale type
        """
        def inner(fn):
            fn.min = min(labels.keys())
            fn.max = max(labels.keys())
            fn.labels = labels
            @wraps(fn)
            def wrapper(*args, **kwargs):
                try:
                    return args[1] in labels.values()
                except KeyError:
                    return False
            return wrapper
        return inner

    @mapped_scale({-3:"strongly disagree", -2:"disagree",
    -1:"partially disagree", 0:"undecided", 1:"partially agree",
    2:"agree", 3:"strongly agree"})
    def isSevenValuedVote(self, val):
        """
        checks that a value falls within a seven valued scale,
        eg: such as the Likert scale used in questionnaires
        """
        pass

