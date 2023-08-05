#!/usr/bin/python -tt
# -*- coding: UTF-8 -*-
# vim: sw=4 ts=4 et:
#
# Copyright (C) 2007 Andy Shevchenko
#
# Licensed under the Academic Free License version 2.1
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

__author__ = "Andy Shevchenko <andy@smile.org.ua>"
__revision__ = "$Id: setup.py 36 2007-11-11 12:18:30Z andy $"

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = "0.1.10"

setup(name = "minihallib",
    description = "Library to handle HAL devices and events",
    version = version,
    author = "Andy Shevchenko",
    author_email = "andy@smile.org.ua",
    url = "http://www.smile.org.ua/trac/minihallib",
    license = "GPLv2+ or AFL",
    packages = ['minihallib'],
    long_description = "Python threaded library to handle HAL devices and their events",
    keywords = "python dbus hal",
    platforms = "Python 2.4 and later",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Operating System :: Unix",
        "License :: OSI Approved :: Academic Free License (AFL)",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware",
        ]
    )
