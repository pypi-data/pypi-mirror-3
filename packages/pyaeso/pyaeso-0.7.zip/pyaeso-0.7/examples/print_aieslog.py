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

'''Print snapshot of the Alberta Interconnected Electric Sysem Event
Log then exit.'''

# Standard library imports
import sys

# 3rd Party Libraries
from aeso import aieslog
from aeso import AB_TZ

def  main():
    print 'Alberta Interconnected Electric System Event Log'
    print '================================================'

    f = aieslog.urlopen()
    for utc_dt, msg in aieslog.parse_aieslog_file(f):
        # All times reported by pyaeso are in UTC.  Must convert to
        # Alberta timezone before displying to user.
        ab_dt = AB_TZ.normalize(utc_dt.astimezone(AB_TZ))
        print '%s, %s' % (ab_dt, msg)

    f.close()

    return(0)


if __name__ == '__main__':
    sys.exit(main())
