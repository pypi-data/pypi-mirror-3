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



INSTALLSTEPS = ['git clone git://git.linaro.org/people/torez/pm-qa.git',
                'cd pm-qa && make clean && make all']
RUNSTEPS = ['cd pm-qa && awk -f testcases.awk  run_template']
DEPS = ['git-core', 'make', 'alsa-utils', 'pulseaudio-utils', 'lame', 'festival', 'wget']

pwrmgmtinst = TestInstaller(INSTALLSTEPS, deps=DEPS)
pwrmgmtrun = TestRunner(RUNSTEPS)

# test case name is between "pm-qa-"  and  ":"  and results and/or
# measurements are rest of the line
PATTERN = "^pm-qa-(?P<test_case_id>\w+):\s+(?P<message>.*)"


pwrmgmtparser = TestParser(PATTERN,
    appendall={'result':'pass'})

testobj = Test(test_id="pwrmgmt", installer=pwrmgmtinst,
                                  runner=pwrmgmtrun, parser=pwrmgmtparser)
