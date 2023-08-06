# Copyright (C) 2011-2012 by Dr. Dieter Maurer <dieter@handshake.de>
"""Zope 2 (product class) constructor support for ``SchemaConfigured``.

Zope 2 is extended by so called "products" (which really are only
specially registered extensions). Products can register classes
which thereby become available via the so  called "add list" of
the Zope management interface. The interface between the "add list"
and the construction of class instances is implemented by
so called "constructors", provided as parameters during the
class registration via ``registerClass``.

This module allows to generate such a constructor for
classes derived from ``dm.zope.schema.SchemaConfigured``.
It makes use of a ``zope.formlib`` form generated according to
the class' schema.
"""
from Acquisition import aq_base
from zope.schema import ASCIILine
from zope.formlib.form import Fields
from zope.i18nmessageid import MessageFactory

try: from Products.Five.formlib.formbase import AddForm
except ImportError:
  # some Zope version dropped formlib" support from "Five"; try "five.formlib"
  from five.formlib.formbase import AddForm

from dm.zope.schema.form import SchemaConfiguredFormMixin

from form import ZmiMixin

_ = MessageFactory('dm_zope_schema')


class SchemaConfiguredAddForm(SchemaConfiguredFormMixin, AddForm):
  """Default add form class."""

  __id_is_field = False

  def __init__(self, context, request):
    """**ATTENTION** *context* is expected to be the object added
    not the container; the container is expected to be found in
    the acquisition context of *context*.
    """
    super(SchemaConfiguredAddForm, self).__init__(context, request)
    if hasattr(context, '__parent__'): parent = context.__parent__
    elif hasattr(context, 'aq_parent'): parent = context.aq_parent
    else: parent = None # should not happen
    self.__parent__ = parent
    # set ``render_context`` for all fields different from ``id``
    # check whether there is an ``id`` field
    for f in self.form_fields:
      if f.__name__ == 'id':
        self.__id_is_field = True
        f.get_rendered = lambda form: context.getId()
      else: f.render_context = True
    if not self.__id_is_field:
      self.form_fields = Fields(ASCIILine(__name__='id', title=u"id")) \
                         + self.form_fields

  def create(self, data):
    ob = self.context
    ob._setId(data["id"]); del data["id"]
    ob.__init__(**data)
    return aq_base(ob)

  def add(self, ob):
    parent = self.__parent__; id = ob.getId()
    parent._setObject(id, ob)
    self._finished_add = True
    ob = parent._getOb(id) # update acquisition context
    # reset self.context -- work around acquisition bug
    aq_base(self).context = ob
    return ob

  def nextURL(self): 
    return self.context.absolute_url() + '/manage_workspace'


class SchemaConfiguredZmiAddForm(ZmiMixin, SchemaConfiguredAddForm):
  zmi_support = False # makes no sense for the add form


def add_form_factory(class_, label=None, description=None, form_class=SchemaConfiguredAddForm, template=None):
  """return an add form for *class_* based on *form_class*.

  The add form can be used as an (usualy, the) *constructors* element
  of the ``registerClass`` call.

  *title* and *description* are used to set the forms *title* and
  *description*. They should be unicode
  or ``zope.i18nmessageid.MessageFactory`` instances.
  *title* defaults to "Create instance of *class_*\ " (translated
  in the translation domain ``dm_zope_schema``) and *class_*\ .__doc__.

  If you need your own template (e.g. when you are in an environment where
  the standard template does not work), you can provide it via *template*.
  Probably, it should be a
  `Products.Five.pagetemplatefile.ViewPageTemplateFile`.
  `template.form_template` might be a candidate.` 
  """
  def add_form(self, REQUEST):
    " "
    ob = class_()
    # provide parent information
    if hasattr(ob, '__of__'): ob = ob.__of__(self)
    else: ob.__parent__ = self # should we use an adapter?
    # Note: *template* might be a descriptor which has effect only when
    #  it is assigned to a class
    if template is not None: 
      class fc(form_class): pass
      fc.template = template
    else: fc = form_class
    form = fc(ob, REQUEST)
    if hasattr(form, "__of__"): form = form.__of__(self)
    if label is not None: form.label = label
    elif not form.label: form.label = _(
      u'Create instance',
      u'Create ${class_} instance',
      dict(class_=class_.__name__), # might need to unicodify the name
      )
    if description is not None: form.description = description
    elif not getattr(form, "description", "") and class_.__doc__:
      form.description = class_.__doc__
    # make the form public -- protection is garanteed by the product dispatcher
    form.__roles__ = None
    return form()
  add_form.__name__ = "add_" + class_.__name__
  return add_form
