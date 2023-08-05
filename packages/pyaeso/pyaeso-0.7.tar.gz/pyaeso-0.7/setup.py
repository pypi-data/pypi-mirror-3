#~ pyaeso is a python package that makes access to the Alberta, Canada's
#~ Electric System Operator's (AESO) Energy Trading System (ETS) easier.

#~ Copyright (C) 2009 Keegan Callin

#~ This program is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.

#~ This program is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.

#~ You should have received a copy of the GNU General Public License
#~ along with this program.  If not, see
#~ <http://www.gnu.org/licenses/gpl-3.0.html>.

from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    # 2.x
    from distutils.command.build_py import build_py


NAME = 'pyaeso'
VERSION = '0.7'
DOWNLOAD_URL = 'http://pypi.python.org/pypi/pyaeso'


def long_description():
    f = open('README.txt')
    try:
        text = f.read()
    finally:
        f.close()

    return text


DESCRIPTION = "Pythonic access to the Alberta (Canada) Electric System Operator (AESO) Energy Trading System (ETS)."
LONG_DESCRIPTION = long_description()
CLASSIFIERS = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.0",
    "Programming Language :: Python :: 3.1",
    "Programming Language :: Python :: 3.2",
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Information Analysis",
]


setup(
    name = NAME,
    packages = ['pyaeso', 'aeso'],
    version = VERSION,
    description = DESCRIPTION,
    author = "Keegan Callin",
    author_email = "kc@kcallin.net",
    url = "http://bitbucket.org/kc/pyaeso/wiki/Home",
    download_url = DOWNLOAD_URL,
    keywords = [],
    license = 'GNU General Public License Version 3 (GPLv3)',
    requires = ['pytz'],
    classifiers = CLASSIFIERS,
    long_description = LONG_DESCRIPTION,
    cmdclass = {
        'build_py' : build_py,
    }
)
