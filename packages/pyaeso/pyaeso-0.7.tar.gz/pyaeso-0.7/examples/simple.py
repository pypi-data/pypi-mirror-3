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

'''Print yesterday's market clearing price/demand points and exit.'''

# Standard library imports
import sys
try:
    from io import BytesIO
except ImportError:
    # For Python 3
    from StringIO import StringIO as BytesIO
import datetime

# 3rd Party Libraries
from aeso import equilibrium
from aeso import AB_TZ

def  main():
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(1)

    f = BytesIO()
    try:
        equilibrium.dump_equilibrium(f, start_date, end_date)
        f.seek(0)
        data = list(equilibrium.parse_equilibrium_file(f))

        print '''Yesterday's market clearing price/demand points.'''
        for d in data:
            # Time calculations are easier when done in UTC so that no timezone
            # conversions or daylist-savings time conversions need to be made.  For
            # this reason all times yielded by pyaeso are UTC.
            #
            # UTC times are converted to local times when they are displayed to the
            # user.
            print d.t.astimezone(AB_TZ), '$' + str(d.price), str(d.demand) + 'MW'
    finally:
        f.close()

    return(0)


if __name__ == '__main__':
    sys.exit(main())
