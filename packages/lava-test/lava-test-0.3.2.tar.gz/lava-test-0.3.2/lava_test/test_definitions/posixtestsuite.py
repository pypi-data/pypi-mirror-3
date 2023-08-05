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
   results parsing for the OpenPosix test suite.
   The POSIX Test Suite is an open source test suite with the goal of
   performing conformance, functional, and stress testing of the IEEE
   1003.1-2001 System Interfaces specification However the automation here
   does not support the stress test runs.

"""
import re

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test


VERSION="20100831"
URL= "http://downloads.sourceforge.net/project/ltp/LTP Source/ltp-%s/"\
     "ltp-full-%s.bz2" % (VERSION, VERSION)
MD5="6982c72429a62f3917c13b2d529ad1ce"
DEFAULT_OPTIONS = ""
INSTALLSTEPS = ['tar -xjf ltp-full-20100831.bz2']
DEPS = ['gcc', 'bzip2']
RUNSTEPS = ['cd ltp-full-20100831/testcases/open_posix_testsuite/ && make $(OPTIONS)']

PATTERN = "((?P<test_case_id>\A(\w+[/]+)+\w+[-]*\w*[-]*\w*) .*? (?P<result>\w+))"
FIXUPS = {
            "FAILED"      :  "fail",
            "INTERRUPTED" :  "skip",
            "PASSED"      :  "pass",
            "UNRESOLVED"  :  "unknown",
            "UNSUPPORTED" :  "skip",
            "UNTESTED"    :  "skip",
            "SKIPPING"    :  "skip"
         }


class PosixParser(TestParser):
    def parse(self, artifacts):
        filename = "testoutput.log"
        pat = re.compile(self.pattern)
        with open(filename) as fd:
            for lineno, line in enumerate(fd, 1):
                match = pat.match(line)
                if not match:
                    continue
                results = match.groupdict()
                test_case_id = results['test_case_id']
                results['test_case_id'] = test_case_id.replace("/", ".")
                results["log_filename"] = "testoutput.log"
                results["log_lineno"] = lineno
                self.results['test_results'].append(
                    self.analyze_test_result(results))

posix_inst = TestInstaller(INSTALLSTEPS, deps=DEPS,
    url=URL, md5=MD5)
posix_run = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
posixparser = PosixParser(PATTERN, fixupdict = FIXUPS)
testobj = Test(test_id="posixtestsuite", test_version=VERSION,
                                  installer=posix_inst, runner=posix_run,
                                  parser=posixparser)
