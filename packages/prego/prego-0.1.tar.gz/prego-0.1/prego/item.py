# -*- coding:utf-8; tab-width:4; mode:python -*-

import os
from commodity.type_ import checked_type

from .tools import Printable


class File(Printable):
    def __init__(self, fpath, fd=None):
        self.fpath = checked_type(str, fpath)
        self.fd = fd

    @classmethod
    def from_fd(cls, fd):
        fd = checked_type(file, fd)
        assert not fd.closed, fd
        return File(fd.name, fd)

    def read(self):
        with file(self.fpath) as fd:
            return fd.read()

    def write(self, data):
        self._assure_open()
        self.fd.write(data)

    def flush(self):
        self._assure_open()
        self.fd.flush()

    @property
    def closed(self):
        return self.fd.closed

    def close(self):
        assert not self.fd.closed
        self.fd.close()

    def _assure_open(self):
        if self.fd is None:
            self.fd = file(self.fpath, 'w', 0)

        if self.fd.closed:
            raise ValueError('%s was closed' % self.fd.name)

#    def find(self, substring):
#        with file(self.fpath) as fd:
#            return fd.read().find(substring)

    def exists(self):
        return os.path.exists(self.fpath)

    def remove(self):
        if self.exists():
            os.remove(self.fpath)

    @property
    def content(self):
        return self.read()

    def __unicode__(self):
        return u"File({0!r})".format(self.fpath)


class DeferredItem(object):
    def __init__(self):
        self.task = None

    def config(self, task):
        self.task = task


class OutContent(DeferredItem):
    def __init__(self, out):
        super(DeferredItem, self).__init__()
        self.out = out

    def config(self, task):
        DeferredItem.config(self, task)
        self.out.config(task)

    def get_value(self):
#        print self.out.get_value()
        return self.out.get_value().content

    def __str__(self):
        return "{0} content".format(self.out)


class OutBase(DeferredItem):
    @property
    def content(self):
        return OutContent(self)


class StdOut(OutBase):
    def config(self, task):
        OutBase.config(self, task)
        task._enable_out('out')

    def get_value(self):
        return self.task.stdout

    def __str__(self):
        return "{0} stdout ({1})".format(
            self.task.name, self.task.stdout.fpath)


class StdErr(OutBase):
    def config(self, task):
        OutBase.config(self, task)
        task._enable_out('err')

    def get_value(self):
        return self.task.stderr

    def __str__(self):
        return "{0} stderr ({1})".format(
            self.task.name, self.task.stderr.fpath)
