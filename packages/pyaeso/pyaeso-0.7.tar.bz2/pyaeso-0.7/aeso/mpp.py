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

'''Access to marginal pool price (MPP) data.  The raw report can be
accessed at <http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalSystemMarginalPriceReportServlet>.'''

########################################################################
## Import Standard Library Modules

import urllib
import urllib2
from time import strptime
from time import mktime
import decimal
from decimal import Decimal
from datetime import datetime
from datetime import timedelta
from datetime import date
from shutil import copyfileobj
import csv

########################################################################
## Import 3rd Party Modules
import pytz

########################################################################
## Import AESO package modules
from aeso import AB_TZ
from aeso._util import (
  DayBlockIt,
  _compat_urlopen,
  Utf8Reader,
  Utf8Writer,
  UTF8
)


def urlopen(start_date, end_date, timeout = None):
    '''Returns a file-like object attached to the ETS marginal pool
    price report.  The report is limited by AESO to returning 31 days of
    information (2010-02-09).  The report will include data for
    start_date but not for end_date.  The earliest date for which
    marginal price information is available is 1999-10-01 (2010-02-10).
    *start_date* must be before *end_date*.

    :param start_date: :class:`datetime.date`
    :param end_date: :class:`datetime.date`
    :param timeout: optional parameter specifying timeout in seconds for
        blocking operations like the connection attempt.  If operation
        times out :class:`urllib2.URLError` will be raised.  ValueError
        will be raised in Python 2.4 and 2.5 if this parameter is set to
        anything but None.
    :rtype: file-like object as returned by urlopen.

    .. versionadded:: 0.6

    .. versionadded:: 0.7
        timeout parameter.

    Usage example::

        >>> # Standard library imports
        >>> from datetime import date
        >>> from datetime import timedelta
        >>>
        >>> # 3rd Party Libraries
        >>> from pyaeso.ets import urlopen_marginal_pool_price
        >>>
        >>> start_date = date(2010, 1, 1)
        >>> end_date = date(2010, 1, 31) + timedelta(1)
        >>> # If you want to include all days in january, must add 24 hours.
        >>> # Remember that there will be no information returned for
        >>> # *end_date* itself, only for dates prior to it!
        >>>
        >>> f = urlopen_marginal_pool_price(start_date, end_date)
        >>> text = f.read()
        >>> f.close()
    '''

    DATE_FORMAT = '%m%d%Y'
    url = 'http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalSystemMarginalPriceReportServlet'
    parameters = {
        'contentType' : 'csv',
        'beginDate' : start_date.strftime(DATE_FORMAT),
        'endDate' : end_date.strftime(DATE_FORMAT),
    }

    encoded_params = urllib.urlencode(parameters).encode(UTF8)
    #http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalSystemMarginalPriceReportServlet?beginDate=02012010&endDate=02092010&contentType=csv
    f = _compat_urlopen(url, encoded_params, timeout = timeout)

    return f


def _marginal_pool_price_dt(cells):
    date, hour_hint = [s.strip() for s in cells[0].split()]
    if hour_hint.endswith("*"):
        hour_hint = hour_hint[:-1]
    hour_hint = int(hour_hint)
    time = cells[1].strip()
    price = Decimal(cells[2])

    is_dst = None
    if time.endswith('*'):
        is_dst = False
        time = time[:-1]

    dt_str = date + ' ' + time
    dt_str = dt_str.strip()

    add_one_day = False
    try:
        struct_time = strptime(dt_str, "%m/%d/%Y %H:%M")
    except ValueError:
        # ValueError: time data '01/09/2010 24:00' does not match
        # format '%m/%d/%Y %H:%M'
        #
        # This happens because there is no "24:00" in strptime.  It
        # should be "00:00" of the following day!
        dt_str = dt_str.replace('24:', '00:')
        if hour_hint == 24:
            add_one_day = True

        struct_time = strptime(dt_str, "%m/%d/%Y %H:%M")

    # Create naive datetime object
    timestamp = mktime(struct_time)
    naive_dt = datetime.fromtimestamp(timestamp)
    if add_one_day:
        naive_dt += timedelta(1)

    # Convert naive datetime object to UTC.
    try:
        ab_dt = AB_TZ.localize(naive_dt, is_dst = is_dst)
    except pytz.AmbiguousTimeError:
        ab_dt = AB_TZ.localize(naive_dt, is_dst = True)
    utc_dt = pytz.utc.normalize(ab_dt.astimezone(pytz.utc))

    return utc_dt


