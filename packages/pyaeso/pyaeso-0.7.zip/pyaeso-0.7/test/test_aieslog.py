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
import warnings

from os.path import dirname
from os.path import join

import bz2
import sys

import doctest

# Custom libraries
from aeso import AB_TZ


class WarningMessage(object):
    """Copied from 2.6 sourcecode so that this works in Python >= 2.4"""

    _WARNING_DETAILS = ("message", "category", "filename", "lineno", "file",
                        "line")

    def __init__(self, message, category, filename, lineno, file=None,
                    line=None):
        local_values = locals()
        for attr in self._WARNING_DETAILS:
            setattr(self, attr, local_values[attr])

        self._category_name = category.__name__

    def __str__(self):
        return ("{message : %r, category : %r, filename : %r, lineno : %s, "
                    "line : %r}" % (self.message, self._category_name,
                                    self.filename, self.lineno, self.line))

# Unittest to ensure that a warning is raised.
_warning_log = []
_saved_showarning = warnings.showwarning
_saved_filters = warnings.filters
def _showwarning(*args, **kwargs):
    global _warning_log
    _warning_log.append(WarningMessage(*args, **kwargs))
warnings.showwarning = _showwarning

warnings.simplefilter("always")

# Trigger a warning.
from aeso import aieslog

# Verify some things
assert len(_warning_log) == 1
assert issubclass(_warning_log[-1].category, DeprecationWarning)
assert "deprecated" in str(_warning_log[-1].message)

warnings.showwarning = _saved_showarning
warnings.filters = _saved_filters



class TestAiesLog(unittest.TestCase):
    def test_parse_asset_list_file(self):
        test_file = join(dirname(__file__), 'res', 'RealTimeShiftReportServlet.csv.bz2')
        f = bz2.BZ2File(test_file)

        num_rows = 0
        for dt, entry in aieslog.parse_aieslog_file(f):
                num_rows += 1
                #print dt.astimezone(AB_TZ), entry
        f.close()
        self.assertEqual(num_rows, 29)


class TestRemoteAiesLog(unittest.TestCase):
    def test_parse_asset_list_file(self):
        f = aieslog.urlopen()
        rows = list(aieslog.parse_aieslog_file(f))
        f.close()
        self.assertTrue(len(rows) > 5)


if __name__ == '__main__':
    unittest.main()
