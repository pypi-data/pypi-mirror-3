The ZODB is a mostly easy to use object oriented database -- especially,
when used within a framework which provides transaction management (such
as Zope). Nice features are the almost transparent persistency (modified
objects are automatically stored when the transaction is committed)
and the absence of locking requirements (due to an optimistic
concurrency control). However, the ZODB becomes a bit difficult when
operations need to be performed asynchronously, i.e. in a separate thread.

This package contains some utilities to make it easier to implement
asynchronous access to the ZODB. Some of those can be helpful, too,
in a synchronous environment.


Dependencies
============
The package depends on ``decorator``, ``transaction``,
``dm.transaction.aborthook`` and ``ZODB3`` (>= 3.8).
The ZODB dependancy is not declared in ``setup.py`` because I need
the package in an environment where the ZODB is not used eggified.

The module ``zope2`` depends on Zope 2 (>= 2.10). This dependancy, too,
is not declared (for identical reasons).


Modules
=======

The package consists of modules ``transactional``, ``scheduler``,
``context`` and ``zope2``. 

Detailed information can be found in the source via docstrings.


``transactional``
-----------------

``transactional`` contains decorators which provide transaction management
in environments where this is not provided by the framework.
They can be useful even in a synchronous environment (e.g. a script
environment). The transaction management comprises automatic retry
after concurrency problems (which the ZODB indicates by so a
called ``ConflictError``).

Its main content is the decorator ``transactional``, a particular
instance of the class ``TransactionManager``. ``transactional``
(and other instances of ``TransactionManager``) declare a function or method to
be transactional: before the function is called, a new transaction
is begun (a potentially pending transaction aborted), metadata is registered
for the transaction
and when the function returns the transaction is either committed (no exception)
or aborted (exception). If the exception was a ``ConflictError``, the
call is retried up to a configurable number of times after configurable delays.

``transactional`` (and other instances of ``TransactionManager``)
have effect only at the top level, as the ZODB does not support fully
nested transactions (it can, however, partially emulated
nested transactions by so called "savepoint"s).
Nested calls (inside the same transaction) simply
call the decorated function/method. The decorators recognize only
their own transaction management: if the transaction is managed on higher
level, this is not recognized and control is taken over.

Example
,,,,,,,

In this section, we set up a simple example that demonstrates
how ``transactional`` (and other instances of
``TransactionManager``) is used and what it does.

``transactional`` manages transactions. Therefore, it is
useful to be able to monitor transaction management.
We use after commit hooks (directly provided by ``transaction``)
and abort hooks (provided by ``dm.transaction.aborthook``).
With them, we define the auxiliary function ``register_hooks`` which
will monitor transaction aborts and commits. We also set up logging
to see logging messages.

>>> import transaction
>>> 
>>> def register_hooks(text):
...   """register transaction hooks such that we can monitor transaction operation"""
...   def show(status, type):
...     print "transaction %s:" % type, text
...   T = transaction.get() # current transaction
...   T.addAfterCommitHook(show, ("commit",))
...   T.addAfterAbortHook(show, (False, "abort"))
... 
>>> from logging import basicConfig
>>> basicConfig()

We now define two simple transactional functions ``f`` and ``g``
with ``f`` calling ``g`` and then call ``f``.

>>> @transactional
... def f(a=1, b=2):
...   register_hooks("f")
...   print "f:", a, b
...   g(2*a)
...   print "after g call"
...   return a + b
... 
>>> @transactional
... def g(x):
...   register_hooks("g")
...   print "g:", x
... 
>>> f()
f: 1 2
g: 2
after g call
transaction commit: f
transaction commit: g
3

The output tells us, that transaction commit hooks have been
called. This means that some transaction has been commited.
In addition, the ``g`` transaction commit hook was not called at
the end of the ``g`` call but at the end of the ``f`` call.
This means that the ``g`` call has not introduced its own transaction
level but participates on that of ``f`` -- even though, ``g`` has
be declared transactional. When we call ``g`` directly, we see that
in this case, it gets its own transaction control.

>>> g(1)
g: 1
transaction commit: g


Should a transactional method raise an exception, the transaction
is aborted and the exception is propagated:

>>> @transactional
... def raise_exception():
...   register_hooks("raise exception")
...   print "raise exception"
...   raise ValueError()
... 
>>>> raise_exception()
raise exception
transaction abort: raise exception
Traceback (most recent call last):
  ...
ValueError


In case of a ``ConflictError``, the call is automatically retried
(in a new transaction). Retrial may be repeated (how often is
controlled by a ``TransactionManager`` attribute) with increasing
randomly chosen delays between retries (also controlled
by ``TransactionManager`` attributes).

