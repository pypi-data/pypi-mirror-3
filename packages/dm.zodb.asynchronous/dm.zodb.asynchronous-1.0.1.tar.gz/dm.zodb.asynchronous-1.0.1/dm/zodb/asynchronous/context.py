# Copyright (C) 2011 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
"""Pass persistent objects across threads.

The ZODB forbids to pass persistent objects across thread boundaries.
To be more precise: in the standard ZODB execution model, connections
are (indirectly, via transactions) associated with threads and a thread must
only access persistent objects loaded via connections associated with itself.
Failure to observe this restriction can lead to non deterministic
(`ConnectionStateError`) errors or even persistent data corruption.

This module defines the class `PersistentContext` which helps
to handle this limitation. One thread can construct an instance with
persistent objects and then pass the instance to a different thread.
This can then get access to the persistent objects.

`PersistentContext` does not directly manage the persistent objects
but instead identifies them by their ZODB and their oid. On access,
they are loaded from the ZODB properly via a connection associated
with the accessing thread, newly opened if necessary.

The function is not without risk: it is dangerous to access a
given ZODB via several connections in the same transaction (this may lead
to deadlock during `commit`).
`PersistentContext` prevents this for the connections it opens itself.
However, it does not have any knowledge about connections opened
independently by the target thread. Usually, only the root database
is opened independently; all other databases are opened indirectly
via the root connection. In this case, `PersistentClass` knows about
the dependently opened connections and the problem is limited to
the root database. `PersistentClass.get_root_connection()` can be used
to get a proper root connection avoiding the need for the target
thread to open its own connection.
If a ``PersistentContext`` is used to return the result of an asynchronous
operation, it is likely that the receiving target already has a root connection
opened. For this use case, ``PersistentContext`` hat the method
``set_root_connection`` to inform ``PersistentContext`` about the root connection to use. Note that the root connection is stored on the current transaction
and lost at transaction boundaries.

The persistent objects passed in a `PersistentContext` across
thread boundaries are reloaded in the destination thread.
This implies that modifications to those objects in the source thread
may not be seen in the destination thread as they become visible only
after a successful commit. `scheduler.TransactionalScheduler` can
be used (in some cases) to ensure that modifications are seen
(it delays a thread start until a successful transaction commit).

When a `PersistentContext` instance is constructed, it must be able
to determine its associated ZODB and oid. If necessary, it performs
a `transaction.savepoint` to get those information. This will work for
persistent objects which are already part of the graph of persistent objects.
It will fail for persistent objects which do not yet form part of this
graph; a `ValueError` is raised in this case.
"""
import transaction

class PersistentContext(object):
  """see module docstring."""

  def __init__(self, root_db, *objs, **kwobjs):
    """create a persistent context for persistent objects from *objs* and *kwobjs*.

    Subscription syntax (`[...]`) can be used to access
    the managed persistent objects.
    `int` keys access *objs*, `str` keys *kwobjs*.

    All objects must be persistent objects (otherwise `AttributeError` occurs)
    and must be part of the graph of persistent objects (otherwise
    `ValueError` occurs).

    *root_db* is the ZODB root database.
    This is a bit awkward: modern ZODB versions do not have this concept
    but instead use the `multidatabase` notion where multiple databases
    are at the same level. However, `PersistentContext` needs this concept
    to reduce the risk of multiple connections to the same database.
    It opens all database connections via a connection to the root
    database and assumes that the destination thread does this too.
    """
    self._db = root_db
    savepoint_called = False

    def identify(obj):
      """determine database and oid for *obj*.

      return pair *savepoint_called*, *id*.
      """
      sc = savepoint_called
      jar, oid = obj._p_jar, obj._p_oid # `AttributeError` if not persistent
      if oid is None:
        # this is a new object
        if not sc:
          transaction.savepoint() # try to associate a database
          sc = True
      jar, oid = obj._p_jar, obj._p_oid # `AttributeError` if not persistent
      if jar is None or oid is None:
        raise ValueError("obj %r not part of the graph of persistent objects" % obj)
      return sc, (jar.db().database_name, oid)

    self._objs = oids = []
    for o in objs:
      savepoint_called, oid = identify(o)
      oids.append(oid)

    self._kwobjs = kwids = {}
    for k, o in kwobjs.iteritems():
      savepoint_called, oid = identify(o)
      kwids[k] = oid


  def __getitem__(self, k):
    """access persistent object -- reload from proper connection."""
    if isinstance(k, int): i = self._objs
    else: i = self._kwobjs
    return self.__resolve(i[k]) # may raise `IndexError` or `KeyError`.

  # length information for positional objects
  def __len__(self): return len(self._objs)

  # mapping access for keyword objects
  def get(self, k, default=None):
    i = self._kwobjs.get(k)
    if i is None: return default
    return self.__resolve(i)

  def keys(self): return self._kwobjs.keys()
  def iterkeys(self): return self._kwobjs.iterkeys()


  def get_root_connection(self):
    T = transaction.get() # current transaction
    root_connection = getattr(T, self.__tag, None)
    if root_connection is None:
      root_connection = self._db.open()
      self.set_root_connection(root_connection, True)
    return root_connection

  def set_root_connection(self, root_connection, close=False):
    T = transaction.get() # current transaction
    rc = getattr(T, self.__tag, None)
    if rc is not None:
      if rc != root_connection:
        raise ValueError("root connection already set up")
      else: return
    setattr(T, self.__tag, root_connection)
    if close:
      T.addAfterCommitHook(self.__close_root_connection, (T,))
      T.addAfterAbortHook(self.__close_root_connection, (False, T,))



  # internal -- do not touch
  __tag = __name__ + '_tag'

  def __resolve(self, (db_name, oid)):
    """return the persistent object identified by *db_name* and *oid*.

    The object is properly loaded from a connection associated with
    the current thread (indirectly via the current transaction).
    """
    rc = self.get_root_connection()
    c = rc.get_connection(db_name)
    return c[oid] # may raise `POSKeyError` or old state


  def __close_root_connection(self, status, T):
    root_connection = getattr(T, self.__tag)
    root_connection.close()
    delattr(T, self.__tag)


      
