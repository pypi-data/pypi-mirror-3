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

'''The Energy Trading System (ETS) is a website <http://ets.aeso.ca>
made available by the Alberta Electric System Operator (AESO)
<http://www.aeso.ca> for energy trading and public information
purposes.  The ets module makes access to many of the reporting
functions easier.  This is useful for the contruction of market models
and various heuristic "expert" trading systems.'''

# Standard library imports
import urllib
import urllib2
import csv
import datetime
from datetime import timedelta
import time
import decimal
from decimal import Decimal
import shutil
import time
import sys
import re
from time import strptime
from time import mktime
import codecs

# Other 3rd Party Libraries
import pytz

UTF8 = 'utf-8'
Utf8Reader = codecs.getreader(UTF8)
Utf8Writer = codecs.getwriter(UTF8)

class DayBlockIt(object):
    '''Steps over blocks of days between two time periods.  Each call to
    next() will return a 2-tuple containing a start date and end date as
    far apart as is permitted by the /days/ parameter.

    Example
    >>> from pyaeso import ets
    >>> import datetime
    >>>
    >>> start_date = datetime.date(1995, 1, 1)
    >>> end_date = datetime.date(1995, 1, 10)
    >>>
    >>> it = ets.DayBlockIt(start_date, end_date, 4)
    >>> it.next()
    (datetime.date(1995, 1, 1), datetime.date(1995, 1, 4))
    >>> it.next()
    (datetime.date(1995, 1, 5), datetime.date(1995, 1, 8))
    >>> it.next()
    (datetime.date(1995, 1, 9), datetime.date(1995, 1, 10))
    >>> it.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "pyaeso/ets.py", line 65, in next
        raise StopIteration()
    StopIteration
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

        self._delta = datetime.timedelta(days)
        self._delta_less_one = datetime.timedelta(days - days / abs(days))
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


def urlopen_pool_price(start_date, end_date):
    '''Returns a file-like object attached to the ETS pool price report
    webservice.  Note that the webservice limits the number of days
    that can be queried to 721 days (as of 2009-11-12).

    :param start_date: :class:`datetime.date`
    :param end_date: :class:`datetime.date`
    :rtype: file-like object as returned by urlopen.

    Usage example::

        >>> # 3rd Party Libraries
        >>> from pyaeso import ets
        >>>
        >>> end_date = datetime.date.today()
        >>> start_date = end_date - datetime.timedelta(1)
        >>>
        >>> f = ets.urlopen_pool_price(start_date, end_date)
        >>> print f.read()
        >>> f.close()

    .. note::

        The raw ETS pool price report can be accessed at
        <http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet>.
    '''
    DATE_FORMAT = '%m%d%Y'

    url = 'http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet'
    parameters = {
        'contentType' : 'csv',
        'beginDate' : start_date.strftime(DATE_FORMAT),
        'endDate' : end_date.strftime(DATE_FORMAT),
    }

    encoded_params = urllib.urlencode(parameters).encode('utf-8')
    #http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet?contentType=html&beginDate=08012009&endDate=08112009
    f = urllib2.urlopen(url, encoded_params)

    return f


def urlopen_asset_list():
    '''Returns a file-like object containing data returned by the ETS
    asset list webservice.

    :rtype: file-like object as returned by urlopen.

    .. versionadded:: 0.2

    Usage example::

        >>> # 3rd Party Libraries
        >>> from pyaeso import ets
        >>>
        >>> f = ets.urlopen_asset_list()
        >>> print f.read()
        >>> f.close()


    .. note::

        The raw ETS asset list report can be accessed at
        <http://ets.aeso.ca/ets_web/ip/Market/Reports/AssetListReportServlet>.
    '''

    url = 'http://ets.aeso.ca/ets_web/ip/Market/Reports/AssetListReportServlet'
    parameters = {
        'contentType' : 'csv',
    }

    encoded_params = urllib.urlencode(parameters).encode(UTF8)
    #http://ets.aeso.ca/ets_web/ip/Market/Reports/AssetListReportServlet?contentType=html
    f = urllib2.urlopen(url, encoded_params)

    return f


def dump_pool_price(f_out, start_date = datetime.date(1995, 1, 1), end_date = datetime.date.today() + datetime.timedelta(1)):
    '''Downloads market equilibrium data from ETS and writes it to the
    file object f_out.  Unlike urlopen_pool_price there is no
    restriction on the amount of data that can be requested.  Internally
    an iterator is used to query data in 721 day blocks before it is
    written to f_out.

    Usage example::

        >>> # 3rd Party Libraries
        >>> from pyaeso import ets
        >>>
        >>> end_date = datetime.date.today()
        >>> start_date = end_date - datetime.timedelta(1)
        >>>
        >>> f = open('pool_price_report.csv', 'w')
        >>> ets.dump_pool_price(f, start_date, end_date)
        >>> f.close()
    '''

    for (start, end) in DayBlockIt(start_date, end_date, 721):
        # print 'From', start, 'to', end
        f_in = urlopen_pool_price(start, end)
        shutil.copyfileobj(f_in, f_out)

        if end < end_date:
            time.sleep(10)


def dump_asset_list(f_out):
    '''Downloads asset list report and writes it to file-object *f*.

    .. versionadded:: 0.2

    Usage example::

        >>> # 3rd Party Libraries
        >>> from pyaeso import ets
        >>>
        >>> f = open('asset_list_report.csv', 'w')
        >>> ets.dump_asset_list(f)
        >>> f.close()
    '''

    f_in = urlopen_asset_list()
    shutil.copyfileobj(f_in, f_out)


_RE_DATEHOUR = re.compile('(\d+)/(\d+)/(\d+) (\d+)$')
ALBERTA_TZ = pytz.timezone('America/Edmonton')

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
        t = datetime.datetime.fromtimestamp(timestamp)

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
                t = datetime.datetime(year, month, day, 0) + datetime.timedelta(1)
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
        dst_test_time = datetime.datetime(t.year, t.month, t.day, t.hour - 1)
        try:
            ALBERTA_TZ.localize(dst_test_time, is_dst = None)
        except pytz.AmbiguousTimeError:
            # This "2" occurs after a DST transition
            ab_dt = ALBERTA_TZ.localize(dst_test_time, is_dst = False)
        else:
            # This "2" does not occur after a DST transition; no is_dst necessary
            ab_dt = ALBERTA_TZ.localize(t, is_dst = None)
    else:
        try:
            ab_dt = ALBERTA_TZ.localize(t, is_dst = None)
        except pytz.AmbiguousTimeError:
            if t.hour == 1 and not starred:
                # First hour occurring before a DST jump.
                ab_dt = ALBERTA_TZ.localize(t, is_dst = True)
            else:
                raise

    # convert from Alberta time to UTC time
    return pytz.utc.normalize(ab_dt.astimezone(pytz.utc))


class QpPoint(object):
    def __init__(self, t, price, demand):
        self._t = t
        self._price = Decimal(price)
        self._demand = Decimal(demand)

    @property
    def t(self):
        return self._t

    @property
    def price(self):
        return self._price

    @property
    def demand(self):
        return self._demand

    @classmethod
    def from_csvline(cls, line):
        # Sample line:
        # ['Date (HE)', 'Price ($)', '30Ravg ($)', 'System Demand (MW)']
        # ['08/10/2009 15', '67.36', '39.67', '8623.0']

        # Normalize time string to UTC time.
        t = _normalize_pool_price_dtstr_to_utc(line[0])
        price = Decimal(line[1])
        demand = Decimal(line[3])

        point = QpPoint(t, price, demand)

        return point


def parse_pool_price_file(f):
    '''Yields :class:`QpPoint` objects as extracted from the open CSV
    file-object *f*.

    Usage example::

        >>> # Standard library imports
        >>> from StringIO import StringIO
        >>> import datetime
        >>>
        >>> # 3rd Party Libraries
        >>> from pyaeso import ets
        >>>
        >>> end_date = datetime.date.today()
        >>> start_date = end_date - datetime.timedelta(1)
        >>>
        >>> f = StringIO()
        >>> ets.dump_pool_price(f, start_date, end_date)
        >>> f.seek(0)
        >>> data = list(ets.parse_pool_price_file(f))
        >>> f.close()
        >>>
        >>> print "Yesterday's market clearing price/demand points."
        >>> for d in data:
        ...   ab_time = d.t.astimezone(ets.ALBERTA_TZ)
        ...   print '{0} ${1} {2}MW'.format(ab_time, d.price, d.demand)

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


