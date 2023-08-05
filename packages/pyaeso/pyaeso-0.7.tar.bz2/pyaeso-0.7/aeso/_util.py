#~ pyaeso is a python package that makes access to the Alberta, Canada's
#~ Electric System Operator's (AESO) Energy Trading System (ETS) easier.

#~ Copyright (C) 2009 - 2011 Keegan Callin

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

from datetime import timedelta
import sys
import urllib2
import codecs

class DayBlockIt(object):
    '''Steps over blocks of days between two time periods.  Each call to
    next() will return a 2-tuple containing a start date and end date as
    far apart as is permitted by the /days/ parameter.

    .. versionadded:: 0.6

    Example::

        >>> import sys
        >>> from aeso._util import DayBlockIt
        >>> from datetime import date
        >>> from os import linesep
        >>>
        >>> start_date = date(1995, 1, 1)
        >>> end_date = date(1995, 1, 10)
        >>>
        >>> it = DayBlockIt(start_date, end_date, 4)
        >>> for first, last in it:
        ...   # Using sys.stdout.write instead of print for
        ...   # compatibility on Python 2 and Python 3
        ...   n = sys.stdout.write(str(first) + ' ' + str(last) + linesep)
        ...
        1995-01-01 1995-01-04
        1995-01-05 1995-01-08
        1995-01-09 1995-01-10
    '''

    def __init__(self, start_date, end_date, days):
        '''Create an object that iterates blocks of start/end dates of length
        /days/.

        @param days:  maximum number of days in each step.

        @type start_date: datetime.date
        @type end_date: datetime.date
        @type days: int
        '''
        if days == 0:
            raise ValueError('DayBlockIt() arg 3 must not be zero')
        self._delta = timedelta(days)
        self._delta_less_one = timedelta(days - days / abs(days))
        self._now = start_date
        self._start_date = start_date
        self._end_date = end_date

    def __iter__(self):
        return self

    def next(self):
        if (self._start_date <= self._now and self._now <= self._end_date) or \
            (self._start_date >= self._now and self._now >= self._end_date):
            start_date = self._now
            end_date = self._now + self._delta_less_one

            self._now = self._now + self._delta
            if self._start_date <= self._end_date:
                if self._now > self._end_date:
                    end_date = self._end_date
            else:
                if self._now < self._end_date:
                    end_date = self._end_date

            return (start_date, end_date)
        else:
            raise StopIteration()


def __urlopen_no_timeout(url, data = None, timeout = None):
  if timeout is not None:
    raise ValueError('timeout parameter only supported in python >= 2.6.')
    
  return urllib2.urlopen(url, data)


UTF8 = 'utf-8'
Utf8Reader = codecs.getreader(UTF8)
Utf8Writer = codecs.getwriter(UTF8)

python_version = sys.version_info[0:2]
py3k = (sys.version_info[0] == 3)

if py3k or python_version in [(2,6), (2,7)]:
  _compat_urlopen = urllib2.urlopen
elif python_version in [(2,4), (2,5)]:
  _compat_urlopen = __urlopen_no_timeout
else:
  raise NotImplementedError('Unsupported python version.')
