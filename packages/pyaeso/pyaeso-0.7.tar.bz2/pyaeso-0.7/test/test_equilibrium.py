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

########################################################################
## Standard library imports
import unittest
from os.path import dirname
from os.path import join
import doctest
from datetime import date
from datetime import datetime
#from datetime import timedelta
import sys
import bz2
from urllib2 import URLError

try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO

########################################################################
## AESO Modules
from aeso import AB_TZ
from aeso import UTC_TZ
from aeso import equilibrium


class TestEquilibrium(unittest.TestCase):
    def test_parse_pool_price_file(self):
        test_series_file = join(dirname(__file__), 'res', 'ets_testseries.csv.bz2')

        f = bz2.BZ2File(test_series_file)
        points = list(equilibrium.parse_equilibrium_file(f))
        self.assertEqual(len(points), 6728)
        f.close()


    def test_datetime_normalization(self):
        # Test DST handling
        lut = {
            # DST active
            "10/26/1996 00" : datetime(1996, 10, 26, 6),
            "10/26/1996 01" : datetime(1996, 10, 26, 7),
            "10/26/1996 02" : datetime(1996, 10, 26, 8),
            "10/26/1996 03" : datetime(1996, 10, 26, 9),

            # DST ends this day
            "10/27/1996 00" : datetime(1996, 10, 27, 6),
            "10/27/1996 01" : datetime(1996, 10, 27, 7),
            "10/27/1996 02" : datetime(1996, 10, 27, 8),
            "10/27/1996 02*" : datetime(1996, 10, 27, 9),
            "10/27/1996 03" : datetime(1996, 10, 27, 10),

            # DST inactive
            "10/28/1996 00" : datetime(1996, 10, 28, 7),
            "10/28/1996 01" : datetime(1996, 10, 28, 8),
            "10/28/1996 02" : datetime(1996, 10, 28, 9),
            "10/28/1996 03" : datetime(1996, 10, 28, 10),
        }
        for datetime_str, expected_utc_datetime in list(lut.items()):
            actual_dt = equilibrium._normalize_pool_price_dtstr_to_utc(datetime_str)
            expected_dt = UTC_TZ.localize(expected_utc_datetime)
            self.assertEqual(actual_dt, expected_dt)

        # Test handling of 24
        # '03/02/2005 24' -> 2009-03-03 0
        self.assertEqual(equilibrium._normalize_pool_price_dtstr_to_utc('03/02/2005 24'), AB_TZ.localize(datetime(2005, 3, 3, 0)).astimezone(UTC_TZ))


class TestRemoteShort(unittest.TestCase):
    def test_timeout(self):
        b = BytesIO()
        try:
            if sys.version_info[0:2] in [(2,4), (2,5)]:
                self.assertRaises(ValueError, equilibrium.dump_equilibrium, b, timeout = 1.5)
            else:
                self.assertRaises(URLError, equilibrium.dump_equilibrium, b, timeout = 0.0000000000001)
        finally:
            b.close()


    def test_pool_price_connection(self):
        start_date = date(2011, 1, 1)
        end_date = date(2011, 2, 1)

        f = BytesIO()
        try:
            equilibrium.dump_equilibrium(f, start_date, end_date)
            f.seek(0)
            points = list(equilibrium.parse_equilibrium_file(f))
        finally:
            f.close()


class TestRemoteLong(unittest.TestCase):
    def test_pool_price_connection(self):
        f = BytesIO()
        try:
            equilibrium.dump_equilibrium(f)
            f.seek(0)
            points = list(equilibrium.parse_equilibrium_file(f))
        finally:
            f.close()


if __name__ == '__main__':
    unittest.main()