class AssetType(object):
    SOURCE = 'source'
    SINK = 'sink'

    _lut = {
        SOURCE : 'source',
        SINK : 'sink',
    }

    @classmethod
    def from_str(klass, string):
        normalized = string.strip().lower()

        try:
            return klass._lut[normalized]
        except KeyError:
            #raise ValueError('Unknown asset type {0}.'.format(repr(string)))
            raise ValueError('Unknown asset type ' + repr(string))


class AssetStatus(object):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    RETIRED = 'retired'
    SUSPENDED = 'suspended'

    _lut = {
        ACTIVE : 'active',
        INACTIVE : 'inactive',
        RETIRED : 'retired',
        SUSPENDED : 'suspended',
    }

    @classmethod
    def from_str(klass, string):
        normalized = string.strip().lower()

        try:
            return klass._lut[normalized]
        except KeyError:
            raise ValueError('Unknown asset status ' + repr(string))
            #raise ValueError('Unknown asset status {0}.'.format(repr(string)))


_RE_ASSETNAME = re.compile('<[^>]*>\s*<[^>]*>(.*)')
def _normalize_asset_name(string):
    #'<A NAME=3Anchor"></A>301A 3070 Ret #1'
    match = _RE_ASSETNAME.match(string)
    if match:
        return match.group(1)
    else:
        return string


