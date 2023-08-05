# Copyright (C) 2011 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
"""Decorators indicating transactional functions/methods."""
from time import sleep
from random import uniform
from logging import getLogger

from decorator import decorator

from transaction import begin, get
from ZODB.POSException import ConflictError


logger = getLogger(__name__)


class TransactionManager(object):
  """Base class to handle transactional functions/methods.

  The `__call__` method can be used as decorator for transactional
  functions/methods. It causes the decorated function to be called
  in a transaction frame: transaction metadata is registered,
  the function is called and then the transaction
  is either commited or aborted, when the call succeeds or an exception
  is raised, respectively. In case of a `ConflictError`, the call
  may be retried under control of `retry` configuration parameters.

  A transaction frame is only implemented on top level: if a nested
  transactional function/method is called, it is simply called and
  no special action performed.
  Note that only transactions handled by a `TransactionManager` are
  recognized. There is no reliable way to detect that a transaction
  is managed by some higher level.
  """

  # may be overridden by derived classes or in the constructor
  retry_number = 3 # maximal number of retrial
  retry_initial_delay = 1 # in seconds
  retry_delay_factor = 2
  retry_exceptions = (ConflictError,)

  # private: do not touch
  __tag = __name__ + "_tag"

  # metadata determination: may be overridden by derived classes
  def get_user_info(self):
    """should return `None` or a pair *name*, *path*."""
    return None

  def get_description(self, f, args, kw):
    """should return a string."""
    return str(f)


  def __init__(self, retry_number=None, retry_initial_delay=None, retry_delay_factor = None):
    if retry_number is not None: self.retry_number = retry_number
    if retry_initial_delay is not None: self.retry_initial_delay = retry_initial_delay
    if retry_delay_factor is not None: self.retry_delay_factor = retry_delay_factor


  def __call__(self, f):
    def wrap(f, *args, **kw):
      T = get() # current transaction
      if getattr(T, self.__tag, False):
        # nested -- just call the function
        return f(*args, **kw)
      # top level
      retry_count = 0; retry_delay = self.retry_initial_delay
      while True:
        T = begin() # new transaction; pending transaction aborted
        setattr(T, self.__tag, True) # mark to detect nested operations
        try:
          user_info = self.get_user_info()
          if user_info is not None: T.setUser(*user_info)
          description = self.get_description(f, args, kw)
          T.note(description)
          try:
            r = f(*args, **kw)
            T.commit()
            return r
          except self.retry_exceptions:
            T.abort()
            if retry_count >= self.retry_number: raise
            # might want to add more traceback information
            logger.exception("retrying %s", description)
            retry_count += 1
            sleep(uniform(0, retry_delay))
            retry_delay *= self.retry_delay_factor
            continue
          except:
            T.abort()
            raise
        finally:
          delattr(T, self.__tag) # might not be necessary
    return decorator(wrap, f)


transactional = TransactionManager() # a transaction manager with default parameters
