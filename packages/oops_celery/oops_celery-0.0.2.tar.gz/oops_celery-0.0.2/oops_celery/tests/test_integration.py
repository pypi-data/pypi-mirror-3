# Copyright (c) 2012, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

from celery import signals
from celery.task import task
from fixtures import TempDir
import oops
from oops_datedir_repo import DateDirRepo
from testtools import TestCase

from ..oops_reporter import setup_oops_reporter


class TestTaskFailed(Exception):
    pass


@task
def test_task(arg):
    raise TestTaskFailed


class IntegrationTests(TestCase):

    def setUp(self):
        super(IntegrationTests, self).setUp()
        original_receivers = signals.task_failure.receivers
        def restore_receivers():
            signals.task_failure.receivers = original_receivers
        self.addCleanup(restore_receivers)
        signals.task_failure.receivers = []

    def test_creates_oops(self):
        oopses = []
        config = oops.Config()
        config.publishers.append(oopses.append)
        setup_oops_reporter(config)
        result = test_task.apply(args=("the task",))
        self.assertIsInstance(result.result, TestTaskFailed)
        self.assertEqual(1, len(oopses))

    def test_can_write_oops(self):
        config = oops.Config()
        tempdir = self.useFixture(TempDir())
        repo = DateDirRepo(tempdir.path)
        config.publishers.append(repo.publish)
        setup_oops_reporter(config)
        result = test_task.apply(args=(object(),))
        # This just checks an assumption of the test
        self.assertIsInstance(result.result, TestTaskFailed)
        # We are testing that the datedir repo successfully published
        # the oops, but it doesn't provide an interface to get at the
        # serialized oops, so we have to assume that no exception == no
        # problem.
