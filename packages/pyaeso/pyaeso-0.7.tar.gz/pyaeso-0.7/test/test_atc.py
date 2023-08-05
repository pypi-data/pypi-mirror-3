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
from datetime import datetime
from datetime import date
from datetime import timedelta
import unittest
import doctest
import sys
from os.path import join
import bz2
from urllib2 import URLError
from shutil import copyfileobj

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO



########################################################################
## AESO Modules
from aeso import UTC_TZ
from aeso import AB_TZ
from aeso import atc

import env


# Problems observed in AESO data.
expected_missing_dts = [
    # 2000-10-28,23,600,"RAS Limitation",550,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-28,24,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,1,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,2,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,2*,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,4,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,5,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    # 2000-10-29,6,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    datetime(2000, 10, 29, 3, 0),
    #2000-11-11,20,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-11,21,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-11,22,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-11,23,600,"RAS Limitation",550,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-11,24,600,"RAS Limitation",500,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-12,1,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-12,2,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-12,3,600,"RAS Limitation",600,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-12,4,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    # ...
    #2000-11-12,21,600,"RAS Limitation",775,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-12,22,600,"RAS Limitation",775,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-12,23,600,"RAS Limitation",725,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-13,1,600,"RAS Limitation",600,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-13,2,600,"RAS Limitation",600,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-13,3,600,"RAS Limitation",600,"Conversion",75,"Conversion",153,"Conversion"
    # ...
    #2000-11-13,20,600,"RAS Limitation",775,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-13,21,600,"RAS Limitation",775,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-13,22,600,"RAS Limitation",725,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-13,23,600,"RAS Limitation",725,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-14,1,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-14,2,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-14,3,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    # ...
    #2000-11-14,20,600,"RAS Limitation",775,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-14,21,600,"RAS Limitation",775,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-14,22,600,"RAS Limitation",775,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-14,23,600,"RAS Limitation",725,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-15,1,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-15,2,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-15,3,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    # ...
    #2000-11-15,20,600,"RAS Limitation",775,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-15,21,600,"RAS Limitation",775,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-15,22,600,"RAS Limitation",775,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-15,23,600,"RAS Limitation",725,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-16,1,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-16,2,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-16,3,600,"RAS Limitation",625,"Conversion",75,"Conversion",153,"Conversion"
    # ...
    #2000-11-16,21,600,"RAS Limitation",800,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-16,22,600,"RAS Limitation",800,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-16,23,220,"Correct to load",750,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-16,24,380,"Correct to load",675,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-17,1,450,"Correct to load",625,"Conversion",75,"Conversion",153,"Conversion"
    #2000-11-17,2,520,"Correct to load",625,"Conversion",75,"Conversion",153,"Conversion"

    datetime(2000, 11, 13, 0, 0),
    datetime(2000, 11, 14, 0, 0),
    datetime(2000, 11, 15, 0, 0),
    datetime(2000, 11, 16, 0, 0),

    #2002-12-26,7,650,"Conversion",500,"Conversion",75,"Conversion",153,"Conversion"
    #2002-12-26,8,600,"Conversion",550,"Conversion",75,"Conversion",153,"Conversion"
    #2002-12-26,9,560,"Conversion",550,"Conversion",75,"Conversion",153,"Conversion"
    #2002-12-26,10,560,"Conversion",550,"Conversion",75,"Conversion",153,"Conversion"
    # >> Missing 11:00 here.
    #2002-12-26,12,560,"Conversion",575,"Conversion",75,"Conversion",153,"Conversion"
    #2002-12-26,13,560,"Conversion",575,"Conversion",75,"Conversion",153,"Conversion"
    #2002-12-26,14,560,"Conversion",550,"Conversion",75,"Conversion",153,"Conversion"
    #2002-12-26,15,560,"Conversion",550,"Conversion",75,"Conversion",153,"Conversion"
    datetime(2002, 12, 26,11, 0),

    #2004-09-27,23,200,"Calgary cap oos",610,"887/1L274 oos (not in OPP)",0,"840s McNeill oos",0,"840s McNeill oos"
    #2004-09-27,24,200,"Calgary cap oos",535,"887/1L274 oos (not in OPP)",0,"840s McNeill oos",0,"840s McNeill oos"
    #2004-09-28,1,500,"Calgary cap oos",535,"887/1L274 oos (not in OPP)",0,"840s McNeill oos",0,"840s McNeill oos"
    #2004-09-28,3,500,"Calgary cap oos",510,"887/1L274 oos (not in OPP)",0,"840s McNeill oos",0,"840s McNeill oos"
    #2004-09-28,4,500,"Calgary cap oos",510,"887/1L274 oos (not in OPP)",0,"840s McNeill oos",0,"840s McNeill oos"
    #2004-09-28,5,500,"Calgary cap oos",510,"887/1L274 oos (not in OPP)",0,"840s McNeill oos",0,"840s McNeill oos"
    datetime(2004,  9, 28, 2, 0),
]
expected_missing_dts = set([AB_TZ.localize(dt) for dt in expected_missing_dts])


