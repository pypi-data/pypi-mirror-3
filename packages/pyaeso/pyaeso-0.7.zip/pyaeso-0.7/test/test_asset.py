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
#~ from datetime import datetime
#~ from datetime import date
#~ from datetime import timedelta
import unittest
import doctest
import sys
import os
import bz2
from urllib2 import URLError

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO


########################################################################
## Import 3rd party modules
#~ import pytz


########################################################################
## AESO Modules
from aeso import asset


class TestAssetList(unittest.TestCase):
    def test_parse_asset_list_file(self):
        test_series_file = os.path.join(os.path.dirname(__file__), 'res', 'asset_list.csv.bz2')

        f = bz2.BZ2File(test_series_file)
        try:
            assets = list(asset.parse_asset_list_file(f))
            self.assertEqual(len(assets), 1862)
            for a in assets:
                for char in '<>':
                    # ETS embeds HTML anchors in the asset name.  Test to
                    # make sure they have been properly stripped out.
                    self.assertTrue(char not in a.asset_name)
        finally:
            f.close()


class TestAssetRemote(unittest.TestCase):
    def test_timeout(self):
        b = BytesIO()
        try:
            if sys.version_info[0:2] in [(2,4), (2,5)]:
                self.assertRaises(ValueError, asset.dump_asset_list, b, timeout = 1.5)
            else:
                self.assertRaises(URLError, asset.dump_asset_list, b, timeout = 0.000000001)
        finally:
            b.close()


    def test_asset_list_connection(self):
        f = BytesIO()
        try:
            asset.dump_asset_list(f)
            assets = list(asset.parse_asset_list_file(f))
        finally:
            f.close()


if __name__ == '__main__':
    unittest.main()

