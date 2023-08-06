# -*- coding: utf-8 -*-

from zope.interface import Interface
from z3c.form.interfaces import IButtonForm, IHandlerForm, IButton


class IGrokForm(IButtonForm, IHandlerForm):
    """A grok z3c form. This marker interface is used to have a
    different default template.
    """


class IGroupForm(IGrokForm):
    pass


class ICancelButton(IButton):
    """A button to cancel a form.
    """


class IGroup(Interface):
    pass


__all__ = ("IGrokForm", "ICancelButton", "IGroup", "IGroupForm")