For demonstrational purposes, we define
a class for with the first call raises ``ConflictError`` and the second
call succeeds. Therefore, the first retrial succeeds and the example
will not show further retrials.

>>> class ConflictRaiser(object):
...   raised = False
...   
...   @transactional
...   def __call__(self):
...     register_hooks("conflict raiser")
...     if self.raised: print "conflict raiser returns without exception"
...     else:
...       print "conflict raiser raises `ConflictError`"
...       self.raised = True
...       from ZODB.POSException import ConflictError
...       raise ConflictError()
... 
>>> cr = ConflictRaiser()
>>> cr()
conflict raiser raises `ConflictError`
transaction abort: conflict raiser
ERROR:dm.zodb.asynchronous.transactional:retrying __call__
Traceback (most recent call last):
  ...
ConflictError: database conflict error
conflict raiser returns without exception
transaction commit: conflict raiser




``scheduler``
-------------

This module defines the class ``TransactionalScheduler`` which supports
the following use case: some context starts an operation in a separate
thread and then terminates; a different context later checks whether
the operation has completed and if so processes the results.
The use case arises for example in a web application (such as Zope) for
long running operations which should be processed asynchronously
(in a separate thread) rather than inline (in the originating request)
to provide useful partial results or feedback immediately. Later results
are fetched and presented e.g. via dynamic (AJAX, Web 2) techniques.

The initial schedule returns an identifier which can later be used
to check for and access results.

The function becomes nontrivial when the operation must access the ZODB.
The ZODB forbids a thread to access persistent objects loaded in
a separate thread. Therefore, persistent objects accessed asynchronously
must be reloaded from the ZODB via a new thread specific connection.
Without special measures, the asynchronous operation may not see modifications
to persistent objects performed by the context which has scheduled
the asynchonous operation (as they become available only after the
transaction has committed). ``TransactionScheduler`` uses the
``after-commit`` hook of ZODB transactions to start the asynchronous
operation ensuring that modifications are seen.

When the result of an asynchronous operation is fetched, its deletion
is automatically scheduled at transaction commit. A deletion timeout
controls deletion of results which got "forgotten".

Example
,,,,,,,

This example demonstrates the working of the
``TransactionalScheduler``. We set up logging, a scheduler (``s``)
and a simple function (``show``)
with prints something and returns something so that we can monitor
when it is called.

>>> from transaction import abort, commit
>>> from logging import basicConfig
>>> basicConfig()
>>>
>>> import dm.zodb.asynchronous.scheduler
>>> s = dm.zodb.asynchronous.scheduler.TransactionalScheduler()
>>> 
>>> def show(*args, **kw):
...   print "show:", args, kw
...   return "ok"
... 

The scheduling returns an id which can be used to learn about
the operation's fate via a ``get_result`` call.
If ``get_result`` returns ``None``, the schedule is unknown
(probably lost); ``False`` means known but not yet complete.
Finally, ``get_result`` may return a tuple *return-value*, *exception*.

After a new schedule, the schedule is known but not yet complete.

>>> sid = s.schedule(show, 1, 2, a="a")
>>> s.get_result(sid)
False

A transaction abort deletes the schedule.

>>> abort()
>>> s.get_result(sid)

If the transaction is commited, the scheduled operation is
called.

>>> sid = s.schedule(show, 1, 2, a="a")
>>> commit()
show: (1, 2) {'a': 'a'}

After the completion, ``get_result`` returns its result.
A transaction abort does not delete the result. However, a commit
will.

>>> s.get_result(sid)
('ok', None)
>>> abort()
>>> s.get_result(sid)
('ok', None)
>>> commit()
>>> s.get_result(sid)

We now schedule ``exc``, a function which raises an exception.

def exc(): raise Exception()
... 
>>> sid = s.schedule(exc)
>>> commit()
>>> ERROR:dm.zodb.asynchronous.scheduler:exception in call of <function exc at 0xb687fb54>
Traceback (most recent call last):
...
Exception

Note: The output above comes from the logging; the ``commit`` does
not output anything by itself.

Again, ``get_result`` provides information about the result.

>>> s.get_result(sid)
(None, <exceptions.Exception instance at 0xb687c50c>)



``context``
-----------

This module defines the class ``PersistentContext``. It can be used
to pass persistent objects from one (thread) context to another one.
As described in the ``scheduler`` section, persistent objects cannot
simply be passed on: instead the target context must reload them
from a (new) connection associated with the target. ``PersistentContext``
records the databases and oids associated with the persistent objects
and facilitates the reloading inside the target.

