# -*- coding: utf-8 -*-
'''
Created on 9 Nov 2016

@author: mhaa
'''
import contextlib

from util import util
import logging
import collections
from threading import local

_threadlocals = local()

logger = logging.getLogger('dws')

_tlocal = local()
_tlocal.pending_updates = None
_sentinel = object()

@util.log_arguments
def validate_now_or_later(objs):
    # NOTE: need to make sure that the transaction is not committed before validation is finally done
    if not util.is_sequence(objs):
        objs = [objs]
    for obj in objs:
        if obj.pk:
            duplicate_check_key = 'validate_%s' % obj.pk
        else:
            duplicate_check_key = None  # no reliable way to prevent duplicate validations
        call_now_or_later(obj.validate, duplicate_check_key)


@util.log_arguments
def call_now_or_later(func, duplicate_check_key=None):
    if _tlocal.pending_updates is None:
        func()
    else:
        if duplicate_check_key is None:
            duplicate_check_key = (_sentinel, len(_tlocal.pending_updates), func.__name__)  # unique
        _tlocal.pending_updates[duplicate_check_key] = func


@util.log_exceptions_w(stats=True)
@util.log_execution_w()
def do_pending_updates():
    util.validate(_tlocal.pending_updates is not None, 'ERROR 482030423: must be used only with update_at_end')
    for k, func in list(_tlocal.pending_updates.items()):
        logger.debug('do_pending_updates: %s %s', k, func)
        func()
    _tlocal.pending_updates.clear()


@contextlib.contextmanager
def update_at_end():
    # can be used both as context manager and decorator, like:
    # @delay_updates_until_end_of_block()
    # def foo():
    #     ...
    util.validate(_tlocal.pending_updates is None,
                  'ERROR 382932: nested update_at_end not supported - need to use contextlib.ContextDecorator')
    _tlocal.pending_updates = collections.OrderedDict()
    try:
        yield
        do_pending_updates()
    finally:
        # tested 2017-01: finally block is executed if wrapped function throws when using as a decorator
        _tlocal.pending_updates = None


def is_updates_pending():
    return _tlocal.pending_updates is not None and len(_tlocal.pending_updates) > 0
