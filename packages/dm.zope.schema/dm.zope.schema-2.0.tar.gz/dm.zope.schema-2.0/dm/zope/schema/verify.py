# Copyright (C) 2010 by Dr. Dieter Maurer <dieter@handshake.de>
"""Schema verification.

This is a companion to ``zope.interface.verify`` which verifies methods
but does not do anything with schema fields.
"""

from schema import Object

def verify_schema(iface, obj, context=None, check_declaration=True):
  """verify that *obj* satisfies the schema requirements of *iface*.

  *context* specifies the context for schema binding. It defaults to *obj*.

  *check_declaration* checks that *obj* declares to provide *iface*.
  """
  if context is None: context = obj
  Object(iface, check_declaration=check_declaration).bind(context).validate(obj)
