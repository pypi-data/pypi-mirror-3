# -*- coding: utf-8 -*-
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
from datetime import date
from datetime import datetime
from datetime import timedelta
from os.path import join
from os.path import dirname
from StringIO import StringIO
from shutil import copyfileobj
import sys
from bz2 import BZ2File
import doctest
from urllib2 import URLError

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

# 3rd Party Required Libraries
import pytz

# Custom Libraries
from aeso import AB_TZ
from aeso import UTC_TZ
from aeso import mpp
from aeso.mpp import _filter_mpp_headers
from aeso._util import UTF8

AESO_BUG_1_CANARY = '''"09/01/2004 01","24:15","11.02"
"09/01/2004 01","24:00","11.04"
"08/31/2004 24","24:00","11.02"
"08/31/2004 24","24:00","72.50"
'''

def ab_to_utc(naive_dt, is_dst = None):
    '''Localizes a naive_dt object to the Alberta timezone, then returns
    the UTC equivalent.'''

    ab_dt = AB_TZ.localize(naive_dt, is_dst = is_dst)
    utc_dt = UTC_TZ.normalize(ab_dt.astimezone(pytz.utc))
    return utc_dt


class TestRemoteShort(unittest.TestCase):
    def assert_expected_start_end_behaviour(self, start_date, end_date):
        DATE_FORMAT = '%m/%d/%Y'

        f = mpp.urlopen(start_date, end_date)
        text = f.read().decode(UTF8)
        self.assertTrue(start_date.strftime(DATE_FORMAT) in text, 'start date should have been included in report')
        self.assertFalse(end_date.strftime(DATE_FORMAT) in text, 'end date should not have been included in report')
        f.close()


    def test_start_and_end(self):
        self.assert_expected_start_end_behaviour(date(2004, 8, 31), date(2004, 9, 1))
        self.assert_expected_start_end_behaviour(date(2004, 1, 1), date(2004, 1, 31))
        self.assert_expected_start_end_behaviour(date(2004, 1, 1), date(2004, 1, 31))

        # Try some sample dates.
        self.assert_expected_start_end_behaviour(date(2009, 12, 11), date(2010, 1, 10))
        self.assert_expected_start_end_behaviour(date(2009, 11, 10), date(2009, 12, 10))
        self.assert_expected_start_end_behaviour(date(2009, 10, 10), date(2009, 11, 9))
        self.assert_expected_start_end_behaviour(date(2009, 10, 1), date(2009, 10, 9))


    def test_reversed_start_and_end(self):
        start_date = date(2004, 8, 31)
        end_date = date(2004, 9, 1)

        f = mpp.urlopen(end_date, start_date)
        try:
            text = f.read().decode(UTF8)
            self.assertTrue('Report end date must be after begin date.' in text, 'expected error text did not appear in %s.' % repr(text))
        finally:
            f.close()


    def _ignore_test_aeso_bug_1(self):
        '''Hour "24" is used alternatively to mean the end of one day
        and the beginning of another.  That is, 2004-31-08 24:00 and
        2004-09-01 24:00 can be used to refer to the same instant.
        Observe the following:

        "09/01/2004 02","01:20","11.03"
        "09/01/2004 02","01:00","20.01"
        "09/01/2004 01","24:26","11.02"
        "09/01/2004 01","24:17","11.02"
        "09/01/2004 01","24:15","11.02" <===
        "09/01/2004 01","24:00","11.04" <=== Where does 24 start and end?
        "08/31/2004 24","24:00","11.02" <===
        "08/31/2004 24","24:00","72.50" <===
        "08/31/2004 24","24:00","11.04"
        "08/31/2004 24","23:00","11.04"
        "08/31/2004 23","22:52","11.04"

        2011-11-25: Something at AESO has changed.  In download now find:

        "09/01/2004 03","02:02","11.00"
        "09/01/2004 03","02:00","11.01"
        "09/01/2004 02","01:41","11.01"
        "09/01/2004 02","01:20","11.03"
        "09/01/2004 02","01:00","20.01"
        "09/01/2004 01","24:26","11.02"
        "09/01/2004 01","24:17","11.02"
        "09/01/2004 01","24:15","11.02"
        "08/31/2004 24","24:00","72.50" <====
        "08/31/2004 24","24:00","11.04" <===
        "09/01/2004 01","24:00","11.04" <==   What's going on here?
        "08/31/2004 24","24:00","11.02" <===
        "08/31/2004 24","23:00","11.04" <====
        "08/31/2004 23","22:52","11.04"

        Disabling test until this is sorted out.
        '''

        start_date = date(2004, 8, 31)
        end_date = date(2004, 9, 2)

        f = mpp.urlopen(start_date, end_date)
        try:
            text = f.read().decode(UTF8)
            self.assertTrue(AESO_BUG_1_CANARY in text, 'expected aeso_bug_1 canary to sing.')
        finally:
            f.close()


    def test_timeout(self):
        start_date = date(2009, 10, 1)
        end_date = date(2010, 1, 10)

        b = BytesIO()
        try:
            if sys.version_info[0:2] in [(2,4), (2,5)]:
                self.assertRaises(ValueError, mpp.dump_mpp, b, start_date, end_date, timeout = 1.5)
            else:
                self.assertRaises(URLError, mpp.dump_mpp, b, start_date, end_date, timeout = 0.000000001)
        finally:
            b.close()


    def test_dump(self):
        DATE_FORMAT = '%m/%d/%Y'

        start_date = date(2010, 1, 1)
        end_date = date(2010, 2, 1)

        buff = BytesIO()
        mpp.dump_mpp(buff, start_date, end_date)
        text = buff.getvalue().decode(UTF8)
        buff.seek(0)

        # Make sure all dates are represented in data
        d = start_date
        while d <= end_date:
            #self.assertTrue(d.strftime(DATE_FORMAT) in text, 'Data missing for {0}'.format(d))
            self.assertTrue(d.strftime(DATE_FORMAT) in text, 'Data missing for ' + str(d))
            d += timedelta(1)



