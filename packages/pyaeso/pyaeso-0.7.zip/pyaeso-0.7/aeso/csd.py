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

'''Access to current supply demand (CSD) data.  The raw report can be
accessed at <http://ets.aeso.ca/ets_web/ip/Market/Reports/CSDReportServlet>.'''

# Standard library imports
import urllib2
import csv
from time import strptime
from datetime import datetime
from decimal import Decimal

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
    '''Returns an open file-object connected to AESO's Current Supply
    Demand (CSD) webservice.

    :param timeout: optional parameter specifying timeout in seconds for
        blocking operations like the connection attempt.  If operation
        times out :class:`urllib2.URLError` will be raised.  ValueError
        will be raised in Python 2.4 and 2.5 if this parameter is set to
        anything but None.
    :rtype: file-like object.

    .. versionadded:: 0.5

    .. versionadded:: 0.7
        timeout parameter.
    '''
    src = 'http://ets.aeso.ca/ets_web/ip/Market/Reports/CSDReportServlet?contentType=csv'
    return _compat_urlopen(src, timeout = timeout)


def _normalize_unit(unit):
    try:
        s = unit[unit.rindex('>') + 1:]
        while s.endswith('"'):
            s = s[0:-1]

        return s
    except ValueError:
        return unit


class CsdStat(object):
    '''Superclass of SystemStat and UnitStat'''
    pass


class SystemStat(CsdStat):
    '''Class representing a system statistic.

    .. versionadded:: 0.6

    Example Usage::
        >>> from aeso import csd
        >>> from datetime import datetime
        >>> dt = datetime(2010, 4, 22)
        >>> stat = csd.SystemStat(dt, 'Sample System Statistic', 10)
        >>> stat.dt
        datetime.datetime(2010, 4, 22, 0, 0)
        >>> stat.name
        'Sample System Statistic'
        >>> stat.value
        10
        >>> dt, name, value = stat
        >>> assert stat.dt == dt
        >>> assert stat.name == name
        >>> assert stat.value == value
    '''

    def __init__(self, datetime, name, value):
        self.__dt = datetime
        self.__name = name
        self.__value = value
        self.__tuple = (self.__dt, self.__name, self.__value)

    @property
    def dt(self):
        '''Entry :class:`datetime.datetime`.'''
        return self.__dt

    @property
    def name(self):
        '''Unit name, :class:`str`.'''
        return self.__name

    @property
    def value(self):
        '''Value, polymorphic.'''
        return self.__value

    def __iter__(self):
        return iter(self.__tuple)

    def __len__(self):
        return len(self.__tuple)

    def __getitem__(self, idx):
        '''Method is present only to support old code.'''
        return self.__tuple[idx]


class UnitStat(CsdStat):
    '''Class representing an entry in the Alberta Integrated Electric
    System Log.  This object will iterate over its members returning
    self.dt, and self.description in succession.

    .. versionadded:: 0.6

    Example Usage::
        >>> from aeso import csd
        >>> from datetime import datetime
        >>> dt = datetime(2010, 4, 22)
        >>> stat = csd.UnitStat(dt, 'Sample Unit Statistic', 10, 5, 0)
        >>> stat.dt
        datetime.datetime(2010, 4, 22, 0, 0)
        >>> stat.name
        'Sample Unit Statistic'
        >>> stat.mcr
        10
        >>> stat.tng
        5
        >>> stat.dcr
        0
        >>> dt, name, mcr, tng, dcr = stat
        >>> assert stat.dt == dt
        >>> assert stat.name == name
        >>> assert stat.mcr == mcr
        >>> assert stat.tng == tng
        >>> assert stat.dcr == dcr
        '''

    def __init__(self, datetime, name, mcr, tng, dcr):
        self.__dt = datetime
        self.__name = name
        self.__mcr = mcr
        self.__tng = tng
        self.__dcr = dcr
        self.__tuple = (self.__dt, self.__name, self.__mcr, self.__tng, self.__dcr)


    @property
    def dt(self):
        '''Entry :class:`datetime.datetime`.'''
        return self.__dt


    @property
    def name(self):
        '''Unit name.'''
        return self.__name


    @property
    def mcr(self):
        '''Maximum continuous rating.
        
        :rtype: Decimal'''
        return self.__mcr

    @property
    def tng(self):
        '''Total net generation.
        
        :rtype: Decimal or None'''
        return self.__tng

    @property
    def dcr(self):
        '''Dispatched contingency reserve.

        :rtype: Decimal or None'''
        return self.__dcr

    def __iter__(self):
        return iter(self.__tuple)

    def __len__(self):
        return len(self.__tuple)

    def __getitem__(self, idx):
        '''Method is present only to support old code.'''
        return self.__tuple[idx]


