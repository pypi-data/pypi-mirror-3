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

from distutils.command.install import INSTALL_SCHEMES

import glob
import re
import os
from unittest import defaultTestLoader

try:
    from setuptools import setup
    from setuptools import find_packages
    from setuptools import Command
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup
    from setuptools import find_packages
    from setuptools import Command

try:
    _long_descr = open(os.path.join(
        os.path.dirname(__file__), "README.txt"),
        'r').read()
except IOError:
    _long_descr = ""

try:
    from hwit.core.about import version
except ImportError:
    try:
        from hwit.core.doc.conf import release as version
    except ImportError:
        version = "0.00"

# Lonnie Princehouse's tip for improving data_files behaviour
for scheme in INSTALL_SCHEMES.values():
    scheme["data"] = scheme["purelib"]

_options = {
    "py2exe": {
        "skip_archive": 1,
        "packages": ["encodings", "hwit.core.checks"],
        "excludes": ["_ssl", "_hashlib"],
        "dll_excludes": [
            'MSVCP90.dll'
         ]
     }
}

if os.name == "nt":
    import py2exe
    # Eli Bendersky's fix for missing DLLs 
    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    def isSystemDLL(pathname):
        if os.path.basename(pathname).lower() in (
        "msvcp71.dll", "dwmapi.dll"):
            return 0
        return origIsSystemDLL(pathname)

    py2exe.build_exe.isSystemDLL = isSystemDLL

_data_files = [
("ref",["ref/hewit_poll.hwit", "ref/scout_camp.hwit", "ref/attitude_form.hwit",
"ref/scout_camp.tsv","ref/attitude_form.tsv", "ref/gui_test-template.tsv"]),
("doc",glob.glob("doc/*.html")),
("doc/ui/default",glob.glob("doc/ui/default/*")),
("doc/html",glob.glob("doc/html/*.html")),
("doc/html/_static",glob.glob("doc/html/_static/*")),
("doc/html/_images",glob.glob("doc/html/_images/*"))
]

# Distribute is under heavy development. It's important
# to pin to known-good versions. See
# https://bitbucket.org/tarek/distribute/issues/
_distribute_spec = "distribute" + ','.join([
    ">=0.6.14", # 0.6.14 known good
    "!=0.6.17", # bug with namespace packages
    "!=0.6.26", # setup.py install --user fail
])

setup(
    name="hwit-core",
    version=version,
    description="Here's What I Think; core library",
    author="D Haynes",
    author_email="tundish@thuswise.org",
    license="COPYING",
    url="http://hwit.org",
    long_description=_long_descr,
    classifiers=[
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
    ],
    namespace_packages = ["hwit"],
    packages=find_packages(),
    options = _options,

    dependency_links = [
    ],

    package_data = {
        "": ["COPYING", "README.txt", "CHANGES.txt", "INSTALL.txt"],
        "hwit.core.doc": ["*.rst", "_build/html/*.js", "_build/html/*.html", "_build/html/_static/*"],
        "hwit.core.test": ["ref/*.hwit", "ref/*.tsv"],
    },
    exclude_package_data = {
    },
    setup_requires=[
    ],
    tests_require=[
    ],
    install_requires=[
    ],
    entry_points={
        "console_scripts": [
            "hwit-console = hwit.core.utils.hwit_console:run"
        ],
        "thuswise.hugo.testloader": [
            "console = hwit.core.test.test_console:load_tests",
            "container = hwit.core.test.test_container:load_tests",
            "context = hwit.core.test.test_context:load_tests",
            "generator = hwit.core.test.test_generator:load_tests",
            "typertest = hwit.checks.test.test_typertest:load_tests"
        ],
        "thuswise.hugo.fixture": [
        ]
    },
    extras_require={
    }
)
