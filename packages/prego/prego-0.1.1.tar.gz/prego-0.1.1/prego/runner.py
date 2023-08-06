# -*- coding:utf-8; tab-width:4; mode:python -*-

import os
import logging

from .const import Status, PREGO_TMP
from .exc import TestFailed

log = logging.getLogger('prego')


class Runner(object):
    def __init__(self, tasks):
        self.tasks = tasks
        self.keep_running = False

    def run(self):
        self.run_tasks()
        self.wait_detached()
        self.remove_gen()
        self.eval_tasks()

    def run_tasks(self):
        for t in self.tasks:
            t.run()
            if not self.keep_running and \
                    t.status in [Status.FAIL, Status.ERROR]:
                break

    def wait_detached(self):
        while 1:
            unfinished = self.get_unfinished_tasks()
            if not unfinished:
                return

            for t in unfinished:
                t.log.info("waiting for detached task")
                t.terminate()
                t.wait_detached(0.5)

    def remove_gen(self):
        for t in self.tasks:
            t.remove_gen()

        try:
            os.removedirs(PREGO_TMP)
        except OSError:
            pass

    def eval_tasks(self):
        for t in self.tasks:
            if t.status != Status.OK:
                raise TestFailed(t)

    def get_unfinished_tasks(self):
        return [t for t in self.tasks if t.thread
                and t.thread.isAlive()]
