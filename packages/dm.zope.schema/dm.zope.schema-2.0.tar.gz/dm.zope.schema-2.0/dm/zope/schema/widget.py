# Copyright (C) 2011-2012 by Dr. Dieter Maurer <dieter@handshake.de>
"""Some widget extensions."""
from datetime import timedelta

from zope.i18nmessageid import MessageFactory

from dm.reuse import rebindFunction


_ = MessageFactory('dm_zope_schema')

try: import zope.formlib.textwidgets
except ImportError: modern = False
else: modern = True
  
if modern:
  from zope.formlib.textwidgets import TextWidget, ConversionError, \
       PasswordWidget
  from zope.formlib.widget import DisplayWidget, InputErrors
  from zope.formlib.interfaces import IDisplayWidget, IInputWidget
else:
  from zope.app.form.browser.textwidgets import TextWidget, ConversionError, \
       PasswordWidget
  from zope.app.form.browser.widget import DisplayWidget, InputErrors
  from zope.app.form.interfaces import IDisplayWidget, IInputWidget


##############################################################################
## Timedelta support

def format_timedelta(value):
  if value is None: return ''
  pairs = []
  if value.days: pairs.append("%dd" % value.days)
  if value.seconds: pairs.append("%ds" % values.seconds)
  if value.microseconds: pairs.append("%dm" % values.microsecond)
  if not pairs: pairs.append("0s")
  return " ".join(pairs)


class TimedeltaInputWidget(TextWidget):
  """widget for timedelta input.

  The values are space separated concatenations of sign/int/unit tuples.
  *sign* is missing, `+` or '-'.
  *unit* is `d` (day), `s` (second) and `m` (microsecond).
  Examples are `5d 17s`, `300s`, `-5d 17s`, `-5d -17s`.
  """
  # maps `unit` to target, factor pairs
  #  the factors are there to support e.g. hours, minutes, ...
  CONV = dict(d=("d", 1), s=("s", 1), m=("m", 1))

  def _toFieldValue(self, input):
    value = super(TimedeltaInputWidget, self)._toFieldValue(input.strip())
    if value is None: return value
    if value.startswith("-"): neg = True; value = value[1:]
    else: neg = False
    v = dict(d=0, s=0, m=0); conv = self.CONV
    try:
      for pair in value.split():
        nf = 1
        if pair.startswith("-"): nf = -1; pair = pair[1:]
        elif pair.startswith("+"): pair = pair[1:]
        if not pair:
          raise ValueError(_(u"missing unit", u"missing unit"))
        unit = pair[-1]
        if unit not in conv:
          raise ValueError(_(u"unknown unit", u"unknown unit"))
        t, f = conv[unit]
        if len(pair) == 1: pv = 1 # only unit
        else: pv = int(pair[:-1], 10) # explicitely specified
        v[t] += nf * pv * f
      return timedelta(v["d"], v["s"], v["m"])
    except ValueError, v:
      raise ConversionError(_(u"invalid timedelta", u"invalid timedelta"), v)

  def _toFormValue(self, value): return format_timedelta(value)


class TimedeltaDisplayWidget(DisplayWidget):
  __call__ = rebindFunction(DisplayWidget.__call__,
                            escape=lambda x: "<span>%s</span>" % (x and format_timedelta(x))
                            )


##############################################################################
## Decent `Password` support

class PasswordInputWidget(PasswordWidget):
  """Improved `PasswordWidget`.

  The standard Zope `PasswordWidget` replaces the field value by `''`.
  This forces the user to provide a new value each time the form is
  edited. If he forgets it, the password is lost.

  Our `PasswordInputWidget`, too, replaces the value by a fixed constant
  (determined by `TAG_UNCHANGED`). When it gets this value back, it
  treats the password as unchanged. This way, you need to provide
  a password value only when you want to change it.

  Be carefull, however: the value shown on the html page has nothing to
  do with the real password value. When you want to change your password,
  you must provide a completely new value. You cannot just modify some
  characters.
  """

  TAG_UNCHANGED = "**__unchanged__**"

  __call__ = TextWidget.__call__

  def hasInput(self):
    # we trick `zope.formlib` to make the field value available by
    #  pretending to have no input when the input is our unchanged tag
    return super(PasswordInputWidget, self).hasInput() \
           and self._getFormInput() != self.TAG_UNCHANGED

  def _getFormValue(self):
    if self.hasInput(): return self._getFormInput()
    # do not pretend a value is set if it is not
    if not self._renderedValueSet() or not self._data: return ""
    # we have a non empty value -- hide it
    return self.TAG_UNCHANGED

  def _toFieldValue(self, input):
    value = super(PasswordInputWidget, self)._toFieldValue(input.strip())
    if value != self.TAG_UNCHANGED: return value
    elif self._renderedValueSet(): return self._data
    else: return self.context.missing_value


class PasswordDisplayWidget(DisplayWidget):
  __call__ = rebindFunction(DisplayWidget.__call__,
                            escape=lambda x: "<span>%s</span>" % ("*" * len(x))
                            )
  
