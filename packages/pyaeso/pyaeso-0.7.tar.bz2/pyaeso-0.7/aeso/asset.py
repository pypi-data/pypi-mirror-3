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

'''Helpers to access AESO's asset list at
<http://ets.aeso.ca/ets_web/ip/Market/Reports/AssetListReportServlet>.
'''

########################################################################
## Standard library imports
import csv
import shutil
import re
import urllib


# import custom libraries
from aeso._util import (
  DayBlockIt,
  _compat_urlopen,
  Utf8Reader,
  UTF8
)


def urlopen_asset_list(timeout = None):
    '''Returns a file-like object containing data returned by the ETS
    asset list webservice.

    :param timeout: optional parameter specifying timeout in seconds for
        blocking operations like the connection attempt.  If operation
        times out :class:`urllib2.URLError` will be raised.  ValueError
        will be raised in Python 2.4 and 2.5 if this parameter is set to
        anything but None.
    :rtype: file-like object.

    .. versionadded:: 0.6

    .. versionadded:: 0.7
        timeout parameter.

    Usage example::

        >>> # 3rd Party Libraries
        >>> from aeso import asset
        >>>
        >>> f = asset.urlopen_asset_list()
        >>> text = f.read()
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
    f = _compat_urlopen(url, encoded_params, timeout = timeout)

    return f


def dump_asset_list(f_out, timeout = None):
    '''Downloads asset list report and writes it to file-object *f*.

    :param f_out: file-like object to write asset list to.
    :param timeout: optional parameter specifying timeout in seconds for
        blocking operations like the connection attempt.  If operation
        times out :class:`urllib2.URLError` will be raised.  ValueError
        will be raised in Python 2.4 and 2.5 if this parameter is set to
        anything but None.

    .. versionadded:: 0.6

    .. versionadded:: 0.7
        timeout parameter.

    Usage example::

        >>> try:
        ...   from io import BytesIO
        ... except ImportError:
        ...   from StringIO import StringIO as BytesIO
        >>> # 3rd Party Libraries
        >>> from aeso import asset
        >>>
        >>> f = BytesIO()
        >>> try:
        ...   asset.dump_asset_list(f)
        ... finally:
        ...   f.close()
    '''

    f_in = urlopen_asset_list(timeout = timeout)
    shutil.copyfileobj(f_in, f_out)


_RE_DATEHOUR = re.compile('(\d+)/(\d+)/(\d+) (\d+)$')


class AssetType(object):
    '''Asset type enumeration.

    .. versionadded:: 0.6
    '''

    #:
    SOURCE = 'source'

    #:
    SINK = 'sink'

    _lut = {
        SOURCE : 'source',
        SINK : 'sink',
    }

    @classmethod
    def from_str(klass, string):
        '''Converts some simple strings to enumeration values.'''
        normalized = string.strip().lower()

        try:
            return klass._lut[normalized]
        except KeyError:
            #raise ValueError('Unknown asset type {0}.'.format(repr(string)))
            raise ValueError('Unknown asset type ' + repr(string))


class AssetStatus(object):
    '''Asset state enumeration.

    .. versionadded:: 0.6
    '''

    #:
    ACTIVE = 'active'

    #:
    INACTIVE = 'inactive'

    #:
    RETIRED = 'retired'

    #:
    SUSPENDED = 'suspended'

    _lut = {
        ACTIVE : 'active',
        INACTIVE : 'inactive',
        RETIRED : 'retired',
        SUSPENDED : 'suspended',
    }

    @classmethod
    def from_str(klass, string):
        '''Converts some simple strings to enumeration values.'''
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
    '''Represents an asset be it an :class:`AssetType.SINK` and :class:`AssetType.SOURCE`

    .. versionadded:: 0.6
    '''

    def __init__(self, asset_name, asset_id, asset_type, status, participant_name, participant_id):
        self._asset_name = asset_name
        self._asset_id = asset_name
        self._asset_type = asset_type
        self._status = status
        self._participant_name = participant_name
        self._participant_id = participant_id

    @property
    def asset_name(self):
        ''':class:`str` property.'''
        return self._asset_name

    @property
    def asset_id(self):
        ''':class:`str` property.'''
        return self._asset_id

    @property
    def asset_type(self):
        ''':class:`AssetType` property.'''
        return self._asset_type

    @property
    def status(self):
        ''':class:`AssetStatus` property.'''
        return self._status

    @property
    def participant_name(self):
        ''':class:`str` property.'''
        return self._participant_name

    @property
    def participant_id(self):
        ''':class:`str` property.'''
        return self._participant_id


def parse_asset_list_file(f):
    '''Yields Asset objects extracted from the open file-object *f*.

    .. versionadded:: 0.6

    Usage example::

        >>> # 3rd Party Libraries
        >>> from aeso import asset
        >>>
        >>>
        >>> f = asset.urlopen_asset_list()
        >>> assets = list(asset.parse_asset_list_file(f))
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

