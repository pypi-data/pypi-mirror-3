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

import logging
import logging.config

from  lava_test.core.config import get_config

from lava_tool.dispatcher import LavaDispatcher, run_with_dispatcher_class


class LAVATestDispatcher(LavaDispatcher):

    toolname = 'lava_test'
    description = """
    LAVA Test wrapper framework
    """
    epilog = """
    Please report all bugs using the Launchpad bug tracker:
    http://bugs.launchpad.net/lava-test/+filebug
    """


def main():

    logging_config_file = get_config().get_logging_config_file()

    if logging_config_file != None:
        logging.config.fileConfig(logging_config_file)
    else:
        # config the python logging
       FORMAT = '<LAVA_TEST>%(asctime)s %(levelname)s: %(message)s'
       DATEFMT= '%Y-%m-%d %I:%M:%S %p'
       logging.basicConfig(format=FORMAT,datefmt=DATEFMT)
       logging.root.setLevel(logging.ERROR)

    run_with_dispatcher_class(LAVATestDispatcher)


if __name__ == '__main__':
    import os
    import sys
    arg_only = sys.argv
    arg_only.remove(arg_only[0])
    code = LAVATestDispatcher().dispatch(arg_only)
    if (code != 0): exit(code)