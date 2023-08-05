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

'''Helper functions to access AESO's raw ETS pool price report as
published by AESO at
<http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet>.'''

########################################################################
## Standard library imports
import urllib
import urllib2
from datetime import date
from datetime import datetime
from datetime import timedelta
import shutil
import time
import csv
import decimal
from decimal import Decimal
from time import strptime
from time import mktime
import re


########################################################################
## Import 3rd party modules
import pytz


########################################################################
## AESO Modules
from aeso import AB_TZ
from aeso._util import (
  DayBlockIt,
  _compat_urlopen,
  Utf8Reader,
  UTF8
)

_RE_DATEHOUR = re.compile('(\d+)/(\d+)/(\d+) (\d+)$')

def urlopen(start_date, end_date, timeout = None):
    '''Returns a file-like object attached to the ETS pool price report
    webservice.  Note that the webservice limits the number of days
    that can be queried to 721 days (as of 2009-11-12).

    :param start_date: :class:`datetime.date`
    :param end_date: :class:`datetime.date`
    :param timeout: optional parameter specifying timeout in seconds for
        blocking operations like the connection attempt.  If operation
        times out :class:`urllib2.URLError` will be raised.  ValueError
        will be raised in Python 2.4 and 2.5 if this parameter is set to
        anything but None.
    :rtype: file-like object.

    .. versionadded:: 0.7
        timeout parameter.

    Usage example::

        >>> # Standard library imports
        >>> from datetime import date
        >>> from datetime import timedelta
        >>>
        >>> # 3rd Party Libraries
        >>> from aeso import equilibrium
        >>>
        >>> end_date = date.today()
        >>> start_date = end_date - timedelta(1)
        >>>
        >>> f = equilibrium.urlopen(start_date, end_date)
        ... try:
        ...     bytes = f.read()
        ...     assert len(bytes) > 0
        ... finally:
        ...     f.close()
    '''
    DATE_FORMAT = '%m%d%Y'

    url = 'http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet'
    parameters = {
        'contentType' : 'csv',
        'beginDate' : start_date.strftime(DATE_FORMAT),
        'endDate' : end_date.strftime(DATE_FORMAT),
    }

    encoded_params = urllib.urlencode(parameters).encode(UTF8)
    #http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet?contentType=html&beginDate=08012009&endDate=08112009
    f = _compat_urlopen(url, encoded_params, timeout = timeout)

    return f


def dump_equilibrium(f_out, start_date = date(1995, 1, 1), end_date = None, timeout = None):
    '''Downloads market equilibrium data from ETS and writes it to the
    file object f_out.  Unlike urlopen_pool_price there is no
    restriction on the amount of data that can be requested.  Internally
    an iterator is used to query data in 721 day blocks before it is
    written to f_out.

    :param f: file-like object
    :param start_date: :class:`datetime.date`
    :param end_date: :class:`datetime.date` (default date.today() + timedelta(1))
    :param timeout: optional parameter specifying timeout in seconds for
        blocking operations like the connection attempt.  If operation
        times out :class:`urllib2.URLError` will be raised.  ValueError
        will be raised in Python 2.4 and 2.5 if this parameter is set to
        anything but None.

    .. versionadded:: 0.7
        timeout parameter.

    Usage example::

        >>> # Standard Libraries
        >>> from datetime import date
        >>> from datetime import timedelta
        >>> try:
        ...     # Python 3
        ...     from io import BytesIO
        ... except ImportError:
        ...     # Python 2.x
        ...     from StringIO import StringIO as BytesIO
        >>>
        >>> # Import 3rd party libraries
        >>> from aeso import equilibrium
        >>>
        >>> end_date = date.today()
        >>> start_date = end_date - timedelta(1)
        >>>
        >>> f = BytesIO()
        >>> try:
        ...     equilibrium.dump_equilibrium(f, start_date, end_date)
        ...     assert len(f.getvalue()) > 0
        ... finally:
        ...     f.close()
    '''

    if end_date is None:
        end_date = date.today() + timedelta(1)

    for (start, end) in DayBlockIt(start_date, end_date, 721):
        # print 'From', start, 'to', end
        f_in = urlopen(start, end, timeout = timeout)
        shutil.copyfileobj(f_in, f_out)

        if end < end_date:
            time.sleep(10)