class Asset(object):
    def __init__(self, asset_name, asset_id, asset_type, status, participant_name, participant_id):
        self._asset_name = asset_name
        self._asset_id = asset_name
        self._asset_type = asset_type
        self._status = status
        self._participant_name = participant_name
        self._participant_id = participant_id

    @property
    def asset_name(self):
        return self._asset_name

    @property
    def asset_id(self):
        return self._asset_id

    @property
    def asset_type(self):
        return self._asset_type

    @property
    def status(self):
        return self._status

    @property
    def participant_name(self):
        return self._participant_name

    @property
    def participant_id(self):
        return self._participant_id


def parse_asset_list_file(f):
    '''Yields Asset objects extracted from the open file-object *f*.

    .. versionadded:: 0.2

    Usage example::

        >>> # 3rd Party Libraries
        >>> from pyaeso import ets
        >>>
        >>>
        >>> f = ets.urlopen_asset_list()
        >>> assets = list(ets.parse_asset_list_file(f))
        >>> f.close()
    '''
    reader = csv.reader(Utf8Reader(f))
    for idx, line in enumerate(reader):
        # ["Williams Lk Gen St - BCH","IPI1","Source","Retired","Inland Pacific Energy Services","IPES"]
        try:
            if idx > 2 and len(line) > 0:
                yield Asset(_normalize_asset_name(line[0]), line[1], AssetType.from_str(line[2]), AssetStatus.from_str(line[3]), line[4], line[5])
        except IndexError:
            # raised when number of cells in row is incorrect.
            #raise ValueError('Unable to parse line {0}: {1}'.format(idx, repr(line)))
            raise ValueError('Unable to parse line ' + str(idx) + ': ' + repr(line))


def urlopen_marginal_pool_price(start_date, end_date):
    '''Returns a file-like object attached to the ETS marginal pool
    price report.  The report is limited by AESO to returning 31 days of
    information (2010-02-09).  The report will include data for
    start_date but not for end_date.  The earliest date for which
    marginal price information is available is 1999-10-01 (2010-02-10).
    *start_date* must be before *end_date*.

    :param start_date: :class:`datetime.date`
    :param end_date: :class:`datetime.date`
    :rtype: file-like object as returned by urlopen.

    .. versionadded:: 0.4

    Usage example::

        >>> # Standard library imports
        >>> from datetime import date
        >>> from datetime import timedelta
        >>>
        >>> # 3rd Party Libraries
        >>> from pyaeso.ets import urlopen_marginal_pool_price
        >>>
        >>> start_date = datetime.date(2010, 1, 1)
        >>> end_date = datetime.date(2010, 1, 31) + datetime.timedelta(1)
        >>> # If you want to include all days in january, must add 24 hours.
        >>> # Remember that there will be no information returned for
        >>> # *end_date* itself, only for dates prior to it!
        >>>
        >>> f = urlopen_marginal_pool_price(start_date, end_date)
        >>> text = f.read()
    '''

    DATE_FORMAT = '%m%d%Y'
    url = 'http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalSystemMarginalPriceReportServlet'
    parameters = {
        'contentType' : 'csv',
        'beginDate' : start_date.strftime(DATE_FORMAT),
        'endDate' : end_date.strftime(DATE_FORMAT),
    }

    encoded_params = urllib.urlencode(parameters).encode('utf-8')
    #http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalSystemMarginalPriceReportServlet?beginDate=02012010&endDate=02092010&contentType=csv
    f = urllib2.urlopen(url, encoded_params)

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
    naive_dt = datetime.datetime.fromtimestamp(timestamp)
    if add_one_day:
        naive_dt += datetime.timedelta(1)

    # Convert naive datetime object to UTC.
    try:
        ab_dt = ALBERTA_TZ.localize(naive_dt, is_dst = is_dst)
    except pytz.AmbiguousTimeError:
        ab_dt = ALBERTA_TZ.localize(naive_dt, is_dst = True)
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

    shutil.copyfileobj(reader, writer)


