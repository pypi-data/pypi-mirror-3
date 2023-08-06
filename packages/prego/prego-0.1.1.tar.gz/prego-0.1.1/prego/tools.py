# -*- coding:utf-8; tab-width:4; mode:python -*-

import string
import os
import socket
import traceback
import logging

from commodity.log import CapitalLoggingFormatter

from .const import PREGO_TMP_BASE, PREGO_TMP

basedir = os.getcwd()


class Interpolator(object):
    fixed_vars = dict(
        basedir      = basedir,
        fullbasedir  = os.path.abspath(basedir),
        pid          = os.getpid(),
        tmpbase      = PREGO_TMP_BASE,
        tmp          = PREGO_TMP,
        hostname     = socket.gethostname(),
        )

    def __init__(self):
        testpath = traceback.extract_stack()[-4][0]
        testdir, testname  = os.path.split(testpath)

        self.vars = self.fixed_vars.copy()
        self.vars.update(
            dict(
                testdir      = testdir,
                fulltestdir  = os.path.abspath(testdir),
                testfilename = testname,
                ))

    def apply(self, text):
        if not isinstance(text, basestring):
            return text

        return string.Template(text).safe_substitute(self.vars)


def create_file(fpath, *args):
    path, name = os.path.split(fpath)
    if path in [PREGO_TMP, PREGO_TMP_BASE]:
        try:
            os.makedirs(path)
        except OSError:
            pass

    return file(fpath, *args)


def set_logging_formatter(log):
    if not log.handlers:
        log.addHandler(logging.StreamHandler())

    handler = log.handlers[0]
    formatter = CapitalLoggingFormatter(
        '[%(levelcapital)s] %(name)s %(message)s')
    handler.setFormatter(formatter)


def create_logger(name):
    retval = logging.getLogger(name)
    retval.setLevel(logging.DEBUG)
    retval.propagate = True
    return retval

#    formatter = CapitalLoggingFormatter('[%(levelcapital)s] %(name)s %(message)s')
#    console = logging.StreamHandler()
#    console.setFormatter(formatter)
#    retval.addHandler(console)
##    retval.addHandler(NullHandler())
#    retval.propagate = False
#    return retval


class Printable(object):
    def __repr__(self):
        return str(self)

    def __str__(self):
        return unicode(self).encode('utf-8', 'replace')