def _normalize_pool_price_dtstr_to_utc(datetime_str):
    # Sample line:
    # ['Date (HE)', 'Price ($)', '30Ravg ($)', 'System Demand (MW)']
    # ['08/10/2009 15', '67.36', '39.67', '8623.0']
    datetime_str = datetime_str.strip()
    starred = False

    # Construct a naive datetime object
    try:
        if datetime_str.endswith('*'):
            starred = True
            datetime_str = datetime_str[0:-1]

        # This series is to support Python < 2.5
        struct_time = strptime(datetime_str, "%m/%d/%Y %H")
        timestamp = mktime(struct_time)
        t = datetime.fromtimestamp(timestamp)

        # Python >= 2.5
        # t = datetime.datetime.strptime(datetime_str, "%m/%d/%Y %H")

        # This code segment verifies that the Python 2.4 code section
        # above is equivalent to the Python >= 2.5 version.
        #~ if datetime.datetime.strptime(datetime_str, "%m/%d/%Y %H") != t:
            #~ raise ValueError('Problem!')

    except ValueError:
        # Often receive a line like this.
        # ['07/31/2009 24', '36.78', '41.83', '7556.0']
        #
        # AESO clock goes from 1-24 hours instead of expected
        # range of 0-23.
        #
        # Compensating for this strangeness
        miscreant_str = datetime_str
        match = _RE_DATEHOUR.match(miscreant_str)
        if match:
            year = int(match.group(3))
            month = int(match.group(1))
            day = int(match.group(2))
            hour = int(match.group(4))

            if hour == 24:
                t = datetime(year, month, day, 0) + timedelta(1)
            else:
                raise
        else:
            raise

    # Localize naive datetime objects.
    #
    # On a Daylight-Savings-Time (DST) switch, AESO hours are counted:
    # 1, 2, 2*
    #
    # Need to translate this to:
    # 1 (with is_dst option set to True), 1 (with is_dst option set to False), 2
    #
    if t.hour == 2 and not starred:
        # Testing to see if this second-hour of the day occurs
        # after a DST transition
        dst_test_time = datetime(t.year, t.month, t.day, t.hour - 1)
        try:
            AB_TZ.localize(dst_test_time, is_dst = None)
        except pytz.AmbiguousTimeError:
            # This "2" occurs after a DST transition
            ab_dt = AB_TZ.localize(dst_test_time, is_dst = False)
        else:
            # This "2" does not occur after a DST transition; no is_dst necessary
            ab_dt = AB_TZ.localize(t, is_dst = None)
    else:
        try:
            ab_dt = AB_TZ.localize(t, is_dst = None)
        except pytz.AmbiguousTimeError:
            if t.hour == 1 and not starred:
                # First hour occurring before a DST jump.
                ab_dt = AB_TZ.localize(t, is_dst = True)
            else:
                raise

    # convert from Alberta time to UTC time
    return pytz.utc.normalize(ab_dt.astimezone(pytz.utc))


class QpPoint(object):
    '''Represents the market equilibrium price and quantity exchanged at
    a given point in time.'''

    def __init__(self, t, price, demand):
        self._t = t
        self._price = Decimal(price)
        self._demand = Decimal(demand)

    @property
    def t(self):
        ''':class:`datetime.datetime` property.'''
        return self._t

    @property
    def price(self):
        ''':class:`decimal.Decimal` property.'''
        return self._price

    @property
    def demand(self):
        ''':class:`decimal.Decimal` property.'''
        return self._demand

    @classmethod
    def from_csvline(cls, line):
        '''Extracts a QpPoint object from a sequece object like:
        ['08/10/2009 15', '67.36', '39.67', '8623.0'].
        '''
        # ['Date (HE)', 'Price ($)', '30Ravg ($)', 'System Demand (MW)']

        # Normalize time string to UTC time.
        t = _normalize_pool_price_dtstr_to_utc(line[0])
        price = Decimal(line[1])
        demand = Decimal(line[3])

        point = QpPoint(t, price, demand)

        return point


def parse_equilibrium_file(f):
    '''Yields :class:`QpPoint` objects as extracted from the open CSV
    file-object *f*.

    Usage example::

        >>> # Standard library imports
        >>> from datetime import date
        >>> from datetime import timedelta
        >>> try:
        ...     from io import BytesIO
        ... except ImportError:
        ...     from StringIO import StringIO as BytesIO
        >>>
        >>> # 3rd Party Libraries
        >>> import aeso
        >>> from aeso import equilibrium
        >>>
        >>> end_date = date.today()
        >>> start_date = end_date - timedelta(1)
        >>>
        >>> f = BytesIO()
        >>> try:
        ...     equilibrium.dump_equilibrium(f, start_date, end_date)
        ...     ofs = f.seek(0)
        ...     data = list(equilibrium.parse_equilibrium_file(f))
        ...     assert len(data) > 0
        ... finally:
        ...     f.close()
        >>>
        >>> # Yesterday's market clearing price/demand points.
        >>> for d in data:
        ...   ab_time = AB_TZ.normalize(d.t.astimezone(aeso.AB_TZ))
        ...   # print '{0} ${1} {2}MW'.format(ab_time, d.price, d.demand)
    '''

    reader = csv.reader(Utf8Reader(f))
    for idx, line in enumerate(reader):
        # ['Date (HE)', 'Price ($)', '30Ravg ($)', 'System Demand (MW)']
        # ['08/10/2009 15', '67.36', '39.67', '8623.0']
        try:
            try:
                yield QpPoint.from_csvline(line)
            except ValueError, e:
                #~ if line[0].strip().endswith('*'):
                    #~ # Star exists in output (meaning is unknown)
                    #~ # ignore this point.
                    #~ pass
                if line[0].strip() == '' or \
                    line[0].strip() == 'Pool Price' or \
                    line[0].strip() == 'Date (HE)':
                    # Date string is empty.  This is a header line or
                    # blank line.
                    pass
                else:
                    raise
            except IndexError, e:
                # Ignore the line; it does not have the right number of cells.
                # It may, for example, be blank.
                pass
            except decimal.InvalidOperation, e:
                if line[1].strip() == '-':
                    # No price data available. Ignore point.
                    pass
                else:
                    raise
        except (ValueError, IndexError, decimal.InvalidOperation), e:
            #raise ValueError('Unable to parse line {0}: {1}'.format(idx, repr(line)))
            raise ValueError('Unable to parse line ' + str(idx) + ': ' + repr(line))



