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
The Linux Test Project is a collection of tools for testing Linux with a 
focus on the kernel.

**URL:** http://ltp.sourceforge.net

**Default options:** -f syscalls -p -q
"""

import re


from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test


VERSION="20100831"
URL='http://downloads.sourceforge.net/project/ltp/LTP Source/ltp-%s/ltp-full-%s.bz2' % (VERSION, VERSION)
MD5="6982c72429a62f3917c13b2d529ad1ce"
DEPS = ['bzip2', 'flex', 'bison', 'make', 'build-essential']

SCRIPT = """
tar -xjf ltp-full-20100831.bz2
mkdir build
cd ltp-full-20100831
./configure --prefix=$(readlink -f ../build)
make all
SKIP_IDCHECK=1 make install
"""
DEFAULT_OPTIONS = "-f syscalls -p -q"

INSTALLSTEPS = ["echo '%s' > installltp.sh" % SCRIPT,
                'chmod +x installltp.sh',
                './installltp.sh']
RUNSTEPS = ['cd build && sudo ./runltp $(OPTIONS)']
PATTERN = "^(?P<test_case_id>\S+)    (?P<subid>\d+)  (?P<result>\w+)  :  (?P<message>.+)"
FIXUPS = {"TBROK":"fail",
          "TCONF":"skip",
          "TFAIL":"fail",
          "TINFO":"unknown",
          "TPASS":"pass",
          "TWARN":"unknown"}


class LTPParser(TestParser):
    def parse(self, artifacts):
        filename = artifacts.stdout_pathname
        print "filename=%s" %filename
        pat = re.compile(self.pattern)
        with open(filename, 'r') as fd:
            for line in fd.readlines():
                match = pat.search(line)
                if match:
                    results = match.groupdict()
                    subid = results.pop('subid')
                    #The .0 results in ltp are all TINFO, filtering them
                    #should help eliminate meaningless, duplicate results
                    if subid == '0':
                        continue
                    results['test_case_id'] += "." + subid
                    self.results['test_results'].append(
                        self.analyze_test_result(results))


ltpinst = TestInstaller(INSTALLSTEPS, deps=DEPS, url=URL,
                                           md5=MD5)
ltprun = TestRunner(RUNSTEPS,default_options = DEFAULT_OPTIONS)
ltpparser = LTPParser(PATTERN, fixupdict = FIXUPS)
testobj = Test(test_id="ltp", test_version=VERSION,
                                  installer=ltpinst, runner=ltprun,
                                  parser=ltpparser)