_TITLE_TEXT = u'Historical System Marginal Price'.strip()
_HEADER_TEXT = u'Date (HE),Time,Price ($)'.strip()

def _filter_mpp_headers(src, dst):
    reader = Utf8Reader(src)
    writer = Utf8Writer(dst)

    l0 = reader.readline() # Historical System Marginal Price
    l1 = reader.readline() # Date (HE),Time,Price ($)
    l2 = reader.readline() # blank line

    l0 = l0.strip()
    l1 = l1.strip()
    l2 = l2.strip()

    if l0 != _TITLE_TEXT:
        raise ValueError('Expected title line not found on line 1.')

    if l1 != _HEADER_TEXT:
        raise ValueError('Expected header not found on line 2.')

    if l2 != '':
        raise ValueError('Expected line 3 of mpp file to be blank.')

    copyfileobj(reader, writer)


def dump_mpp(dst, start_date = date(1999, 10, 1), end_date = None, timeout = None):
    '''Downloads market marginal pool price data from ETS and writes it
    to file object *dst*.  Unlike urlopen_marginal_pool_price there is
    no limit on the amount of data that can be requested.  Internally
    an iterator is used to query data in 31 day blocks before it is
    written to *dst*.  Output is included for start_date but excludes
    data for end_date.

    :param dst: writeable file object
    :param start_date: :class:`datetime.date`
    :param end_date: :class:`datetime.date`
    :param timeout: optional parameter specifying timeout in seconds for
        blocking operations like the connection attempt.  If operation
        times out :class:`urllib2.URLError` will be raised.  ValueError
        will be raised in Python 2.4 and 2.5 if this parameter is set to
        anything but None.

    .. versionadded:: 0.6

    .. versionadded:: 0.7
        timeout parameter.

    Usage example::

        >>> # Standard library imports
        >>> from datetime import date
        >>> from datetime import timedelta
        >>> try:
        ...     # For Python 3
        ...     from io import BytesIO
        ... except ImportError:
        ...     # For Python 2.x
        ...     from StringIO import StringIO as BytesIO
        >>>
        >>> # 3rd Party Libraries
        >>> from aeso import mpp
        >>>
        >>> start_date = date(2010, 1, 1)
        >>> end_date = date(2010, 1, 31) + timedelta(1)
        >>> # Remember, no data will be returned on end_date itself!
        >>>
        >>> f = BytesIO()
        >>> mpp.dump_mpp(f, start_date, end_date)
        >>> text = f.getvalue()
        >>> f.close()
    '''

    if end_date is None:
        end_date = date.today() + timedelta(1)

    if start_date > end_date:
        raise ValueError('start_date must be before end_date')

    first_file = True
    for block_end, block_start in DayBlockIt(end_date, start_date, -31):
        f = urlopen(block_start, block_end + timedelta(1), timeout = timeout)
        try:
            if first_file:
                copyfileobj(f, dst)
                first_file = False
            else:
                _filter_mpp_headers(f, dst)
        finally:
            f.close()


