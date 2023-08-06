# Copyright (C) 2010-2011 by Dr. Dieter Maurer <dieter@handshake.de>
"""schema related utilities."""
from zope.interface import Interface, providedBy, implements
from zope.interface.interfaces import IMethod
from zope.schema.interfaces import IField, IObject, \
     WrongContainedType, SchemaNotProvided, ValidationError, \
     SchemaNotFullyImplemented
from zope.schema import Object as ObjectBase, Bool, getFieldsInOrder

from interfaces import ISchemaConfigured


def interface_from_spec(spec, name=None, **kw):
  """build an interface from interface spec *spec*.

  This should probably go into its own package (maybe ``dm.zope.interface``).

  Note: the interfaces constructed in this way may not be picklable
  (not tested). If they are indeed not picklable, they should not be stored.
  """
  # try to guess whether "spec" is an interface or specification
  #  The implementors have broken "issubclass", we therefore need
  #  more indirect (and in principle less reliable) methods
  # if issubclass(spec, Interface):
  if hasattr(spec, 'names'):
    if name is None and not kw: return spec
    spec = (spec,)
  name = name is None and 'FromSpec' or name
  return type(Interface)(name, tuple(spec), kw)


def schemaitems(spec):
  """The schema part of interface specification *spec* as a list of id, field pairs."""
  iface = interface_from_spec(spec)
  # may want to filter duplicates out or raise an exception on duplicates
  seen = set(); items = []
  for (name, field) in getFieldsInOrder(iface):
    if name in seen: continue
    seen.add(name); items.append((name, field))
  return items


def schemadict(spec):
  """The schema part of interface specification *spec* as a ``dict``."""
  return dict(schemaitems(spec))
  

class SchemaConfigured(object):
  """Mixin class to provide configuration by the provided schema components."""

  implements(ISchemaConfigured)

  def __init__(self, **kw):
    schema = schemadict(self.sc_schema_spec())
    for k, v in kw.iteritems():
      # might want to control this check
      if k not in schema:
        raise TypeError('non schema keyword argument: %s' % k)
      setattr(self, k, v)
    # provide default values for schema fields not set
    for f, fields in schema.iteritems():
      if not hasattr(self, f): setattr(self, f, fields.default)

  # provide control over which interfaces define the data schema
  SC_SCHEMAS = None

  def sc_schema_spec(self):
    """the schema specification which determines the data schema.

    This is determined by `SC_SCHEMAS` and defaults to `providedBy(self)`.
    """
    spec = self.SC_SCHEMAS
    if spec is None: return providedBy(self)
    return spec


class SchemaConfiguredEvolution(object):
  """Mixin class to support schema evolution for `SchemaConfigured` subclasses.

  Must come early in the resulting class's `mro` to be effective.
  """
  def __setstate__(self, state):
    sst = getattr(super(SchemaConfigured, self), "__setstate__", None)
    if sst is None and isinstance(state, dict):
      self.__dict__.update(state) # default
    else: sst(state)
    SchemaConfigured.__init__(self) # provide default values for missing fields


class _IObject(IObject):
  """auxiliary interface for ``Object`` extension.

  Note: no support yet for internationalization.
  """
  check_declaration = Bool(
    title=u"check declaration",
    description=u"check that the validated object declares the provided interface",
    default=True,
    )


class Object(ObjectBase):
  """improved ``zope.schema.Object``.

  Error reports for ``zope.schema.Object`` forget to specify the
  problemativ field. This class adds them.

  Occasionally, we do not wish to check that the existance of an
  interface declaration. Make this controllable with a
  ``check_declaration`` property.
  """
  implements(_IObject)

  # work around stupid ``Field`` constructor
  def __init__(self, *args, **kw):
    if 'check_declaration' in kw:
      self.check_declaration = kw['check_declaration']
      del kw['check_declaration']
    super(Object, self).__init__(*args, **kw)

  def _validate(self, value):
    super(ObjectBase, self)._validate(value)

    # schema has to be provided by value
    if self.check_declaration and not self.schema.providedBy(value):
      raise SchemaNotProvided

    # check the value against schema
    errors = []
    for name, field in schemadict(self.schema).iteritems():
      exc = None
      try: field.validate(getattr(value, name))
      except ValidationError, error: exc = error
      except AttributeError, error: exc = SchemaNotFullyImplemented(error)
      if exc is not None: errors.append((name, exc))
    if errors:
      raise WrongContainedType(errors)
  
