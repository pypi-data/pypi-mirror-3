# Copyright (c) 2010, 2011 Linaro
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
   This script automates the automate installation, execution, and
   results parsing for the Peacekeeper browser benchmark.

   http://clients.futuremark.com/peacekeeper/index.action
"""


from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

import os

curdir = os.path.realpath(os.path.dirname(__file__))

INSTALLSTEPS = ['cp -rf %s/peacekeeper/* .'%curdir]
RUNSTEPS = ['python peacekeeper_runner.py firefox']
DEPS = ['python-ldtp','firefox']

my_installer = TestInstaller(INSTALLSTEPS, deps=DEPS)
my_runner = TestRunner(RUNSTEPS)

PATTERN = "^(?P<result>\w+): Score = (?P<measurement>\d+)"

my_parser = TestParser(PATTERN,
                                          appendall={'units':'point'})

testobj = Test(test_id="peacekeeper", installer=my_installer,
                                  runner=my_runner, parser=my_parser)
