#--
# Copyright (c) 2008-2012 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

import stackless

tasklet_contexts = {}


class DummyLock(object):
    acquire = release = lambda self: None


class TaskletContext(object):
    pass


def get_context_id():
    current = stackless.getcurrent()
    return getattr(current, '_nagare_local', id(current))


class TaskletsContext(object):
    def create_lock(self):
        return DummyLock()

    def start_request(self):
        global tasklet_contexts
        tasklet_contexts[get_context_id()] = TaskletContext()

    def end_request(self):
        del tasklet_contexts[get_context_id()]

    def __setattr__(self, name, v):
        setattr(tasklet_contexts[get_context_id()], name, v)

    def __getattr__(self, name):
        return getattr(tasklet_contexts[get_context_id()], name)


class Tasklet(stackless.tasklet):
    def __init__(self, *args, **kw):
        super(Tasklet, self).__init__(*args, **kw)
        self._nagare_local = get_context_id()

    def __setstate__(self, state):
        super(Tasklet, self).__setstate__(state)
        self._nagare_local = get_context_id()