class ExpectedTimeMixin:
    def assertFileHasExpectedTimes(self, f):
        # See issue number 5
        # https://bitbucket.org/kc/pyaeso/issue/5
        actual_dts = set()
        for point in atc.parse_atc_file(f):
            actual_dts.add(point.t)

        min_expected_dt = min(actual_dts)
        max_expected_dt = max(actual_dts)
        expected_dts = set()
        dt = min_expected_dt
        while dt <= max_expected_dt:
            expected_dts.add(dt)
            dt += timedelta(hours = 1)

        expected_dts = set([dt.astimezone(AB_TZ) for dt in expected_dts])
        actual_dts = set([dt.astimezone(AB_TZ) for dt in actual_dts])

        inrange_expected_missing_dts = set([dt for dt in expected_missing_dts if min_expected_dt <= dt and dt <= max_expected_dt])
        missing_dts = expected_dts - actual_dts
        self.assertEqual(missing_dts, inrange_expected_missing_dts)
        extra_dts = actual_dts - expected_dts
        expected_extra_dts = set()
        inrange_expected_extra_dts = set([dt for dt in expected_extra_dts if min_expected_dt <= dt and dt <= max_expected_dt])
        self.assertEqual(extra_dts, inrange_expected_extra_dts)


class TestAtcLimits(unittest.TestCase, ExpectedTimeMixin):
    def test_date_parsing(self):
        converstions = [
            # Standard time -> daylight saavings time transition
            (('2000-04-01','24'), datetime(2000, 4, 2, 7)),
            (('2000-04-02','1'),  datetime(2000, 4, 2, 8)),
            (('2000-04-02','2'),  datetime(2000, 4, 2, 9)),
            (('2000-04-02','4'),  datetime(2000, 4, 2, 10)),
            (('2000-04-02','5'),  datetime(2000, 4, 2, 11)),

            # Daylight-savings time -> standard time transition
            (('2000-10-28', '24'), datetime(2000, 10, 29, 6)),
            (('2000-10-29', '1'),  datetime(2000, 10, 29, 7)),
            (('2000-10-29', '2'),  datetime(2000, 10, 29, 8)),
            (('2000-10-29', '2*'), datetime(2000, 10, 29, 9)),
            (('2000-10-29', '4'),  datetime(2000, 10, 29, 11)),
            (('2000-10-29', '5'),  datetime(2000, 10, 29, 12)),
        ]

        for cells, expected in converstions:
            expected = UTC_TZ.localize(expected)
            actual = atc._normalize_atc_dtstr_to_utc(cells)
            self.assertEqual(actual, expected)


    def test_parse_atcdump_2011_file(self):
        self.maxDiff = 100
        test_series_file = join(env.res_dir(), 'atcdump-2011.csv.bz2')

        f = bz2.BZ2File(test_series_file)
        try:
            self.assertFileHasExpectedTimes(f)
        finally:
            f.close()


class TestRemoteShort(unittest.TestCase):
    def test_timeout(self):
        start_date = date(2011, 1, 1)
        end_date = date(2011, 2, 1)

        b = BytesIO()
        try:
            if sys.version_info[0:2] in [(2,4), (2,5)]:
                self.assertRaises(ValueError, atc.dump_atc, b, start_date, end_date, timeout = 1.5)
            else:
                self.assertRaises(URLError, atc.dump_atc, b, start_date, end_date, timeout = 0.0000000001)
        finally:
            b.close()


    def test_short_atc_dump(self):
        start_date = date(2011, 1, 1)
        end_date = date(2011, 2, 1)

        fn = join(env.log_dir(), 'test_atc.TestRemoteShort.test_short_atc_dump.txt')
        f = open(fn, 'w+b')
        try:
            atc.dump_atc(f, start_date, end_date)
            f.seek(0)
            points = list(atc.parse_atc_file(f))
        finally:
            f.close()


    def test_urlopen(self):
        start_date = date(2001, 6, 14)
        end_date = date(2001, 12, 10)

        fn = join(env.log_dir(), 'test_atc.TestRemoteShort.test_urlopen.txt')
        f = open(fn, 'w+b')
        try:
            atc.dump_atc(f, start_date, end_date)
            f.seek(0)
            points = list(atc.parse_atc_file(f))
        finally:
            f.close()
        

class TestRemoteLong(unittest.TestCase, ExpectedTimeMixin):
    def test_full_atc_dump(self):
        start_date = date(1999, 12, 22)
        end_date = date.today() + timedelta(1)

        fn = join(env.log_dir(), 'test_atc.TestRemoteLong.test_full_atc_dump.txt')
        f = open(fn, 'w+b')
        try:
            atc.dump_atc(f, start_date, end_date)
            f.seek(0)
            self.assertFileHasExpectedTimes(f)
        finally:
            f.close()


if __name__ == '__main__':
    unittest.main()

