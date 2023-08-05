# Copyright (C) 2011 by Dr. Dieter Maurer, Illtalstr. 25, D-66571 Bubach, Germany
# see "LICENSE.txt" for details
"""Zope 2 specific adaptations.

This requires `Zope2` (>= 2.10).
"""


###############################################################################
## TransactionManager
##
## We know, how to derive user information in the Zope 2 environment.
## We also try to use a description similar to that used by Zope 2

from AccessControl import getSecurityManager

from transactional import TransactionManager

class TransactionManager(TransactionManager):

  def get_user_info(self):
    user = getSecurityManager().getUser()
    if user is not None:
      info = (user.getId(),)
      uf = hasattr(user, "aq_parent") and user.aq_parent or None
      if uf is not None:
        info += ("/".join(uf.getPhysicalPath()[1:-1]),)
      return info

  def get_description(self, f, args, kw):
    """Zope 2 uses information derived from the physical path as description.
    We emulate this here (code derived from
    `Zope2.App.startup.TransactionManager.recordMetaData`).
    """
    prefix = ()
    suffix = [] # we construct it in reverse order
    if hasattr(f, "im_self") and hasattr(f, "__name__"):
      # a method
      suffix.append(f.__name__)
      f = f.im_self # `f` now is an object
    while True:
      if hasattr(f, "getPhysicalPath"):
        # this is a Zope (site building) object
        prefix = f.getPhysicalPath()
        break
      if not hasattr(f, "__name__"):
        # this is something, Zope does not understand
        suffix.append(str(f))
        break
      suffix.append(f.__name__)
      # move up the acquisition containment hierarchy
      f = getattr(f, "aq_inner", f)
      parent = getattr(f, "aq_parent", None)
      if parent is None: break
    suffix.reverse()
    return "/".join(prefix + tuple(suffix))


transactional = TransactionManager()


##############################################################################
## `PersistentContext`
##  we know how to access the root database

from context import PersistentContext
import Zope2

class PersistentContext(PersistentContext):
  def __init__(self, *objs, **kwobjs):
    super(PersistentContext, self).__init__(Zope2.DB, *objs, **kwobjs)
  
