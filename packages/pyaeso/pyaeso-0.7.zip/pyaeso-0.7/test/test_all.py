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

# Standard library imports
import unittest
import sys
import doctest

# Actual Modules
import aeso.asset
import aeso.atc
import aeso.csd
import aeso.equilibrium
import aeso.eventlog
import aeso.mpp
import aeso._util

# Testable libraries
import test_examples
import test_ets
import test_marginal_pool_price
import test_csd
import test_aieslog
import test_eventlog
import test_util
import test_mpp
import test_atc
import test_asset
import test_equilibrium


test_modules = (
    test_aieslog,
    test_asset,
    test_atc,
    test_csd,
    test_equilibrium,
    test_ets,
    test_eventlog,
    test_examples,
    test_marginal_pool_price,
    test_mpp,
    test_util,
)




class NameFilterLoader(unittest.TestLoader):
    def namefilter(self, name):
        return True


    def loadTestsFromModule(self, module):
        tests = []
        for name in dir(module):
            obj = getattr(module, name)
            if (hasattr(obj, 'run') and
                    hasattr(obj, 'setUp') and
                    hasattr(obj, 'tearDown') and
                    self.namefilter(name)):
                tests.append(self.loadTestsFromTestCase(obj))

        return unittest.TestSuite(tests)


class ShortRemoteTestLoader(NameFilterLoader):
    def namefilter(self, name):
        if 'long' not in name.lower():
            rc = True
        else:
            rc = False
        return rc


class LocalTestLoader(NameFilterLoader):
    def namefilter(self, name):
        if 'remote' not in name.lower():
            rc = True
        else:
            rc = False
        return rc


loader = unittest.TestLoader()
AllTestSuite = unittest.TestSuite()
for module in test_modules:
    AllTestSuite.addTests(loader.loadTestsFromModule(module))

loader = ShortRemoteTestLoader()
ShortRemoteSuite = unittest.TestSuite()
for module in test_modules:
    ShortRemoteSuite.addTests(loader.loadTestsFromModule(module))

loader = LocalTestLoader()
LocalSuite = unittest.TestSuite()
for module in test_modules:
    LocalSuite.addTests(loader.loadTestsFromModule(module))


doctest_modules = (
    aeso.asset,
    aeso.atc,
    aeso.csd,
    aeso.equilibrium,
    aeso.eventlog,
    aeso.mpp,
    aeso._util,
)


for module in doctest_modules:
    ShortRemoteSuite.addTests(doctest.DocTestSuite(module))
    AllTestSuite.addTests(doctest.DocTestSuite(module))

if __name__ == '__main__':
    unittest.main()