See the module docstrings for details, especially
about the restrictions and risks.

An example is shown in the section "Typical Usage Example".

Note: ``PersistentContext`` does not retain any acquisition context.
This means (among others) that the Zope2 security mechanism will fail
and that the target thread will not have access to the request object
(a good thing as it gets closed asynchronously). Thus, there are
still severe limitations of what you can do in an asynchronous operation.


``zope2``
---------

This module contains adaptations of facilities defined in the other
modules to a Zope2 environment. For example, there is
an adapted ``TransactionManager`` (and derived ``transactional``
decorator) which provides transaction metadata in the way typical
for the Zope 2 framework. There is also a ``PersistantContext`` implementation
which automatically determines the root database using Zope 2 implementation
details.


Typical Usage Example
=====================

As mentioned in section ``scheduler``, the package can be used in
(e.g.) a Zope 2 environment when some operation takes too much time
to be performed inline (in the same request). In this case,
one can execute it in a separate thread and look for its results
in a following (new) request. We present now a simple example.

We define a simple ``asynchronous_operation``, for demonstrational 
purposes. In real life, the scheduler would probably be global,
e.g. provided by a so called "utility".

>>> import transaction
>>> from dm.zodb.asynchronous.zope2 import transactional, PersistentContext
>>> from dm.zodb.asynchronous.scheduler import TransactionalScheduler
>>> 
>>> 
>>> @transactional
... def asynchronous_operation(context):
...   print "asynchronous_operation"
...   return (context["param"].x, context[0].x)
... 
>>> scheduler = TransactionalScheduler()

We simulate now a request which schedules ``asynchronous_operation``
and allows it to access the ``app`` object (the Zope2 root object)
via ``PersistentContext``. ``PersistentContext`` supports both positional
as well as keyword parameters. For demonstational purposes, we
pass ``app`` both positional as well as via the keyword ``param``.
Inside ``asynchronous_operation``, subscription is used to access the
persistent objects; an integer index accesses positional arguments, an ``str``
index the keyword arguments.

The scheduling returns an id which (in real life) would somehow be
stored (e.g. in the user session or (better) be incorporated inside
the generated response and be used as parameter of a followup request).
The assignment to ``app.x`` is used to demonstrate that
``asynchronous_operation`` sees modifications performed in the
original request (even when they happen after the scheduling).

At the end of the initial request, there will be either
a ``transaction.abort()`` or a ``transaction.commit()``. In the former
case, the schedule will be removed and ``asynchronous_operation`` not
started. In the latter case, ``asynchronous_operation`` will start.

>>> sid = scheduler.schedule(asynchronous_operation,
...                          PersistentContext(app, param=app)
...                          )
>>> print sid
1a1e2d987b154945b7da12d6b09ed658
>>> app.x = 1
>>> 
>>> transaction.commit()
asynchronous_operation

We look now at the followup request. Things must somehow have
been set up that it can access the same ``scheduler`` (usually
done via an utility). Somehow, the followup request has learned
of the schedule id (from the user session or via a request parameter).
With this information, it can check the fate of the asynchronous
operation, process the result and commit.

>>> r = scheduler.get_result(sid)
>>> if r is None: print "lost schedule"
... elif not r: print "operation not yet complete"
... else:
...   (rv, exc) = r
...   if exc is not None:
...     # the asynchronous operation has raised *exc*.
...     # Do not reraise it! It belongs to a different context.
...     # If you raise a different exception, you might want
...     #   to call ``scheduler.remove(sid)``; otherwise, the schedule
...     #   gets removed only after timeout.
...     # Usually, you would not raise an exception but only provide information
...     # about the failure of the asynchronous operation
...     print "exceptioon: ", exc
...     #return process_exception(exc)
...   else:
...     print rv
...     #return process_return_value(rv)
... 
(1, 1)
>>> transaction.commit()
 
The code snippet above has an extended comment about exception
handling from ``asynchronous_operation`` (in our trivial exemple, there
will be no exception). Note that a failing asynchronous operation
does not mean that the current request has failed. The purpose of the
current request is to inform us about the fate of the asynchronous
operation, not to perform this operation. Therefore, a failure
of the asynchronous operation usually should result in the success
of the current request (no exception) -- with appropriate information
that the asynchronous operation has failed.
In our exemple, we have decorated ``asynchronous_request`` with
``transactional``. This way, it handles transaction management correctly
in case of errors (the transaction gets aborted when the
asynchronous operation should fail).
