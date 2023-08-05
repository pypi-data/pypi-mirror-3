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

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

INSTALLSTEPS = ['bzr branch lp:~linaro-foundations/lava-test/bootchartscript']
DEPS = ['bootchart', 'pybootchartgui', 'bzr']
RUNSTEPS = ['./bootchartscript/bootchartscript.sh']
PATTERN = "^(?P<test_case_id>\w+):\W+(?P<measurement>\d+\.\d+)"

bootchartinst = TestInstaller(INSTALLSTEPS, deps=DEPS)
bootchartrun = TestRunner(RUNSTEPS)
bootchartparser = TestParser(PATTERN,
                   appendall={'units':'sec', 'result':'pass'})
testobj = Test(testname="bootchart", installer=bootchartinst,
                                  runner=bootchartrun, parser=bootchartparser)
