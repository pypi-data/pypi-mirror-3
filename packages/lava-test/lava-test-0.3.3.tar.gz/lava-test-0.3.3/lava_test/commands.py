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

import os
import subprocess

from lava_tool.interface import Command as LavaCommand
from lava_tool.interface import LavaCommandError
import versiontools

from lava_test.api.observers import (
    ITestInstallerObserver,
    ITestRunnerObserver)
from lava_test.core.artifacts import TestArtifacts
from lava_test.core.config import get_config
from lava_test.core.loader import TestLoader


class Command(LavaCommand, ITestInstallerObserver, ITestRunnerObserver):

    def __init__(self, parser, args):
        super(Command, self).__init__(parser, args)
        self._config = get_config()
        self._test_loader = TestLoader(self._config)

    @classmethod
    def register_arguments(cls, parser):
        parser.add_argument(
            "-q", "--quiet",
            action="store_true",
            default=False,
            help="Be less verbose about undertaken actions")
        parser.add_argument(
            "-Q", "--quiet-subcommands",
            action="store_true",
            default=False,
            help="Hide the output of all sub-commands (including tests)")

    def say(self, text, *args, **kwargs):
        print "LAVA:", text.format(*args, **kwargs)

    def about_to_install_packages(self, package_list):
        if self.args.quiet:
            return
        self.say("Installing packages: {0}", ", ".join(package_list))

    def about_to_run_shell_command(self, cmd):
        if self.args.quiet:
            return
        self.say("Running shell command: {0!r}", cmd)

    def about_to_download_file(self, url):
        if self.args.quiet:
            return
        self.say("Downloading file from: {0!r}", url)

    def did_install_packages(self, package_list):
        pass

    def did_run_shell_command(self, cmd, returncode):
        if returncode is None:
            self.say("Command {0!r} was terminated prematurely", cmd)
        elif returncode != 0:
            self.say("Command {0!r} returned non-zero exit status {1}",
                     cmd, returncode)

    def did_download_file(self, url):
        pass

    def display_subprocess_output(self, stream_name, line):
        if self.args.quiet_subcommands:
            return
        if stream_name == 'stdout':
            self.say('(stdout) {0}', line.rstrip())
        elif stream_name == 'stderr':
            self.say('(stderr) {0}', line.rstrip())


class list_tests(Command):
    """
    List available tests

    .. program:: lava-test list-tests

    Lists all available tests, grouping them by provider.
    """

    def invoke(self):
        for provider in self._test_loader.get_providers():
            test_list = [provider[test_id] for test_id in provider]
            if not test_list:
                continue
            self.say("{0}", provider.description)
            for test in test_list:
                self.say(" - {test_id}", test_id=test.test_id)


class list_installed(Command):
    """
    List installed tests
    """

    def invoke(self):
        for provider in self._test_loader.get_providers():
            test_list = [provider[test_id] for test_id in provider]
            if not test_list:
                continue
            self.say("{0}", provider.description)
            count = 0
            for test in test_list:
                if not test.is_installed:
                    continue
                self.say(" - {test_id}", test_id=test.test_id)
                count += 1
            if not count:
                self.say("No tests installed")



class TestAffectingCommand(Command):

    INSTALL_REQUIRED = False

    @classmethod
    def register_arguments(cls, parser):
        super(TestAffectingCommand, cls).register_arguments(parser)
        parser.add_argument("test_id",
                            help="Test or test suite identifier")

    def invoke(self):
        try:
            test = self._test_loader[self.args.test_id]
        except KeyError:
            raise LavaCommandError("There is no test with the specified ID")
        return self.invoke_with_test(test)


class install(TestAffectingCommand):
    """
    Install a test program
    """

    def invoke_with_test(self, test):
        if test.is_installed:
            raise LavaCommandError("This test is already installed")
        try:
            test.install(self)
        except (subprocess.CalledProcessError, RuntimeError) as ex:
            raise LavaCommandError(str(ex))


class uninstall(TestAffectingCommand):
    """
    Uninstall a test program
    """

    def invoke_with_test(self, test):
        if not test.is_installed:
            raise LavaCommandError("This test is not installed")
        test.uninstall()


