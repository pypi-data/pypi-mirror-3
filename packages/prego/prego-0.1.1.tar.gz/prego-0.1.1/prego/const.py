#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

import os
import pwd

PREGO_TMP_BASE = os.path.join('/tmp', 'prego-{0}'.format(pwd.getpwuid(os.getuid())[0]))
PREGO_TMP = os.path.join(PREGO_TMP_BASE, str(os.getpid()))


class Status:
    _FAIL    = 0
    _OK      = 1
    _ERROR   = 2
    _NOEXEC  = 3
    _UNKNOWN = 4

    stringfied_values = {
        _FAIL:    ('FAIL',    'FAIL'),
        _OK:      ('OK',      'OK'),
        _ERROR:   ('ERROR',   '!!'),
        _NOEXEC:  ('NOEXEC',  '--'),
        _UNKNOWN: ('UNKNOWN', '??')}

    def __init__(self, value=None):
        if value is None:
            value = self._NOEXEC
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.stringfied_values[self.value][0]

    def pretty(self):
        return "[{0:^4}]".format(self.stringfied_values[self.value][1])

    @classmethod
    def define_statuses(cls):
        Status.FAIL    = Status(Status._FAIL)
        Status.OK      = Status(Status._OK)
        Status.ERROR   = Status(Status._ERROR)
        Status.NOEXEC  = Status(Status._NOEXEC)
        Status.UNKNOWN = Status(Status._UNKNOWN)

#def as_status(func):
#    def wrapper(*args, **kargs):
#        try:
#            retval = func(*args, **kargs)
#        except Exception as e:
#            return Status.ERROR
#
#        if retval:
#            return Status.OK
#
#        return Status.FAIL
#    return wrapper

Status.define_statuses()
