#~ pyaeso is a python package that makes access to the Alberta, Canada's
#~ Electric System Operator's (AESO) Energy Trading System (ETS) easier.

#~ Copyright (C) 2010 Keegan Callin

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

'''Print current output of Alberta generators then exit.'''

# Standard library imports
import sys

# 3rd Party Libraries
from aeso import csd
from aeso import AB_TZ

def  main():
    aggregates = []
    generators = []

    print 'Current Alberta Generator Unit Outputs'
    print '======================================'
    print
    print '    MCR = Maximum continuous rating'
    print '    TNG = Total net generation'
    print '    DCR = Dispatched (and accepted) Contingency Reserve'
    print
    print 'time, unit, MCR, TNG, DCR'

    f = csd.urlopen()
    for cells in csd.parse_csd_file(f):
        if len(cells) == 3:
            aggregates.append(cells)
        else:
            assert len(cells) == 5
            utc_dt, unit, mcr, tng, dcr = cells
            # All times reported by pyaeso are in UTC.  Must convert to
            # Alberta timezone before displying to user.
            ab_dt = AB_TZ.normalize(utc_dt.astimezone(AB_TZ))
            generators.append(cells)
            print '%s, %s, %d, %d, %d' % (ab_dt, unit, mcr, tng, dcr)

    f.close()

    return(0)


if __name__ == '__main__':
    sys.exit(main())
