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

'''Access to the Alberta Interconnected Electric System Event log.  The
raw log is accessible at <http://ets.aeso.ca/ets_web/ip/Market/Reports/RealTimeShiftReportServlet>.

.. warning::
  This module is deprecated and slated for removal.  Please use
  :mod:`aeso.eventlog` instead.
'''


import warnings

warnings.warn('Module aeso.aieslog is deprecated; please use aeso.eventlog instead.', DeprecationWarning, stacklevel=2)

from eventlog import urlopen
from eventlog import parse_eventlog_file as parse_aieslog_file
