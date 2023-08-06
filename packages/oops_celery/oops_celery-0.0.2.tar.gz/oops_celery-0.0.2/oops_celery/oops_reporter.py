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
from oops.createhooks import safe_unicode


def attach_celery_info(report, context):
    """Attach celery info from the context to the oops report.

    TaskOopsReporter puts info about the celery failure in the
    oops context. This hook moves that information to the
    report, which is what is usually desired. If you want to do
    something different then use a different hook.
    """
    for key, value in context.items():
        if key.startswith('celery.'):
            report[key] = value


class TaskOopsReporter(object):
    """Create an oops report when on_failure is called.

    This object has a callback designed to be used with celery's signals
    to create oops reports when celery task failures are triggered.
    """

    def __init__(self, config):
        """Create an oops reporter.

        :param config: the oops.Config object to create the oops from
            and publish it to.
        """
        self.config = config

    def on_failure(self, einfo=None, **kwargs):
        """Callback to create an oops.

        Designed to be used with `celery.signals.on_failure`.
        """
        context = dict()
        if einfo is not None:
            context['exc_info'] = einfo.exc_info
        for key, value in kwargs.items():
            context['celery.' + key] = safe_unicode(value)
        report = self.config.create(context)
        self.config.publish(report)


def setup_oops_reporter(config):
    """Setup an oops reporter to be triggered when a celery job fails.

    This creates a `TaskOopsReporter` object using the passed config,
    and sets up `attach_celery_info` to be called when an oops is
    created. Finally it connects `TaskOopsReporter.on_failure` to
    `celery.signal.task_failure` so that it is called when tasks
    fail.

    If you wish to have a different setup then you can implement those
    steps yourself.

    :param config: the oops.Config to use fore creating and publishing
        the oops.
    """
    config.on_create.append(attach_celery_info)
    reporter = TaskOopsReporter(config)
    signals.task_failure.connect(reporter.on_failure, weak=False)
