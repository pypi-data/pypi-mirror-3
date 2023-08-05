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

'''Contains helpers to access AESO's Available Transfer Capacity report
at <http://itc.aeso.ca/itc/public/atcQuery.do>.  This report lists
transfer capacities over intertie links at given points in time.

AESO notes that these ATC limits might be further imapcted by conditions
on the British Columbia or Saskatchewan grids.  Interested parties
should visit B.C. Hydro's OASIS website
<http://www.oatioasis.com/cwo_default.htm> and SaskPower's OASIS website
<http://www.oatioasis.com/spc/index.html>.

.. warning::
    The available transfer capacity report from AESO suffers from some
    missing data.  More information is available at 
    https://bitbucket.org/kc/pyaeso/issue/5.
'''

########################################################################
## Standard library imports
import csv
from time import strptime
from time import mktime
from datetime import time as datetime_time
from datetime import datetime
from datetime import date
from datetime import timedelta
from decimal import Decimal
import urllib
import urllib2
import shutil
import time


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



def urlopen_atc(start_date, end_date, timeout = None):
    '''Returns a file containing the available transfer capcity report.
    Using this query, Alberta ATC data can be obtained for historical
    dates starting Nov 22, 1999, and for forecasted dates up to six
    months into the future (AESO,
    http://itc.aeso.ca/itc/public/atcQuery.do, retrieved 2010-11-14).
    Due to limitations of the AESO source query end_date - start_date
    must not exceed six months.

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

        >>> # Standard python libraries
        >>> from datetime import date
        >>> from datetime import timedelta
        >>>
        >>> # 3rd Party Libraries
        >>> from aeso import atc
        >>>
        >>> end_date = date.today()
        >>> start_date = end_date - timedelta(1)
        >>>
        >>> f = atc.urlopen_atc(start_date, end_date)
        >>> text = f.read()
        >>> f.close()

    .. note::

        AESO's raw ATC report can be accessed at
        <http://itc.aeso.ca/itc/public/atcQuery.do>.'''

    DATE_FORMAT = '%Y-%m-%d'

    s_from_epoch = time.time() + 5*30*24*60*60 # ~5 months
    ms_from_epoch = 1000. * s_from_epoch
    utc_dt = time.gmtime(s_from_epoch)
    local_dt = time.localtime(s_from_epoch)

    LOCAL_DT_FORMAT = '%Y-%m-%d %H:%M:%s.000 %Z'
    UTC_DT_FORMAT = '%Y-%m-%d %H:%M:%s.000 UTC'

    url = 'http://itc.aeso.ca/itc/public/atcQuery.do'
    parameters = {
        'fileFormat' : 'publicCsvFormatter',
        'startDate' : start_date.strftime(DATE_FORMAT),
        'endDate' : end_date.strftime(DATE_FORMAT),
        # Commenting these next two lines causes internal web server errors! (2009-12-14)
        'availableEffectiveDate' : '943279200000 1999-11-22 07:00:00.000 MST (1999-11-22 14:00:00.000 GMT)',
        'availableExpiryDate' : '%d %s (%s)' % (ms_from_epoch, time.strftime(LOCAL_DT_FORMAT, local_dt), time.strftime(UTC_DT_FORMAT, utc_dt)),
        '' : 'Submit',
    }

    encoded_params = urllib.urlencode(parameters).encode(UTF8)
    #http://itc.aeso.ca/itc/public/atcQuery.do?fileFormat=publicCsvFormatter&startDate=2010-11-10&endDate=2010-11-25&availableEffectiveDate=943279200000+1999-11-22+07%3A00%3A00.000+MST+%281999-11-22+14%3A00%3A00.000+GMT%29&availableExpiryDate=1305439200000+2011-05-15+00%3A00%3A00.000+MDT+%282011-05-15+06%3A00%3A00.000+GMT%29&=Submit
    #print 'opening url: %s?%s' % (url, encoded_params)
    f = _compat_urlopen(url, encoded_params, timeout = timeout)

    return f


