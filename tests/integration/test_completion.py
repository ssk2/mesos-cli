
import httmock
import mock
import os
import StringIO
import sys

import mesos_cli.completion

from .. import utils

def generate_env(line):
    env = {
        "COMP_LINE": line,
        "COMP_POINT": len(line)
    }
    env.update(os.environ)
    return env

@httmock.urlmatch(path="/files/browse.json.*")
def browse_mock(url, req):
    return utils.get_state("browse_twisted.json", parse=False)

# There are some side effects in completion. To test completers, make sure you
# use different commands. Otherwise, you'll get what appears to be random
# failures.
@mock.patch("mesos_cli.completion.EXIT", sys.exit)
class TestCompletion(utils.MockState):

    @mock.patch("os.environ", generate_env("mesos "))
    def test_cmds(self):
        mesos_cli.completion.main()

        assert "help" in self.stdout

    @mock.patch("os.environ", generate_env("mesos cat "))
    def test_task(self):
        self.assertRaises(SystemExit, mesos_cli.completion.main)

        assert "app-15" in self.stdout
        assert "app-215" in self.stdout

    @mock.patch("os.environ", generate_env("mesos state 2"))
    def test_slave(self):
        self.assertRaises(SystemExit, mesos_cli.completion.main)

        assert len(self.stdout.split("\n")) == 2

    @mock.patch("os.environ", generate_env("mesos ls app-215 Twisted-14.0.0/"))
    @httmock.with_httmock(browse_mock)
    def test_file(self):
        self.assertRaises(SystemExit, mesos_cli.completion.main)

        assert "twisted/" in self.stdout
        assert "NEWS" in self.stdout
