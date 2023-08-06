# Copyright (C) 2011-2012 by Dr. Dieter Maurer <dieter@handshake.de>
"""Zope 2 form support for ``SchemaConfigured``."""

try: from Products.Five.formlib.formbase import EditForm, DisplayForm, PageForm
except ImportError:
  # some Zope version dropped `formlib` support from `Five`; try `five.formlib`
  from five.formlib.formbase import EditForm, DisplayForm, PageForm

from dm.zope.schema.form import SchemaConfiguredFormMixin

# simple ZMI supporting template
from template import form_template

class ZmiMixin(object):
  template = form_template
  support_zmi = True


class SchemaConfiguredEditForm(SchemaConfiguredFormMixin, EditForm): pass

class SchemaConfiguredDisplayForm(SchemaConfiguredFormMixin, DisplayForm): pass

class SchemaConfiguredZmiEditForm(ZmiMixin, SchemaConfiguredEditForm): pass
class SchemaConfiguredZmiDisplayForm(ZmiMixin, SchemaConfiguredDisplayForm): pass
