import sys
import traceback

from celery import signals
from celery.datastructures import ExceptionInfo
import oops
from testtools import TestCase

from oops_celery.oops_reporter import (
    attach_celery_info,
    setup_oops_reporter,
    TaskOopsReporter,
    )


class AttachCeleryInfoTests(TestCase):

    def test_adds_all_celery_keys(self):
        context = {
            'celery.foo': 'foo',
            'celery.bar': 'bar',
        }
        report = {}
        attach_celery_info(report, context)
        self.assertEqual(context, report)

    def test_doesnt_add_non_celery_keys(self):
        context = {
            'celery': 'foo',
            'bar': 'bar',
            }
        report = {}
        attach_celery_info(report, context)
        self.assertEqual({}, report)


class TaskOopsReporterTests(TestCase):

    def get_einfo(self):
        try:
            raise ValueError('a message')
        except ValueError:
            exc_info = sys.exc_info()
            return ExceptionInfo(exc_info)

    def setUp(self):
        super(TaskOopsReporterTests, self).setUp()
        self.oopses = []
        config = self.get_oops_config()
        self.recorder = TaskOopsReporter(config)

    def get_oops_config(self):
        config = oops.Config()
        config.publishers.append(self.store_oops)
        config.on_create.append(self.collect_context)
        return config

    def store_oops(self, oops):
        self.oopses.append(oops)

    def collect_context(self, report, context):
        self.context = context

    def test_on_failure_publishes_oops(self):
        einfo = self.get_einfo()
        self.recorder.on_failure()
        self.assertEqual(1, len(self.oopses))

    def test_on_failure_includes_task_id(self):
        einfo = self.get_einfo()
        task_id = 'atask'
        self.recorder.on_failure(task_id=task_id)
        self.assertEqual(task_id, self.context['celery.task_id'])

    def test_on_failure_includes_args(self):
        einfo = self.get_einfo()
        args = [8, 9]
        self.recorder.on_failure(args=args)
        self.assertEqual(args, self.context['celery.args'])

    def test_on_failure_includes_kwargs(self):
        einfo = self.get_einfo()
        kwargs = dict(a=1, b=2)
        self.recorder.on_failure(kwargs=kwargs)
        self.assertEqual(kwargs, self.context['celery.kwargs'])

    def test_on_failure_includes_tb_text(self):
        einfo = self.get_einfo()
        self.recorder.on_failure(einfo=einfo)
        self.assertEqual(u''.join(traceback.format_tb(einfo.tb)), self.oopses[0]['tb_text'])

    def test_on_failure_includes_exception_type(self):
        einfo = self.get_einfo()
        self.recorder.on_failure(einfo=einfo)
        self.assertEqual(einfo.type.__name__, self.oopses[0]['type'])

    def test_on_failure_includes_exception_value(self):
        einfo = self.get_einfo()
        self.recorder.on_failure(einfo=einfo)
        self.assertEqual(unicode(einfo.exception), self.oopses[0]['value'])

    def test_on_failure_includes_sender(self):
        sender = object()
        self.recorder.on_failure(sender=sender)
        self.assertEqual(sender, self.context['celery.sender'])

    def test_on_failure_includes_signal(self):
        signal = object()
        self.recorder.on_failure(signal=signal)
        self.assertEqual(signal, self.context['celery.signal'])

    def test_on_failure_includes_exception(self):
        exception = object()
        self.recorder.on_failure(exception=exception)
        self.assertEqual(exception, self.context['celery.exception'])

    def test_on_failure_includes_traceback(self):
        traceback = object()
        self.recorder.on_failure(traceback=traceback)
        self.assertEqual(traceback, self.context['celery.traceback'])


class SetupOopsReporterTests(TestCase):

    def setUp(self):
        super(SetupOopsReporterTests, self).setUp()
        original_receivers = signals.task_failure.receivers
        def restore_receivers():
            signals.task_failure.receivers = original_receivers
        self.addCleanup(restore_receivers)
        signals.task_failure.receivers = []

    def setup_oops_reporter(self, config=None):
        self.assertEqual(0, len(signals.task_failure.receivers))
        if config is None:
            config = oops.Config()
        setup_oops_reporter(config)

    def test_registers_callback(self):
        self.setup_oops_reporter()
        self.assertEqual(1, len(signals.task_failure.receivers))

    def test_callback_is_a_reporter(self):
        self.setup_oops_reporter()
        receiver = signals.task_failure.receivers[0][1]
        self.assertIsInstance(receiver.im_self, TaskOopsReporter)

    def test_uses_supplied_config(self):
        config = oops.Config()
        self.setup_oops_reporter(config=config)
        receiver = signals.task_failure.receivers[0][1]
        self.assertEqual(config, receiver.im_self.config)

    def test_inserts_hooks(self):
        config = oops.Config()
        self.setup_oops_reporter(config=config)
        self.assertIn(attach_celery_info, config.on_create)

    def test_generates_oops(self):
        config = oops.Config()
        oopses = []
        def save_oops(oops):
            oopses.append(oops)
        config.publishers.append(save_oops)
        self.setup_oops_reporter(config=config)
        signals.task_failure.send(object())
        self.assertEqual(1, len(oopses))
