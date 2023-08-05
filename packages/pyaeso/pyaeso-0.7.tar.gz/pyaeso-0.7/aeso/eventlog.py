# -*- coding: utf-8 -*-
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

'''Access to the Alberta Interconnected Electric System Event log.  The
raw log is accessible at
<http://ets.aeso.ca/ets_web/ip/Market/Reports/RealTimeShiftReportServlet>.
'''

# Standard library imports
import urllib2
import csv
from time import strptime
from time import mktime
from datetime import datetime

# 3rd party libraries
import pytz

# Custom libraries
from aeso import AB_TZ
from aeso._util import (
  DayBlockIt,
  _compat_urlopen,
  Utf8Reader
)



def urlopen(timeout = None):
    '''Returns an open file-object connected to AESO's Alberta
    Interconnected Electric System (AIES) event log webservice.

    :param timeout: optional parameter specifying timeout in seconds for
        blocking operations like the connection attempt.  If operation
        times out :class:`urllib2.URLError` will be raised.  ValueError
        will be raised in Python 2.4 and 2.5 if this parameter is set to
        anything but None.
    :rtype: file-like object.

    .. versionadded:: 0.6

    .. versionadded:: 0.7
        timeout parameter.
    '''

    src = 'http://ets.aeso.ca/ets_web/ip/Market/Reports/RealTimeShiftReportServlet?contentType=csv'
    return _compat_urlopen(src, timeout = timeout)


class LogEntry(object):
    '''Class representing an entry in the Alberta Integrated Electric
    System Log.  This object will iterate over its members returning
    self.dt, and self.description in succession.

    .. versionadded:: 0.6

    Example Usage::
        >>> from aeso import eventlog
        >>> from datetime import datetime
        >>> dt = datetime(2010, 4, 22)
        >>> e = eventlog.LogEntry(dt, 'Sample log entry')
        >>> e.dt
        datetime.datetime(2010, 4, 22, 0, 0)
        >>> e.description
        'Sample log entry'
        >>> extracted_dt, extracted_desc = e
        >>> str(extracted_dt)
        '2010-04-22 00:00:00'
        >>> str(extracted_desc)
        'Sample log entry'
    '''

    def __init__(self, datetime, description):
        self.__dt = datetime
        self.__desc = description
        self.__tuple = (self.__dt, self.__desc)

    @property
    def dt(self):
        ''':class:`datetime.datetime` property.'''
        return self.__dt

    @property
    def description(self):
        ''':class:`str` property.'''
        return self.__desc

    def __iter__(self):
        return iter(self.__tuple)

    def __len__(self):
        return len(self.__tuple)

    def __getitem__(self, idx):
        return self.__tuple[idx]

    def __eq__(self, other):
        if self.__tuple == other.__tuple:
            return True
        else:
            return False


def parse_eventlog_file(f):
    '''Yields (:class:`LogEntry`, str) objects containing
    event datetime and description as extracted from file-like object
    `f`.  As always with pyaeso, datetimes are UTC offset-aware and
    should be converted to localized datetimes before being displayed
    to the user.

    .. versionadded:: 0.6

    Example Usage::
        >>> from aeso import eventlog
        >>> from aeso import AB_TZ
        >>>
        >>> from datetime import datetime
        >>> f = eventlog.urlopen()
        >>> for utc_dt, msg in eventlog.parse_eventlog_file(f):
        ...     # Convert UTC to Alberta timezone before printing
        ...     ab_dt = AB_TZ.normalize(utc_dt.astimezone(AB_TZ))
        ...     assert type(ab_dt) == datetime
        ...     assert type(msg) == str # Event description
        ...
        >>> f.close()
    '''

    num_extracted_rows = 0
    reader = csv.reader(Utf8Reader(f))
    for idx, cells in enumerate(reader):
        try:
            if len(cells) == 0:
                # Blank line.  Ignore and continue
                pass
            elif len(cells) == 2:
                dt_str = cells[0]
                entry = cells[1]

                struct_time = strptime(dt_str, "%m/%d/%Y %H:%M")
                timestamp = mktime(struct_time)
                dt = datetime.fromtimestamp(timestamp)
                ab_dt = AB_TZ.localize(dt)
                utc_dt = pytz.utc.normalize(ab_dt.astimezone(pytz.utc))

                num_extracted_rows += 1
                yield LogEntry(utc_dt, entry)
            else:
                raise IndexError('Incorrect number of cells.')
        except (IndexError, ValueError), e:
            if num_extracted_rows > 0:
                raise
            else:
                continue
