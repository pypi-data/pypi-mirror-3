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
from datetime import date
import unittest
import doctest
import sys

########################################################################
## Custom Imports
import aeso._util
from aeso._util import (
  DayBlockIt,
  _compat_urlopen
)


class TestDayBlockIt(unittest.TestCase):
    def test_iteration(self):
        start_date = date(1995, 1, 1)
        end_date = date(1995, 1, 10)

        it = DayBlockIt(start_date, end_date, 10)
        self.assertEqual(it.next(), (start_date, end_date))
        self.assertRaises(StopIteration, it.next)

        it = DayBlockIt(start_date, end_date, 5)
        self.assertEqual(it.next(), (date(1995, 1, 1), date(1995, 1, 5)))
        self.assertEqual(it.next(), (date(1995, 1, 6), date(1995, 1, 10)))
        self.assertRaises(StopIteration, it.next)


    def test_negative(self):
        start_date = date(1995, 1, 10)
        end_date = date(1995, 1, 1)

        it = DayBlockIt(start_date, end_date, -10)
        self.assertEqual(it.next(), (start_date, end_date))

        it = DayBlockIt(start_date, end_date, -5)
        self.assertEqual(it.next(), (date(1995, 1, 10), date(1995, 1, 6)))
        self.assertEqual(it.next(), (date(1995, 1, 5), date(1995, 1, 1)))
        self.assertRaises(StopIteration, it.next)


class TestCompatUrlopen(unittest.TestCase):
  def test_no_timeout(self):
    f = _compat_urlopen('http://www.google.ca')
    f.read()


  def test_timeout(self):
    if sys.version_info[0:2] in [(2,4), (2,5)]:
      self.assertRaises(ValueError, _compat_urlopen, 'http://www.google.ca', timeout = 1.5)
    else:
      f = _compat_urlopen('http://www.google.ca', timeout = 1.5)
      f.read()
      

if __name__ == '__main__':
    unittest.main()