def dump_marginal_pool_price(dst, start_date = datetime.date(1999, 10, 1), end_date = datetime.date.today() + datetime.timedelta(1)):
    '''Downloads market marginal pool price data from ETS and writes it
    to file object *dst*.  Unlike urlopen_marginal_pool_price there is
    no limit on the amount of data that can be requested.  Internally
    an iterator is used to query data in 31 day blocks before it is
    written to *dst*.  Output is included for start_date but excludes
    data for end_date.

    :param dst: writeable file object
    :param start_date: :class:`datetime.date`
    :param end_date: :class:`datetime.date`

    .. versionadded:: 0.4

    Usage example::

        >>> # Standard library imports
        >>> from datetime import date
        >>> from datetime import timedelta
        >>> from StringIO import StringIO
        >>>
        >>> # 3rd Party Libraries
        >>> from pyaeso.ets import dump_marginal_pool_price
        >>>
        >>> start_date = datetime.date(2010, 1, 1)
        >>> end_date = datetime.date(2010, 1, 31) + datetime.timedelta(1)
        >>> # Remember, no data will be returned on end_date itself!
        >>>
        >>> f = StringIO()
        >>> dump_marginal_pool_price(f)
        >>> text = f.getvalue()
    '''

    if start_date > end_date:
        raise ValueError('start_date must be before end_date')

    first_file = True
    for block_end, block_start in DayBlockIt(end_date, start_date, -31):
        f = urlopen_marginal_pool_price(block_start, block_end + timedelta(1))
        if first_file:
            shutil.copyfileobj(f, dst)
            first_file = False
        else:
            _filter_mpp_headers(f, dst)
        f.close()


class PPoint(object):
    '''A price at a given point in time.

    Since PPoint objects will iterate over their properties t, and
    price, they can be unpacked:

    >>> from datetime import datetime
    >>> point = PPoint(datetime(2010, 2, 12, 10, 36), 4.56)
    >>> t, price = point
    '''
    def __init__(self, t, price):
        self._t = t
        self._price = Decimal(price)
        self._iterable = None

    @property
    def t(self):
        return self._t

    @property
    def price(self):
        return self._price

    def __iter__(self):
        if self._iterable is None:
            self._iterable = [self.t, self.price]

        return iter(self._iterable)


def parse_marginal_pool_price_file(f):
    '''Yields a :class:`PPoint` object for each price point in marginal
    pool price data report file-object *f*.  As always, times are UTC.

    .. versionadded:: 0.4

    Usage example::

        >>> # Standard library imports
        >>> from datetime import date
        >>> from datetime import timedelta
        >>> from StringIO import StringIO
        >>>
        >>> # 3rd Party Libraries
        >>> from pyaeso.ets import dump_marginal_pool_price, parse_marginal_pool_price_file
        >>> from pyaeso import ets
        >>>
        >>> start_date = datetime.date(2010, 1, 1)
        >>> end_date = datetime.date(2010, 1, 31) + datetime.timedelta(1)
        >>> # Remember, no data will be returned on end_date itself!
        >>>
        >>> f = StringIO()
        >>> dump_marginal_pool_price(f)
        >>> f.seek(0)
        >>>
        >>> points = list(parse_marginal_pool_price_file(f))
        >>>
        >>> for pp in points:
        ...   # PPoint objects are iterable and can be unpacked!
        ...   time, price = pp
        ...   print time.astimezone(ets.ALBERTA_TZ), '$' + str(price)
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
                raise ValueError('found ' + str(len(cells)) + ' where ' + str(NUM_EXPECTED_CELLS) + ' were expected ("' + str(cells) + '").')
        except (decimal.InvalidOperation, ValueError), e:
            if first_valid_line:
                #raise ValueError('On row {0}, {1}'.format(idx, str(e)))
                raise ValueError('On row ' + str(idx) + ', ' + str(e))
