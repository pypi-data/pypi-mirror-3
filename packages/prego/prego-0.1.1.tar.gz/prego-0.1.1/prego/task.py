# -*- mode: python; coding: utf-8 -*-

import os
import signal
import time
import logging
from types import NoneType

import nose

from commodity.os_ import SubProcess, FileTee, LoggerAsFile
from commodity.thread_ import start_new_thread
from commodity.type_ import checked_type

from .runner import Runner
from .const import Status, PREGO_TMP
from .exc import TestFailed, ConditionFailed, TimeoutExceeded, \
    log_traceback, CommandAlreadyDefined
from .item import File
from prego.condition import DeferredAssertion, PollDeferredAssertion

import prego.tools as tools

tools.set_logging_formatter(logging.getLogger())
#log = tools.create_logger('prego')
tasks = []


class Task(object):
    identifiers = []

    def __init__(self,
                 desc='',
                 pre=None, post=None,
                 stdout=None, save_stdout=False,
                 stderr=None, save_stderr=False,
                 detach=False,
                 cwd='.'):
        tasks.append(self)
        self.interpolator = tools.Interpolator()

        self.desc = checked_type(str, desc)
        self.pre = []
        self.post = []
        self.stdout      = self.interpolator.apply(stdout)
        self.save_stdout = checked_type(bool, save_stdout)
        self.stderr      = self.interpolator.apply(stderr)
        self.save_stderr = checked_type(bool, save_stderr)
        self.detach      = checked_type(bool, detach)
        self.cwd         = self.interpolator.apply(checked_type(str, cwd))

        self.gen = []
        self.thread = None
        self.status = Status.NOEXEC
#        self.meet_expectations = True
        self.body_defined = False
        self.terminated = False
        self.tinit = None
        self.elapsed = 0
        self.reason = None

        if pre:
            self.pre.append(pre)
        if post:
            self.post.append(post)

        self.log = self.create_logger()
        self._enable_outs_if_requested()

    @classmethod
    def get_index(cls, objid):
        try:
            return cls.identifiers.index(objid)
        except ValueError:
            cls.identifiers.append(objid)
            return cls.get_index(objid)

    @property
    def index(self):
        return self.get_index(id(self))

    @property
    def name(self):
        return "T{0}".format(self.index)

    def create_logger(self, prefix=''):
        name = self.name
        if prefix:
            name += '.{0}|'.format(prefix)
        return tools.create_logger(name)

    def run(self):
        if self.detach:
            self.detached_run()
            return

        self.sync_run()

    def detached_run(self):
        self.thread = start_new_thread(self.sync_run)
        self.wait_starts_or_finish()

    def wait_starts_or_finish(self):
        time.sleep(0.1)

        while 1:
            if self.is_finished() or self.is_running():
                break

            time.sleep(0.2)

            if time.time() - self.tinit > 3:
                self.log.critical("does not start after 3s")
                break

    def sync_run(self):
        self.tinit = time.time()
        self.log.debug("Test starts: {0:-<50}".format(self.desc + ' '))
        self.log.info(str(self))
        self.status = Status.UNKNOWN

        try:
            self.eval_conditions(self.pre, 'pre')

            status = self.do_run()
            if status != Status.OK:
                self.status = status
                return

            self.eval_conditions(self.post, 'post')
            self.status = Status.OK

        except ConditionFailed as e:
            self.set_reason(Status.FAIL, "condition %s" % e)

        except Exception as e:
            self.set_reason(Status.ERROR, "condition %s" % e)
            log_traceback(self.log)

        finally:
            self.elapsed = time.time() - self.tinit
            self.log.info("%s - %.2fs", str(self), self.elapsed)

    def assert_that(self, actual, matcher, reason=''):
        condition = DeferredAssertion(self, actual, matcher, reason)
        self._add_condition(condition)
        return condition

    def wait_that(self, actual, matcher, reason='', timeout=5, each=1):
        condition = PollDeferredAssertion(
            self, actual, matcher, reason, timeout, each)
        self._add_condition(condition)
        return condition

    def _add_condition(self, condition):
        if not self.body_defined:
            self.pre.append(condition)
        else:
            self.post.append(condition)

    def do_run(self):
        raise NotImplementedError

    def is_running(self):
        return self.status == Status.UNKNOWN

    def is_finished(self):
        return self.status not in [Status.UNKNOWN, Status.NOEXEC]

    def terminate(self):
        raise NotImplementedError('terminate')

    def _enable_outs_if_requested(self):
        self._enable_out('out', self.save_stdout or bool(self.stdout))
        self._enable_out('err', self.save_stderr or bool(self.stderr))

    def _enable_out(self, name, state=True):
        assert name in ['out', 'err'], "Internal Error"
        if not state:
            return

        out = getattr(self, "std%s" % name)
        if out is None:
            out = os.path.join(PREGO_TMP, '%s.%s' % (self.index, name))

        if isinstance(out, str):
            out = tools.create_file(out, 'w', 0)

        if isinstance(out, file):
            assert out.mode == 'w', "%s must be writable" % out.name
            out = File.from_fd(out)

        setattr(self, "std%s" % name, out)
        setattr(self, "save_std%s" % name, True)
        self.gen.append(out)

    def eval_conditions(self, conditions, name=''):
        if not conditions:
            return

        for c in conditions:
            c.eval()
            self.log.info("%s condition: %s", Status.OK.pretty(), c)

        self.log.info("%s all %sconditions", Status.OK.pretty(), name)

    def wait_detached(self, timeout=None):
        if self.thread:
            self.thread.join(timeout)

    def set_reason(self, status, reason):
        self.status = status
        self.reason = reason
        self.log.error("{0} {1}".format(status.pretty(), reason))

    def remove_gen(self):
        for f in self.gen:
            self.log.info("removing %s", f)
            f.remove()


