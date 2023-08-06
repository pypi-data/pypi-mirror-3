# -*- coding:utf-8; tab-width:4; mode:python -*-

import logging
import traceback

#from .tools import Printable


class TestFailed(Exception):
    def __init__(self, task):
        self.task = task
        reason = "{0}: {1}".format(task.name, task.reason)
        super(Exception, self).__init__(reason)


class ConditionException(Exception):
    def __init__(self, condition):
        self.condition = condition
        super(Exception, self).__init__(condition)


class ConditionFailed(ConditionException):
    pass


class ConditionError(ConditionException):
    pass


class TimeoutExceeded(Exception):
    def __init__(self, elapsed):
        self.elapsed = elapsed
        super(Exception, self).__init__(elapsed)


class CommandAlreadyDefined(Exception):
    pass


def log_exc(exc, logger=logging):
    for line in str(exc).splitlines():
        if line.strip():
            logger.error('| ' + line)


def log_traceback(logger=logging):
    for line in traceback.format_exc().splitlines():
        if line.strip():
            logger.error('| ' + line)