class PPoint(object):
    '''A price at a given point in time.

    Since PPoint objects will iterate over their properties t, and
    price, they can be unpacked:

    >>> from datetime import datetime
    >>> point = PPoint(datetime(2010, 2, 12, 10, 36), '4.56')
    >>> t, price = point
    '''
    def __init__(self, dt, price):
        self.__dt = dt
        self._price = Decimal(price)
        self._iterable = None

    @property
    def t(self):
        ''':class:`datetime.datetime` property'''
        return self.dt

    @property
    def dt(self):
        '''Equal to property :class:`PPoint.t`'''
        return self.__dt

    @property
    def price(self):
        ''':class:`decimal.Decimal` property'''
        return self._price

    def __iter__(self):
        if self._iterable is None:
            self._iterable = (self.t, self.price)

        return iter(self._iterable)


def parse_mpp_file(f):
    '''Yields a :class:`PPoint` object for each price point in marginal
    pool price data report file-object *f*.  As always, times are UTC.

    .. versionadded:: 0.6

    Usage example::

        >>> # Standard library imports
        >>> from datetime import date
        >>> from datetime import timedelta
        >>> try:
        ...     # For Python 3
        ...     from io import BytesIO
        ... except ImportError:
        ...     # For Python 2.x
        ...     from StringIO import StringIO as BytesIO
        >>>
        >>> # 3rd Party Libraries
        >>> from aeso.mpp import dump_mpp, parse_mpp_file
        >>> from aeso import AB_TZ, UTC_TZ
        >>>
        >>> start_date = date(2010, 1, 1)
        >>> end_date = date(2010, 1, 31) + timedelta(1)
        >>> # Remember, no data will be returned on end_date itself!
        >>>
        >>> f = BytesIO()
        >>> dump_mpp(f, start_date, end_date)
        >>> ofs = f.seek(0)
        >>>
        >>> points = list(parse_mpp_file(f))
        >>>
        >>> for pp in points:
        ...   # PPoint objects are iterable and can be unpacked!
        ...   utc_dt, price = pp
        ...   # print '%s, $%f' % (AB_TZ.normalize(utc_dt.astimezone(AB_TZ)), price)
        ...   # *time* is in UTC, so it must be converted to Alberta
        ...   # timezone before display.
    '''

    ##########################
    #~ SAMPLE FILE:
    ##########################
    #~ Historical System Marginal Price
    #~ Date (HE),Time,Price ($)
    #~
    #~ "01/09/2010 24","23:51","42.00"
    #~ "01/09/2010 24","23:16","44.98"
    #~ "01/09/2010 24","23:09","45.00"
    #~ "01/09/2010 24","23:07","48.22"
    #~ "01/09/2010 24","23:05","49.00"
    #~ "01/09/2010 24","23:00","52.98"
    #~ "01/09/2010 23","22:55","42.00"
    #~ "01/09/2010 23","22:43","43.86"
    #~ "01/09/2010 23","22:41","46.00"
    #~ "01/09/2010 23","22:37","51.98"


    first_valid_line = False
    dst = False
    reader = csv.reader(Utf8Reader(f))
    for idx, cells in enumerate(reader):
        try:
            NUM_EXPECTED_CELLS = 3
            if len(cells) == NUM_EXPECTED_CELLS:
                dt = _marginal_pool_price_dt(cells)
                price = Decimal(cells[2])

                first_valid_line = True
                yield PPoint(dt, price)
            elif first_valid_line and len(cells) != 0:
                #raise ValueError('found {1} cell(s) where {2} were expected ("{3}").'.format(idx, len(cells), NUM_EXPECTED_CELLS, cells))
                #raise ValueError('found ' + str(len(cells)) + ' where ' + str(NUM_EXPECTED_CELLS) + ' were expected ("' + str(cells) + '").')
                raise ValueError('Found %d  where %d were expected (%s).' % (len(cells), NUM_EXPECTED_CELLS, str(cells)))
        except (decimal.InvalidOperation, ValueError), e:
            if first_valid_line:
                #raise ValueError('On row {0}, {1}'.format(idx, str(e)))
                raise ValueError('On row ' + str(idx) + ', ' + str(e))
