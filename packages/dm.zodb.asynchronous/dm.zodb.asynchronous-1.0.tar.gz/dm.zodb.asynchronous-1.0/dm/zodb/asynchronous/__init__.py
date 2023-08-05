# Copyright (C) 2011 by Dr. Dieter Maurer <dieter@handshake.de>
"""Utilities for asynchronous operations accessing the ZODB."""

# we need before abort hooks
from dm.transaction.aborthook import add_abort_hooks
add_abort_hooks()
