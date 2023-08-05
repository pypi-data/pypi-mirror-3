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

from os.path import dirname
from os.path import join

import bz2
import sys

from StringIO import StringIO
from urllib2 import URLError

import doctest

# Custom libraries
from aeso import AB_TZ
from aeso import eventlog

class TestEventLog(unittest.TestCase):
    def test_parse_asset_list_file(self):
        test_file = join(dirname(__file__), 'res', 'RealTimeShiftReportServlet.csv.bz2')
        f = bz2.BZ2File(test_file)

        num_rows = 0
        for dt, entry in eventlog.parse_eventlog_file(f):
                num_rows += 1
                #print dt.astimezone(AB_TZ), entry
        f.close()
        self.assertEqual(num_rows, 29)


class TestEventLogWebservice(unittest.TestCase):
    def test_timeout(self):
        b = StringIO()
        try:
            if sys.version_info[0:2] in [(2,4), (2,5)]:
                self.assertRaises(ValueError, eventlog.urlopen, timeout = 1.5)
            else:
                self.assertRaises(URLError, eventlog.urlopen, timeout = 0.000000001)
        finally:
            b.close()


    def test_parse_asset_list_file(self):
        f = eventlog.urlopen()
        rows = list(eventlog.parse_eventlog_file(f))
        f.close()
        self.assertTrue(len(rows) > 5)


if __name__ == '__main__':
    unittest.main()

