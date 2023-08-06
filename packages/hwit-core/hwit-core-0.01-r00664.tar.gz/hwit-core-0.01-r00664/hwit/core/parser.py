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
import os.path
import logging

# container parsing
import warnings
import htmlentitydefs
from HTMLParser import HTMLParser
from urlparse import urlparse, urljoin

# checker parsing
import imp

import hwit.checks

def isTrue(arg):
    return arg.lower() in ["true","yes"]

def package_path(pkg):
    """
    This returns the hwit.checks package directory.
    ..  warning:: py2exe options must include ``"skip_archive":1``
    """
    return os.path.dirname(
    unicode(pkg.__file__, sys.getfilesystemencoding( )))

def validators(seq):
    prefix = "hwit.checks."
    pkgP = package_path(hwit.checks)
    for k in seq:
        if not k.startswith(prefix): continue
        try:
            bits = k[len(prefix):].split('.')
            if len(bits) < 2: continue
            f,p,d = imp.find_module(bits[0],[pkgP])
            mod = imp.load_module(bits[0],f,p,d)
            klass = getattr(mod,bits[1])
            fn = getattr(klass(),bits[2])
            yield k,fn
        except (ImportError, ValueError, AttributeError):
            # plugin not found
            continue
        except (IndexError):
            # all checker classes are callable
            yield k,klass()

class Reader(HTMLParser):

    """
    A Reader is responsible for processing the file character
    by character. It is closely coupled to
    :class:`hwit.core.model.Container`, and invokes callbacks on
    that class whenever certain tags are detected.
    """

    def __init__(self, factory, logName):
        self._client = factory
        self._dataCallback = None
        self._endTagCallback = None
        self._log = logging.getLogger(logName)
        HTMLParser.__init__(self)
        warnings.resetwarnings()
        warnings.simplefilter("always")

    def requestData(self, callback):
        self._dataCallback = callback

    def requestEnd(self, callback):
        self._endTagCallback = callback

    def handle_decl(self, decl):
        """ Check to see if there is RDF data here """
        start = r'DOCTYPE html PUBLIC "-//W3C//DTD XHTML+RDFa 1.1//EN"'
        end = r'"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"'
        if decl.startswith(start) and decl.endswith(end):
            self._client.on_doctype(self.getpos())

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            self._client.on_meta_start(attrs, self.getpos())
        elif tag == "title":
            self._client.on_title_start(attrs, self.getpos())
        elif tag == "body":
            self._client.on_body_start(
            attrs, self.getpos(), self.get_starttag_text())
        elif tag == "div":
            if dict(attrs).get("class","")=="hwit_group":
                self._client.on_group_start(
                attrs, self.getpos(), self.get_starttag_text())
        elif tag == "dl":
            self._client.on_list_start(
            attrs, self.getpos(), self.get_starttag_text())
        elif tag == "dt":
            self._client.on_term_start(
            attrs, self.getpos(), self.get_starttag_text())
        elif tag == "dd":
            self._client.on_defn_start(
            attrs, self.getpos(), self.get_starttag_text())
        elif tag in ("h1","h2","h3","h4","h5","h6"):
            self.requestData(self._client.on_heading)
            self._client.on_element_start(tag,
            attrs, self.getpos(), self.get_starttag_text())
        elif tag in ("a","html","head","kbd","li","ol","p",
            "span","style","ul"):
            self._client.on_element_start(tag,
            attrs, self.getpos(), self.get_starttag_text())
        else:
            lineno, pos = self.getpos()
            warnings.warn("forbidden '%s' tag at line %d, pos %d"
            % (tag,lineno,pos), SyntaxWarning)

    def handle_data(self, data):
        if self._dataCallback is not None:
            self._dataCallback(data)

    def handle_endtag(self, tag):
        if tag == "meta":
            self._client.on_meta_end(
            self.getpos(), self.get_starttag_text())
        elif tag == "title":
            self._client.on_title_end(
            self.getpos(), self.get_starttag_text())
        elif tag == "body":
            self._client.on_body_end(
            self.getpos(), self.get_starttag_text())
        elif tag == "div":
            self._client.on_group_end(
            self.getpos(), self.get_starttag_text())
        elif tag == "dl":
            self._client.on_list_end(
            self.getpos(), self.get_starttag_text())
        elif tag == "dt":
            self._client.on_term_end(
            self.getpos(), self.get_starttag_text())
        elif tag == "dd":
            self._client.on_defn_end(
            self.getpos(), self.get_starttag_text())
        else:
            self._client.on_element_end(tag,
            self.getpos(), self.get_starttag_text())
        
        if self._endTagCallback is not None:
            self._endTagCallback(
            self.getpos(), self.get_starttag_text())
