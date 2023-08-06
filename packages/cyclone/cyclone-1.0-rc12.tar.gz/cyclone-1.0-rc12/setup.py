#!/usr/bin/env python
#
# Copyright 2010 Alexandre Fiori
# based on the original Tornado by Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys

requires = ["twisted", "pyopenssl"]

from distutils import log
from distutils.core import setup

# PyPy and setuptools don't get along too well, yet.
if sys.subversion[0].lower().startswith('pypy'):
    from distutils.core import setup
    extra = dict(requires=requires)
else:
    from setuptools import setup
    extra = dict(install_requires=requires)


setup(
    name="cyclone",
    version="1.0-rc12",
    author="fiorix",
    author_email="fiorix@gmail.com",
    url="http://cyclone.io/",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="Non-blocking web server. "
                "A facebook's Tornado on top of Twisted.",
    keywords="python non-blocking web server twisted facebook tornado",
    packages=["cyclone", "twisted.plugins"],
    package_data={"cyclone": ["appskel.zip"],
                  "twisted": ["plugins/cyclone_plugin.py"]},
    **extra
)

try:
    from twisted.plugin import IPlugin, getPlugins
    list(getPlugins(IPlugin))
except:
    log.warn("*** Failed to update Twisted plugin cache. ***")
