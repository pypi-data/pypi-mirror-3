# Copyright (C) 2011 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
"""Scheduling asynchronous operations and managing those schedules.
"""
from time import time
from thread import start_new_thread
from logging import getLogger

import transaction

from uuidbp import uuid


logger = getLogger(__name__)


class TransactionalScheduler(object):
  """scheduler for asynchronous operations and their management."""

  # may be overridden by derived classes or the constructor
  timeout = 3600 # s; delete completions older than this (forgotten requests)

  def __init__(self, timeout=None):
    self._schedules = dict()
    self._completed = dict()
    if timeout is not None: self.timeout = timeout


  def schedule(self, f, *args, **kw):
    """schedule an asynchronous call for when the transaction commits and return id.
    """
    schedule = _Schedule((f, args, kw))
    self._schedules[schedule.id] = schedule
    transaction.get().addAfterCommitHook(self._start, (schedule,))
    transaction.get().addAfterAbortHook(self._remove, (True, schedule.id,))
    return schedule.id

  def completed(self, id):
    """`None`, `False` or `True`, if *id* is unknown, not yet completed, completed."""
    if id not in self._schedules: return None
    return id in self._completed

  def remove(self, id):
    """remove schedule *id*, if it exists."""
    self._remove(True, id)

  def get_result(self, id):
    """return the result for *id*.

    It may return `None` (*id* is unknown), `False` (*id* is known
    but not yet completed) or a pair *result*, *exception*.
    In the last case, removal of *id* is scheduled for when the transaction
    commits successfully.
    """
    schedule = self._schedules.get(id)
    if schedule is None: return
    if id not in self._completed: return False
    transaction.get().addAfterCommitHook(self._remove, (id,))
    return schedule.get_result()


  # internal
  def _complete(self, id):
    """mark *id* as completed.

    Also remove "forgotten" completions.
    """
    ct = time()
    # remove outdated schedules
    timeline = ct - self.timeout
    completed = self._completed; schedules = self._schedules
    # we assume that the number is moderate
    #  otherwise, we would need a more efficient data structure (a heap).
    for cid, t in completed.items():
      if t < timeline:
        # outdated -- we are aware that parellel threads may interfere
        try: del schedules[cid]
        except KeyError: pass
        try: del completed[cid]
        except KeyError: pass
    completed[id] = ct


  def _remove(self, status, id):
    """after commit hook to remove *id* in case of a successful transaction."""
    if status:
      # transaction successful
      # we are aware that parallel threads my interfere
      try: del self._schedules[id]
      except KeyError: pass
      try: del self._completed[id]
      except KeyError: pass


  def _start(self, status, schedule):
    """after commit hook to start *schedule* in case of a successfull transaction."""
    if status: start_new_thread(self._run_thread, (schedule,))
    else: self._remove(True, schedule.id)


  def _run_thread(self, schedule):
    """run *schedule* in a new thread."""
    schedule.run() # should not raise an exception
    self._complete(schedule.id)


class _Schedule(object):
  def __init__(self, request):
    self._request = request
    self.id = uuid().hex

  def run(self):
    request = self._request
    r, exc = None, None
    try:
      __traceback_info__ = request # for Zope
      (f, args, kw) = request
      r = f(*args, **kw)
    except Exception, e:
      # provide traceback
      logger.exception("exception in call of %r" % f)
      exc = e
    self._result = r, exc

  def get_result(self): return self._result