class TestRemoteLong(unittest.TestCase):
    def test_dump(self):
        DATE_FORMAT = '%m/%d/%Y'

        start_date = date(2009, 10, 1)
        end_date = date(2010, 1, 10)

        buff = BytesIO()
        mpp.dump_mpp(buff, start_date, end_date)
        text = buff.getvalue().decode(UTF8)
        buff.seek(0)

        # Make sure all dates are represented in data
        d = start_date
        while d <= end_date:
            #self.assertTrue(d.strftime(DATE_FORMAT) in text, 'Data missing for {0}'.format(d))
            self.assertTrue(d.strftime(DATE_FORMAT) in text, 'Data missing for ' + str(d))
            d += timedelta(1)


class TestMarginalPoolPrice(unittest.TestCase):
    def assertMppDtEquals(self, cells, naive_ab_dt, is_dst = None):
        self.assertEqual(mpp._marginal_pool_price_dt(cells), ab_to_utc(naive_ab_dt, is_dst))


    def test_parse(self):
        test_report = join(dirname(__file__), 'res', 'marginal_pool_price_sample.csv.bz2')
        start_date = date(2009, 1, 1)
        end_date = date(2010, 1, 10)

        f = BZ2File(test_report)
        try:
            rows = list(mpp.parse_mpp_file(f))
        finally:
            f.close()

        for i in xrange(1, len(rows)):
            #self.assertTrue(rows[i].t <= rows[i-1].t, 'Expected time on row {0} to be after row {1} ({2} vs {3})'.format(i, i + 1, rows[i - 1], rows[i]))
            self.assertTrue(rows[i].t <= rows[i-1].t, 'Expected time on row ' + str(i) + ' to be after row ' + str(i+1) + ' (' + repr(rows[i-1]) + ' vs ' + repr(rows[i]) + ')')


    def test_date_handling(self):
        utc_offset = 7

        # aeso_bug_1 compensation
        self.assertMppDtEquals(("09/01/2004 01","24:15","11.02"), datetime(2004, 9, 1, 0, 15))
        self.assertMppDtEquals(("09/01/2004 01","24:00","11.04"), datetime(2004, 9, 1, 0, 0))
        self.assertMppDtEquals(("08/31/2004 24","24:00","11.02"), datetime(2004, 9, 1, 0, 0))
        self.assertMppDtEquals(("08/31/2004 24","24:00","72.50"), datetime(2004, 9, 1, 0, 0))

        # DST tests
        self.assertMppDtEquals(("11/01/2009 04","03:00","28.44"), datetime(2009, 11, 1, 3, 0))
        self.assertMppDtEquals(("11/01/2009 03","02:55","28.44"), datetime(2009, 11, 1, 2, 55))
        self.assertMppDtEquals(("11/01/2009 03","02:39","28.70"), datetime(2009, 11, 1, 2, 39))
        self.assertMppDtEquals(("11/01/2009 03","02:00","29.39"), datetime(2009, 11, 1, 2, 0))
        self.assertMppDtEquals(("11/01/2009 02*","01:31*","30.06"), datetime(2009, 11, 1, 1, 31), False)
        self.assertMppDtEquals(("11/01/2009 02*","01:14*","31.55"), datetime(2009, 11, 1, 1, 14), False)
        self.assertMppDtEquals(("11/01/2009 02*","01:00*","32.25"), datetime(2009, 11, 1, 1, 0), False)
        self.assertMppDtEquals(("11/01/2009 02","01:56","32.25"), datetime(2009, 11, 1, 1, 56), True)
        self.assertMppDtEquals(("11/01/2009 02","01:05","35.67"), datetime(2009, 11, 1, 1, 5), True)
        self.assertMppDtEquals(("11/01/2009 02","01:01","32.00"), datetime(2009, 11, 1, 1, 1), True)
        self.assertMppDtEquals(("11/01/2009 02","01:00","31.50"), datetime(2009, 11, 1, 1, 0), True)
        self.assertMppDtEquals(("11/01/2009 01","24:54","31.55"), datetime(2009, 11, 1, 0, 54))
        self.assertMppDtEquals(("11/01/2009 01","24:48","29.59"), datetime(2009, 11, 1, 0, 48))


if __name__ == '__main__':
    unittest.main()

