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

URL="http://www.cs.virginia.edu/stream/FTP/Code/stream.c"
INSTALLSTEPS = ['cc stream.c -O2 -fopenmp -o stream']
DEPS = ['gcc', 'build-essential']
RUNSTEPS = ['./stream']
PATTERN = "^(?P<test_case_id>\w+):\W+(?P<measurement>\d+\.\d+)"

streaminst = TestInstaller(INSTALLSTEPS, deps=DEPS, url=URL)
streamrun = TestRunner(RUNSTEPS)
streamparser = TestParser(PATTERN,
               appendall={'units':'MB/s', 'result':'pass'})
testobj = Test(test_id="stream", installer=streaminst,
                                  runner=streamrun, parser=streamparser)


