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

DEFAULT_OPTIONS = ""
DEPS = ["linux-tools"]
RUNSTEPS = ["export PERFBIN=`find /usr/bin/ -name perf_* | sort -r | head -n 1 | xargs basename`; $PERFBIN test 2>&1  $(OPTIONS)"]
PATTERN = "^ \d+:\s+(?P<test_case_id>[\w\s]+):\W+(?P<message>\w+)"

perfinst = TestInstaller(deps=DEPS)
perfrun = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
perfparser = TestParser(PATTERN,
                   appendall={"result":"pass"})
testobj = Test(test_id="perf", installer=perfinst,
                                  runner=perfrun, parser=perfparser)