def dump_atc(f, start_date, end_date, timeout = None):
    '''Download available transfer capacity data between *start_date* and
    *end_date* and write it to file-object *f*.  Unlike urlopen_atc,
    there is no restriction on the amount of data available.  An
    iterator is used to query data in six-month blocks before it is
    written to *f*.

    :param f: file-like object.
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

        >>> # Standard python libraries
        >>> from tempfile import TemporaryFile
        >>>
        >>> # 3rd Party Libraries
        >>> from aeso import atc
        >>>
        >>> end_date = date.today()
        >>> start_date = end_date - timedelta(1)
        >>>
        >>> f = TemporaryFile()
        >>> atc.dump_atc(f, start_date, end_date)
        >>> f.close()
    '''


    for (start, end) in DayBlockIt(start_date, end_date, 30*6):
        # print 'From', start, 'to', end
        src = urlopen_atc(start, end, timeout = timeout)
        shutil.copyfileobj(src, f)

        if end < end_date:
            time.sleep(2)


def parse_atc_file(f):
    '''Yields :class:`TransferCapacity` objects as extracted from the open
    file-object *f*.  File *f* should contain an available transfer
    capacity report in CSV format.

    :param f: file-like object.

    .. versionadded:: 0.6

    Usage example::

        >>> # Standard library imports
        >>> import datetime
        >>> try:
        ...     # For Python 3
        ...     from io import BytesIO
        ... except ImportError:
        ...     # For Python 2.x
        ...     from StringIO import StringIO as BytesIO
        >>>
        >>> # 3rd Party Libraries
        >>> from aeso import atc
        >>>
        >>> end_date = date.today()
        >>> start_date = end_date - timedelta(1)
        >>>
        >>> f = BytesIO()
        ... try:
        ...   atc.dump_atc(f, start_date, end_date)
        ...   ofs = f.seek(0)
        ...   data = list(atc.parse_atc_file(f))
        ... finally:
        ...   f.close()
        >>>
        >>> # *data* now contains a list of TransferCapacity objects.'''

    #~ Posted As Of: "2009-12-14 16:01:42
    #~ "Date","Hour Ending","BC Export ATC","BC Export Reason","BC Import ATC","BC Import Reason","SK Export ATC","SK Export Reason","SK Import ATC","SK Import Reason",
    #~ 2009-01-01,1,330,"OPP 521 Limit",525,"Opp 312 Limit",35,"",153,""
    #~ 2009-01-01,2,360,"OPP 521 Limit",500,"Opp 312 Limit",35,"",153,""

    date_posted = f.readline()
    column_headings = f.readline()

    # Header lines look like this:
    # "Posted As Of: "2009-12-15 19:36:43
    # "Date","Hour Ending","BC Export ATC","BC Export Reason","BC Import ATC","BC Import Reason","SK Export ATC","SK Export Reason","SK Import ATC","SK Import Reason",

    reader = csv.reader(Utf8Reader(f))
    for idx, line in enumerate(reader):
        # Ignore header lines.   This is done so that files can be concatenated.
        if len(line) == 0:
            # skip blank lines.
            continue
        elif line[0].startswith('Posted'):
            # Ignore first header line
            continue
        elif line[0] == 'Date':
            # Ignore second header line
            continue

        utc_dt = _normalize_atc_dtstr_to_utc(line)

        bc_export_power = line[2]
        bc_export_reason = line[3]
        bc_import_power = line[4]
        bc_import_reason = line[5]
        bc_atc_limit = AtcLimit(AtcLink.BC, bc_import_power, bc_import_reason, bc_export_power, bc_export_reason)

        sk_export_power =  line[6]
        sk_export_reason = line[7]
        sk_import_power = line[8]
        sk_import_reason = line[9]
        sk_atc_limit = AtcLimit(AtcLink.SK, sk_import_power, sk_import_reason, sk_export_power, sk_export_reason)

        capacity = TransferCapacity(utc_dt, [bc_atc_limit, sk_atc_limit])

        yield capacity


