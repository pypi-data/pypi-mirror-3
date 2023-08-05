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

import unittest
import os.path
from datetime import datetime
from datetime import date
import bz2

from shutil import copyfileobj
import sys

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO


# 3rd Party Required Libraries
import pytz

# Custom Libraries
from pyaeso import ets


class TestDayBlockIt(unittest.TestCase):
    def test_iteration(self):
        start_date = date(1995, 1, 1)
        end_date = date(1995, 1, 10)

        it = ets.DayBlockIt(start_date, end_date, 10)
        self.assertEqual(it.next(), (start_date, end_date))
        self.assertRaises(StopIteration, it.next)

        it = ets.DayBlockIt(start_date, end_date, 5)
        self.assertEqual(it.next(), (date(1995, 1, 1), date(1995, 1, 5)))
        self.assertEqual(it.next(), (date(1995, 1, 6), date(1995, 1, 10)))
        self.assertRaises(StopIteration, it.next)


    def test_negative(self):
        start_date = date(1995, 1, 10)
        end_date = date(1995, 1, 1)

        it = ets.DayBlockIt(start_date, end_date, -10)
        self.assertEqual(it.next(), (start_date, end_date))

        it = ets.DayBlockIt(start_date, end_date, -5)
        self.assertEqual(it.next(), (date(1995, 1, 10), date(1995, 1, 6)))
        self.assertEqual(it.next(), (date(1995, 1, 5), date(1995, 1, 1)))
        self.assertRaises(StopIteration, it.next)


class TestPoolPrice(unittest.TestCase):
    def test_parse_pool_price_file(self):
        test_series_file = os.path.join(os.path.dirname(__file__), 'res', 'ets_testseries.csv.bz2')

        f = bz2.BZ2File(test_series_file)
        try:
            points = list(ets.parse_pool_price_file(f))
            self.assertEqual(len(points), 6728)
        finally:
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
        for datetime_str, expected_utc_datetime in lut.items():
            actual_dt = ets._normalize_pool_price_dtstr_to_utc(datetime_str)
            expected_dt = pytz.utc.localize(expected_utc_datetime)
            self.assertEqual(actual_dt, expected_dt)

        # Test handling of 24
        # '03/02/2005 24' -> 2009-03-03 0
        self.assertEqual(ets._normalize_pool_price_dtstr_to_utc('03/02/2005 24'), ets.ALBERTA_TZ.localize(datetime(2005, 3, 3, 0)).astimezone(pytz.utc))


class TestAssetList(unittest.TestCase):
    def test_parse_asset_list_file(self):
        test_series_file = os.path.join(os.path.dirname(__file__), 'res', 'asset_list.csv.bz2')

        f = bz2.BZ2File(test_series_file)
        try:
            assets = list(ets.parse_asset_list_file(f))
            self.assertEqual(len(assets), 1862)
            for asset in assets:
                for char in '<>':
                    # ETS embeds HTML anchors in the asset name.  Test to
                    # make sure they have been properly stripped out.
                    self.assertTrue(char not in asset.asset_name)
        finally:
            f.close()


class TestRemoteShort(unittest.TestCase):
    def test_asset_list_connection(self):
        f = BytesIO()
        try:
            ets.dump_asset_list(f)
            assets = list(ets.parse_asset_list_file(f))
        finally:
            f.close()

    def test_pool_price_connection(self):
        start_date = date(2011, 1, 1)
        end_date = date(2011, 2, 1)

        f = BytesIO()
        try:
            ets.dump_pool_price(f, start_date, end_date)
            f.seek(0)
            points = list(ets.parse_pool_price_file(f))
        finally:
            f.close()


class TestRemoteLong(unittest.TestCase):
    def test_pool_price_connection(self):
        f = BytesIO()
        try:
            ets.dump_pool_price(f)
            f.seek(0)
            points = list(ets.parse_pool_price_file(f))
        finally:
            f.close()


if __name__ == '__main__':
    unittest.main()