def parse_csd_file(f, reference_dt = None):
    '''Yields subclasses of :class:`CsdStat` objects containing
    information from file-like object `f` (as returned by
    :func:`urlopen`).   Subclasses of :class:`CsdStat` presently
    yielded include:

    * :class:`SystemStat`.
    * :class:`UnitStat`.

    AESO presently publishes system statistics with the names (2010-03-10):

    * Alberta Total Net Generation
    * Interchange
    * Alberta Internal Load (AIL)
    * Alberta Load Responsibility
    * Contingency Reserve Required
    * Dispatched Contingency Reserve (DCR)
    * Dispatched Contingency Reserve - Gen
    * Dispatched Contingency Reserve - Other
    * BC Interchange flow
    * SK Interchange flow

    These system statistics will be represented by yielded
    :class:`SystemStat` objects.

    Unit data yielded in :class:`UnitStat` objects may actually be
    pseudo-units; For example, AESO provides data on a "Coal" unit
    that represents the generation output of all coal plants in the
    province.

    .. versionchanged:: 0.6
        Now yields subclasses of :class:`CsdData` instead of 3-tuples
        and 5-tuples.  The change should be transparent because
        :class:`CsdData` subclasses have tuple behaviours like __len__,
        __iter__, and __getitem__.

    .. versionadded:: 0.5

    Example Usage::

        >>> from aeso import csd
        >>> from aeso import AB_TZ
        >>> systemstats = []
        >>> unitstats = []
        >>> f = csd.urlopen()
        >>> for datapoint in csd.parse_csd_file(f):
        ...     if isinstance(datapoint, csd.SystemStat):
        ...         systemstats.append(datapoint)
        ...     elif isinstance(datapoint, csd.UnitStat):
        ...         ab_dt = AB_TZ.normalize(datapoint.dt.astimezone(AB_TZ))
        ...         unitstats.append(datapoint)
        ...     else:
        ...         raise TypeError('Unexpected type')
        ...
        >>> f.close()
    '''

    utc_dt = None
    num_extracted_rows = 0
    reader = csv.reader(Utf8Reader(f))
    for idx, cells in enumerate(reader):
        if len(cells) == 0:
            # Blank line.  Ignore and continue
            pass
        elif len(cells) == 1:
            value = cells[0]
            if value.strip() == 'Current Supply Demand Report':
                # Ignore report title
                pass
            elif value.startswith('Last Update :'):
                struct_time = strptime(cells[0], "Last Update : %b %d, %Y %H:%M")
                dt = datetime(*struct_time[0:6])
                #print cells[0], '=>', dt
                try:
                    ab_dt = AB_TZ.localize(dt, is_dst = None)
                except pytz.AmbiguousTimeError:
                    # Have reference time
                    if reference_dt is None:
                        raise
                    else:
                        with_dst_dt = AB_TZ.localize(dt, is_dst = True)
                        without_dst_dt = AB_TZ.localize(dt, is_dst = False)

                        if abs(without_dst_dt - reference_dt) <= abs(with_dst_dt - reference_dt):
                            ab_dt = AB_TZ.localize(dt, is_dst = False)
                        else:
                            ab_dt = AB_TZ.localize(dt, is_dst = True)

                utc_dt = pytz.utc.normalize(ab_dt.astimezone(pytz.utc))
            else:
                raise ValueError('Unexpected line data' + str(cells))

            num_extracted_rows += 1
        elif len(cells) == 2:
            if utc_dt is None:
                raise ValueError('No datetime set')
            unit = _normalize_unit(cells[0])

            if unit == 'TOTAL':
                continue

            if cells[1] == '-':
                value = ''
            else:
                value = Decimal(cells[1])

            num_extracted_rows += 1
            yield SystemStat(utc_dt, unit, value)
        elif len(cells) == 4:
            if utc_dt is None:
                raise ValueError('No datetime set')

            unit = _normalize_unit(cells[0])
            if unit == 'TOTAL':
                continue
            mcr = Decimal(cells[1]) # Maximum continuous rating

            str_tng, str_dcr = cells[2:4]
            str_tng = str_tng.strip()
            str_dcr = str_dcr.strip()

            if str_tng == '-':
                tng = None
            else:
                tng = Decimal(cells[2]) # total net generation

            if str_dcr == '-':
                tng = None
            else:
                dcr = Decimal(cells[3]) # Dispatched (and Accepted) Contingency Reserve

            num_extracted_rows += 1
            yield UnitStat(utc_dt, unit, mcr, tng, dcr)
        else:
            raise IndexError('Incorrect number of cells.')
