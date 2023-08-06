# -*- coding: utf-8 -*-

import grokcore.component as grok

from zope.interface import Interface
from zope.i18nmessageid import MessageFactory
from zope.traversing.browser import AbsoluteURL

from megrok.z3cform.base.directives import cancellable
from megrok.z3cform.base import button, IGrokForm, ICancelButton

_ = MessageFactory("megrok.z3cform")


class CancelButton(button.Button):
    """A cancel button.
    """
    grok.implements(ICancelButton)

    def __init__(self, *args, **kwargs):
        button.Button.__init__(self, *args, **kwargs)
        self.condition = cancellable.bind().get
    

class FormActions(button.ButtonActions, grok.MultiAdapter):
    grok.adapts(IGrokForm, Interface, Interface)

    def update(self):
        self.form.buttons = button.Buttons(
            self.form.buttons,
            CancelButton('cancel', _(u'Cancel'), accessKey=u'c')
            )
        super(FormActions, self).update()


class AddActionHandler(button.ButtonActionHandler, grok.MultiAdapter):
    grok.adapts(IGrokForm, Interface, Interface, button.ButtonAction)

    def __call__(self):
        if self.action.name == 'form.buttons.cancel':
            self.form.redirect(AbsoluteURL(self.form.context, self.request))
            return
        return super(AddActionHandler, self).__call__()