class Test(Task):
    def __init__(self, *args, **kargs):
        self.expected = checked_type(int, kargs.pop('expected', 0))
        self.timeout  = checked_type((int, NoneType), kargs.pop('timeout', 5))
        self.signal   = checked_type(int, kargs.pop('signal', signal.SIGTERM))
        super(Test, self).__init__(*args, **kargs)
        self.cmd = None
        self.sp = None

    @property
    def returncode(self):
        if self.sp is None:
            return None

        return self.sp.returncode

    def set_cmd(self, cmd):
        if self.cmd is not None:
            raise CommandAlreadyDefined(self.cmd)

        self.cmd = self.interpolator.apply(cmd)
        self.body_defined = True

    def do_run(self):
        def decorate_out_with_logger(out, prefix):
            if out is None:
                return

            out_logger = self.create_logger(prefix)
            return FileTee(out, LoggerAsFile(out_logger.info))

        if self.cmd is None:
            return Status.OK

        stdout = decorate_out_with_logger(self.stdout, 'out')
        stderr = decorate_out_with_logger(self.stderr, 'err')

        self.sp = SubProcess(
            self.cmd,
            stdout=stdout, stderr=stderr,
            close_outs=True,
            cwd=self.cwd,
            shell=True,
            signal=self.signal,
            logger=self.log)

        self.wait()

        if self.status == Status.FAIL:
            return Status.FAIL

        if self.returncode != self.expected:
            self.reason = "Unexpected returncode: {0} != {1}".format(
                self.expected, self.returncode)
            return Status.FAIL

        return Status.OK

    def wait(self):
        if self.timeout is not None:
            try:
                self.check_timeout()

            except TimeoutExceeded as e:
#                self.meet_expectations = False
                reason = "timeout exceeded: {0:1.2f}s >= {1:1.2f}s".format(
                    e.elapsed, self.timeout)

                #FIXME: only sync_run may set status
                self.set_reason(Status.FAIL, reason)
                self.sp.terminate()

        self.sp.wait()
        self.terminated = True

    def check_timeout(self):
        while time.time() - self.tinit < self.timeout and \
                self.sp.poll() is None:
            time.sleep(0.5)

        if self.sp.poll() is None:
            raise TimeoutExceeded(time.time() - self.tinit)

    def terminate(self):
        if self.sp is None:
            self.log.info('terminate: task never started')
        else:
            self.sp.terminate()
        self.terminated = True

    def __str__(self):
        cmd = self.sp or repr(self.cmd)
        return "{0} Test {1} {2} detach:{3}".format(
            self.status.pretty(), self.expected, cmd, self.detach)


# FIXME
def command(cmd, **kargs):
    test = Test(**kargs)
    test.set_cmd(cmd)
    return test


def verify():
    Runner(tasks).run()


def run():
    try:
        verify()
    except TestFailed:
        return Status.FAIL

    return Status.OK


def init():
    del tasks[:]


def prego(func):
    def wrapper(*args, **kargs):
        init()
        func(*args, **kargs)
        verify()

    wrapper = nose.tools.make_decorator(func)(wrapper)
    return wrapper
