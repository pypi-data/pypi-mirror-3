# Copyright (C) 2011 by Dr. Dieter Maurer <dieter@handshake.de>
"""form support for ``SchemaConfigured`` classes.

This module requires ``zope.formlib``.
"""
from zope.interface import providedBy
from zope.formlib.form import EditForm, DisplayForm, Fields

from schema import schemaitems


class SchemaConfiguredFormMixin(object):
  """mixin class for ``SchemaConfigured`` forms.

  It redefines ``__init__`` to generate the fields from *context*
  and then calls ``customize_fields`` (if defined) to allow
  for field customization.
  """

  def __init__(self, context, request):
    super(SchemaConfiguredFormMixin, self).__init__(context, request)
    self.define_fields()


  def define_fields(self):
    self.form_fields = Fields(
      *(i[1] for i in schemaitems(self.context.sc_schema_spec()))
      )
    self.customize_fields()


  def customize_fields(self):
    """to be overridden by derived classes."""
    pass


class SchemaConfiguredEditForm(SchemaConfiguredFormMixin, EditForm): pass

class SchemaConfiguredDisplayForm(SchemaConfiguredFormMixin, DisplayForm): pass
