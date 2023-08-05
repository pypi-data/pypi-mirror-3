======
pyaeso
======

``pyaeso`` is a python package that makes access to the
Alberta, Canada, Electric System Operator's (AESO) Energy Trading
System (ETS) easier.

The Alberta Electric Systems Operator (AESO) <http://www.aeso.ca>
operates Alberta's deregulated electricity market.  AESO provides
price, demand, and other valuable information through the publically
accessible Energy Trading System (ETS) website <http://ets.aeso.ca>.
This information is useful for economic analysis, power trading,
electric system study, and electric system forecasting.  The first
step in using such information is to download it and parse it into
useful data structures - a task performed by this library.  Typically
the data will feed statistical methods, heuristics, and system models
to provide useful analysis of the Alberta electric system.

The pyaeso project is hosted at <http://bitbucket.org/kc/pyaeso> and
releases are made via the Python Package Index at
<http://pypi.python.org/pypi/pyaeso>.  Online documentation is available
at <http://packages.python.org/pyaeso>.


Audience
========

A basic knowledge of the Python programming language is required to
use this library.  Python is an easy to learn, powerful language.  An
excellent introductory tutorial is available at
<http://docs.python.org/tutorial/>.


Requirements
============
* *Python 2.4 or better* - Available at <http://python.org/download>
  (2009-11-25).

* *pytz* - "World timezone definitions, modern and historical".
  Available at <http://pypi.python.org/pypi/pytz> (2009-11-14).


Installation
============

Extract the archive, enter the recovered directory and type:

``python setup.py install``


Usage
=====

Some code samples that use pyaeso are availble in the ``examples``
directory.  One sample is listed here::


    >>> # Standard Library imports
    >>> import sys
    >>> import datetime
    >>> try:
    ...   # Python 3.x style
    ...   from io import BytesIO
    ... except ImportError:
    ...   # Python 2.x
    ...   from StringIO import StringIO as BytesIO
    ... 
    >>> # 3rd Party Module imports
    >>> import aeso
    >>> from aeso import equilibrium
    >>>
    >>> # Program
    >>> end_date = datetime.date.today()
    >>> start_date = end_dt - datetime.timedelta(1)
    >>> f = BytesIO()
    >>> try:
    ...   equilibrium.dump_equilibrium(f, start_dt, end_dt)
    ...   ofs = f.seek(0)
    ...   data = list(equilibrium.parse_equilibrium_file(f))
    ... finally:
    ...   f.close()
    ... 
    >>> for d in data:
    ...   print d.t.astimezone(aeso.AB_TZ), '$' + str(d.price), str(d.demand) + 'MW'
    ... 


Known Incompatibilities
=======================

* *Python <= 2.3* - Fails because pyaeso uses several standard library
  modules that were introduced in Python 2.4.


`pyaeso` 0.7 (2011-12-26)
=========================
* Support for Python 2.7, 3.0, 3.1, and 3.2 added and tested.

* Added timeout parameters to most urlopen and dump functions.

* Simplified test infrastructure.

* Fixed date handling in ATC to match AESO's new format.

* Removed all ATC functions from pyaeso.ets module.  These functions
  have been marked as deprecated since 0.5 and have been replaced by the
  aeso.atc module.

* Updated aeso.csd parser to convert total net generation values of '-'
  to 'None' rather than throwing a ValueError.

* Updated examples to use aeso package.


Bugs and Enhancements
=====================

If you would like to file a bug report or feature request then you can
do so at <http://bitbucket.org/kc/pyaeso/issues>.


Contact
=======

As the maintainer of this library I, Keegan Callin, would welcome your
polite, constructive comments and criticisms of this library.  I can
be reached by email using the address kc (at) kcallin.net.  If you need
to talk to me on the telephone or send me something by snail mail, send
me an email and I'll gladly mail you instructions on how to reach me.
