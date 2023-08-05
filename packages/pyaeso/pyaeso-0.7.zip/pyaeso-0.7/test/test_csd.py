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

# Built-in modules
import unittest

from datetime import datetime
from datetime import timedelta

from os.path import dirname
from os.path import join

from time import strptime
import doctest
import sys

import bz2

from urllib2 import URLError

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO



# 3rd party libraries
import pytz
from pytz import utc as UTC

# Custom libraries
from aeso import AB_TZ
from aeso import csd
from aeso._util import (
  Utf8Reader,
  UTF8
)
from env import res_dir


class TestCsd(unittest.TestCase):
    CSD_DT_FORMAT = '%b %d, %Y %H:%M'

    def test_parse_asset_list_file(self):
        test_file = join(res_dir(), 'CSDReportServlet.csv.bz2')
        f = bz2.BZ2File(test_file)

        num_rows = 0
        for cells in csd.parse_csd_file(f):
            num_rows += 1
            self.assertTrue(len(cells) in (3, 5))
            #~ print entries[0].astimezone(AB_TZ), entries[1:]
        self.assertEqual(num_rows, 115)


    def test_csd_err(self):
        test_file = join(res_dir(), 'csd-err.log.bz2')
        f = bz2.BZ2File(test_file)
        try:
            bytes = f.read()
            texts = bytes.decode(UTF8).split('==========')
        finally:
            f.close()

        for i, text in enumerate(texts):
            bytes = text.encode(UTF8)
            f = BytesIO(bytes)

            num_rows = 0
            for cells in csd.parse_csd_file(f):
                num_rows += 1
                self.assertTrue(len(cells) in (3, 5))


    def _test_dst_begin(self):
        # Dst begins 2010-03-14
        template_fn = join(res_dir(), 'csdreport_dst.csv.bz2')

        f = bz2.BZ2File(template_fn)
        template_text = f.read()
        f.close()

        cursor = datetime(2010, 3, 14, 0)
        max_dt = datetime(2010, 3, 14, 4)

        while cursor < max_dt:
            report_dt_str = cursor.strftime(type(self).CSD_DT_FORMAT)
            text = template_text % (report_dt_str,)
            #text = template_text.format(datetime = report_dt_str)
            f = BytesIO(text)
            num_rows = 0
            for cells in csd.parse_csd_file(f):
                num_rows += 1
            f.close()

            cursor += timedelta(0, 60)


    def test_timedeltas(self):
        td = AB_TZ.localize(datetime(2010, 11, 7, 0, 0), is_dst = False) - AB_TZ.localize(datetime(2010, 11, 6, 23, 59), is_dst = None)
        self.assertEqual(td, timedelta(0, 60))

        td = AB_TZ.localize(datetime(2010, 11, 7, 0, 59), is_dst = False) - AB_TZ.localize(datetime(2010, 11, 7, 0, 58), is_dst = None)
        self.assertEqual(td, timedelta(0, 60))

        td = AB_TZ.localize(datetime(2010, 11, 6, 1, 0), is_dst = None) - AB_TZ.localize(datetime(2010, 11, 6, 0, 59), is_dst = None)
        self.assertEqual(td, timedelta(0, 60))

        td = AB_TZ.localize(datetime(2010, 11, 7, 1, 0), is_dst = True) - AB_TZ.localize(datetime(2010, 11, 7, 0, 59), is_dst = None)
        self.assertEqual(td, timedelta(0, 60))

        td = AB_TZ.localize(datetime(2010, 11, 7, 1, 0), is_dst = False) - AB_TZ.localize(datetime(2010, 11, 7, 1, 59), is_dst = True)
        self.assertEqual(td, timedelta(0, 60))

        # Arithmetic falls over here.  Timdelta should be 60 seconds but it isn't!
        ab_a = AB_TZ.localize(datetime(2010, 11, 7, 1, 0), is_dst = False)
        ab_b = AB_TZ.localize(datetime(2010, 11, 7, 1, 59), is_dst = True)
        utc_a = UTC.normalize(ab_a.astimezone(UTC))
        utc_b = UTC.normalize(ab_b.astimezone(UTC))
        self.assertEqual(ab_a - ab_b, utc_a - utc_b)
        self.assertEqual(utc_a - ab_b, utc_a - utc_b)
        self.assertEqual(ab_a - utc_b, utc_a - utc_b)


    def _open_rendered_template(self, report_dt):
        template_fn = join(res_dir(), 'csdreport_dst.csv.bz2')

        f = Utf8Reader(bz2.BZ2File(template_fn))
        try:
            template_text = f.read()
        finally:
            f.close()
            

        report_dt_str = report_dt.strftime(type(self).CSD_DT_FORMAT)
        text = template_text % (report_dt_str,)
        f = BytesIO(text.encode(UTF8))
        return f


    def assertCsdParseDtEquals(self, report_dt, ref_dt, expected_dt):
        f = self._open_rendered_template(report_dt)
        num_rows = 0
        for cells in csd.parse_csd_file(f, ref_dt):
            self.assertEqual(cells[0], expected_dt)
            num_rows += 1
        f.close()


    def assertCsdParseRaises(self, exception_class, report_dt, ref_dt):
        f = self._open_rendered_template(report_dt)
        it = csd.parse_csd_file(f, ref_dt)
        self.assertRaises(exception_class, it.next)
        f.close()


    def test_dst_end(self):
        # Dst ends 2010-11-07

        rpt_dt = AB_TZ.localize(datetime(2010, 11, 7, 0, 59), is_dst = None)
        self.assertCsdParseDtEquals(rpt_dt, None, UTC.normalize(rpt_dt.astimezone(UTC)))

        rpt_dt = datetime(2010, 11, 7, 1, 0)
        ref_dt = AB_TZ.localize(datetime(2010, 11, 7, 0, 59))
        expected_dt = UTC.normalize(AB_TZ.localize(datetime(2010, 11, 7, 1, 0), is_dst = True).astimezone(UTC))
        self.assertCsdParseDtEquals(rpt_dt, ref_dt, expected_dt)

        rpt_dt = datetime(2010, 11, 7, 1, 30)
        ref_dt = AB_TZ.localize(datetime(2010, 11, 7, 0, 59))
        expected_dt = UTC.normalize(AB_TZ.localize(rpt_dt, is_dst = True).astimezone(UTC))
        self.assertCsdParseDtEquals(rpt_dt, ref_dt, expected_dt)

        rpt_dt = datetime(2010, 11, 7, 1, 30)
        ref_dt = AB_TZ.localize(datetime(2010, 11, 7, 1, 0), is_dst = False)
        expected_dt = UTC.normalize(AB_TZ.localize(rpt_dt, is_dst = False).astimezone(UTC))
        self.assertCsdParseDtEquals(rpt_dt, ref_dt, expected_dt)

        # Without a reference dt, there is not way to guess at whether
        # DST is active.  Should raise AmbiguousTimeError
        self.assertCsdParseRaises(pytz.AmbiguousTimeError, datetime(2010, 11, 7, 1, 30), None)


    def test_dt(self):
        cell = 'Last Update : Mar 14, 2010 02:00'

        struct_time = strptime(cell, "Last Update : %b %d, %Y %H:%M")
        dt = datetime(*struct_time[0:6])
        self.assertEqual(dt.hour, 2)
        self.assertRaises(pytz.NonExistentTimeError, AB_TZ.localize, dt, is_dst = None)


class TestCsdWebservice(unittest.TestCase):
    def test_timeout(self):
        b = BytesIO()
        try:
            if sys.version_info[0:2] in [(2,4), (2,5)]:
                self.assertRaises(ValueError, csd.urlopen, timeout = 1.5)
            else:
                self.assertRaises(URLError, csd.urlopen, timeout = 0.000000001)
        finally:
            b.close()


    def test_csd_webservice(self):
        f = csd.urlopen()
        rows = list(csd.parse_csd_file(f))
        f.close()
        self.assertTrue(len(rows) > 50)


if __name__ == '__main__':
    unittest.main()