class run(TestAffectingCommand):
    """
    Run a previously installed test program
    """

    @classmethod
    def register_arguments(cls, parser):
        super(run, cls).register_arguments(parser)
        group = parser.add_argument_group("initial bundle configuration")
        group.add_argument("-S", "--skip-software-context",
                            default=False,
                            action="store_true",
                           help=("Do not store the software context in the"
                                 " initial bundle. Typically this saves OS"
                                 " image name and all the installed software"
                                 " packages."))
        group.add_argument("-H", "--skip-hardware-context",
                            default=False,
                            action="store_true",
                           help=("Do not store the hardware context in the"
                                 " initial bundle. Typically this saves CPU,"
                                 " memory and USB device information."))
        group.add_argument("--trusted-time",
                            default=False,
                            action="store_true",
                            help=("Indicate that the real time clock has"
                                  " accurate data. This can differentiate"
                                  " test results created on embedded devices"
                                  " that often have inaccurate real time"
                                  " clock settings."))
        group = parser.add_argument_group("complete bundle configuration")
        group.add_argument("-o", "--output",
                            default=None,
                            metavar="FILE",
                           help=("After running the test parse the result"
                                 " artifacts, fuse them with the initial"
                                 " bundle and finally save the complete bundle"
                                 " to the  specified FILE."))
        group.add_argument("-A", "--skip-attachments",
                            default=False,
                            action="store_true",
                            help=("Do not store standard output and standard"
                                  " error log files as attachments. This"
                                  " option is only affecting the bundle"
                                  " created with --output, the initial bundle"
                                  " is not affected as it never stores any"
                                  " attachments."))

        parser.add_argument("-t", "--test-options",
                            default=None,
                            help="Override the default test options. "
                                 "The $(OPTIONS) in the run steps will be replaced by the options."
                                 "See peacekeeper.py as example how to use this feature."
                                 "To provide multiple options, use quote character."
                                 "Example : lava-test run peacekeeper -t firefox.  "
                                 "Example of multiple options : lava-test run foo_test -t 'arg1 arg2'")

    def invoke_with_test(self, test):
        if not test.is_installed:
            raise LavaCommandError("The specified test is not installed")
        try:
            artifacts, run_fail = test.run(self, test_options=self.args.test_options)
        except subprocess.CalledProcessError as ex:
            if ex.returncode is None:
                raise LavaCommandError("Command %r was aborted" % ex.cmd)
            else:
                raise LavaCommandError(str(ex))
        except RuntimeError as ex:
            raise LavaCommandError(str(ex))
        self.say("run complete, result_id is {0!r}", artifacts.result_id)
        artifacts.create_initial_bundle(
            self.args.skip_software_context,
            self.args.skip_hardware_context,
            self.args.trusted_time)
        artifacts.save_bundle()
        if self.args.output:
            parse_results = test.parse(artifacts)
            artifacts.incorporate_parse_results(parse_results)
            if not self.args.skip_attachments:
                artifacts.attach_standard_files_to_bundle()
            artifacts.save_bundle_as(self.args.output)
        if run_fail:
            raise LavaCommandError(
                'Some of test steps returned non-zero exit code')


class parse(TestAffectingCommand):
    """
    Parse the results of previous test run
    """

    @classmethod
    def register_arguments(cls, parser):
        super(parse, cls).register_arguments(parser)
        parser.add_argument("result_id",
                            help="Test run result identifier")
        group = parser.add_argument_group("complete bundle configuration")
        group.add_argument("-o", "--output",
                            default=None,
                            metavar="FILE",
                           help=("After running the test parse the result"
                                 " artifacts, fuse them with the initial"
                                 " bundle and finally save the complete bundle"
                                 " to the  specified FILE."))
        group.add_argument("-A", "--skip-attachments",
                            default=False,
                            action="store_true",
                            help=("Do not store standard output and standard"
                                  " error log files as attachments. This"
                                  " option is only affecting the bundle"
                                  " created with --output, the initial bundle"
                                  " is not affected as it never stores any"
                                  " attachments."))

    def invoke_with_test(self, test):
        artifacts = TestArtifacts(
            self.args.test_id, self.args.result_id, self._config)
        if not os.path.exists(artifacts.bundle_pathname):
            raise LavaCommandError("Specified result does not exist")
        artifacts.load_bundle()
        parse_results = test.parse(artifacts)
        artifacts.incorporate_parse_results(parse_results)
        self.say("Parsed {0} test results",
                 len(artifacts.bundle["test_runs"][0]["test_results"]))
        logging.debug(artifacts.dumps_bundle())
        if self.args.output:
            if not self.args.skip_attachments:
                artifacts.attach_standard_files_to_bundle()
            artifacts.save_bundle_as(self.args.output)


class show(Command):
    """
    Display the output from a previous test run
    """

    @classmethod
    def register_arguments(cls, parser):
        super(show, cls).register_arguments(parser)
        parser.add_argument("result_id",
                            help="Test run result identifier")

    def invoke(self):
        artifacts = TestArtifacts(None, self.args.result_id, self._config)
        if not os.path.exists(artifacts.results_dir):
            raise LavaCommandError("Specified result does not exist")
        if os.path.exists(artifacts.stdout_pathname):
            with open(artifacts.stdout_pathname, "rt") as stream:
                for line in iter(stream.readline, ''):
                    self.display_subprocess_output("stdout", line)
        if os.path.exists(artifacts.stderr_pathname):
            with open(artifacts.stderr_pathname, "rt") as stream:
                for line in iter(stream.readline, ''):
                    self.display_subprocess_output("stderr", line)


class version(Command):
    """
    Show LAVA Test version
    """

    def invoke(self):
        self.say("version details:")
        for framework in self._get_frameworks():
            self.say(" - {framework}: {version}",
                     framework=framework.__name__,
                     version=versiontools.format_version(
                         framework.__version__, framework))

    def _get_frameworks(self):
        import lava_tool
        import lava_test
        import linaro_dashboard_bundle
        import linaro_json
        return [
            lava_test,
            lava_tool,
            linaro_dashboard_bundle,
            linaro_json]


class register_test(Command):
    """
    Register remote test
    """

    @classmethod
    def register_arguments(cls, parser):
        super(register_test, cls).register_arguments(parser)
        parser.add_argument("test_url",
                            help="Url for test definition file")

    def invoke(self):
        try:
            from lava_test.core.providers import RegistryProvider
            RegistryProvider.register_remote_test(self.args.test_url)
        except ValueError as exc:
            raise LavaCommandError("Unable to register test: %s" % exc)
        except KeyError:
            raise LavaCommandError("There is no test_url")

class unregister_test(Command):
    """
    Unregister remote test
    """

    @classmethod
    def register_arguments(cls, parser):
        super(unregister_test, cls).register_arguments(parser)
        parser.add_argument("test_url",
                            help="Url for test definition file")

    def invoke(self):
        try:
            from lava_test.core.providers import RegistryProvider
            RegistryProvider.unregister_remote_test(self.args.test_url)
        except ValueError as exc:
            raise LavaCommandError("Unable to unregister test: %s" % exc)
        except KeyError:
            raise LavaCommandError("There is no test_url")