class TransferCapacity(object):
    '''Available Transfer Capacity Limit.'''

    def __init__(self, t, links):
        self._t = t
        self._links = links

    @property
    def t(self):
        '''Time (:class:`datetime.datetime`) at which intertie link limits are valid.
        '''
        return self._t


    @property
    def links(self):
        '''List of :class:`AtcLimit` objects.  List length is equal to
        the number of values in the :class:`AtcLink` enumeration.
        Presently :class:`AtcLink` has two values: Saskatchewan and
        BC (pyaeso 0.6, 2010-11-14).'''

        return self._links


class AtcLimit(object):
    '''Represents transfer limit for an intertie.'''

    def __init__(self, id, import_power, import_reason, export_power, export_reason):
        self._id = id
        self._import_power = Decimal(import_power)
        self._import_reason = import_reason
        self._export_power = Decimal(export_power)
        self._export_reason = export_reason

    @property
    def id(self):
        '''Value from :class:`AtcLink` enumeration.'''
        return self._id

    @property
    def import_power(self):
        '''Imported power (:class:`decimal.Decimal`).'''
        return self._import_power

    @property
    def import_reason(self):
        ''':class:`str` property.'''
        return self._import_reason

    @property
    def export_power(self):
        ''':class:`decimal.Decimal` property.'''
        return self._export_power

    @property
    def export_reason(self):
        ''':class:`str` property.'''
        return self._export_reason




def _normalize_atc_dtstr_to_utc(cells):
    # Sample line
    # 2009-01-01,1,330,"OPP 521 Limit",525,"Opp 312 Limit",35,"",153,""
    DT_FORMAT = "%Y-%m-%d"

    # This series is to support Python < 2.5
    struct_time = strptime(cells[0], DT_FORMAT)
    timestamp = mktime(struct_time)
    d = datetime.fromtimestamp(timestamp).date()

    # 2000-10-28,24,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,1,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,2,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,2*,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,4,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,5,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,6,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"

    starred = False # Does the hour column have a "*" after the number?

    # Fiddle with "hours"
    hour_str = cells[1]
    try:
        hour = int(hour_str)
    except ValueError:
        # String may look like '2*'.  Strip off traling '*'
        if hour_str.endswith('*'):
            hour_str = hour_str[:-1]
            hour = int(hour_str)
            starred = True
        else:
            # No trailing '*'.  What happened?  Re-reaise exception
            raise

    if hour == 24:
        hour = 0
        d = d + timedelta(1)

    t = datetime_time(hour)
    dt = datetime.combine(d, t)
    dt_minus_one_h = dt - timedelta(hours = 1)


    is_dst = None
    try:
        AB_TZ.localize(dt_minus_one_h, is_dst = is_dst)
    except pytz.AmbiguousTimeError:
        # This is the hour after a DST -> Non-DST transition
        if hour == 2 and not starred:
            hour = 1
            is_dst = False
        elif hour == 2 and starred:
            pass
        else:
            # Should never happen.
            raise

    t = datetime_time(hour)
    dt = datetime.combine(d, t)
    try:
        ab_dt = AB_TZ.localize(dt, is_dst = is_dst)
    except pytz.AmbiguousTimeError:
        if hour == 1:
            ab_dt = AB_TZ.localize(dt, is_dst = True)
        else:
            # Should never happen.
            raise
    except pytz.NonExistentTimeError:
        if hour == 2:
            t = datetime_time(3)
            ab_dt = AB_TZ.localize(datetime.combine(dt, t))
        else:
            # Should never happen
            raise

    # convert from Alberta time to UTC time
    return pytz.utc.normalize(ab_dt.astimezone(pytz.utc))


class AtcLink(object):
    '''Enumeration of import/export transmission links.
    '''

    #: Transfer link to British Columbia.
    BC = 'BC'

    #: Transfer link to Saskatchewan.
    SK = 'SK'



