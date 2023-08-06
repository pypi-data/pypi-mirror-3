# -*- coding: utf-8 -*-

from operator import itemgetter
from rwproperty import getproperty, setproperty

from zope import interface
from zope import component
from zope.publisher.publish import mapply
from zope.pagetemplate.interfaces import IPageTemplate
from z3c.form import form, group

import megrok.layout
import grokcore.view as grok

from megrok.z3cform.base import Fields
from megrok.z3cform.base.interfaces import IGrokForm, IGroup, IGroupForm
from grokcore.view.interfaces import ITemplate as IGrokTemplate


class DefaultFields(Fields):
    """Marker for default fields.
    """


class GrokForm(object):
    """A z3c grok form. This is based on the GrokForm designed for
    Formlib.
    """
    grok.implements(IGrokForm)
    grok.baseclass()

    template = None
    layout = None

    fields = DefaultFields()

    def __init__(self, *args):
        super(GrokForm, self).__init__(*args)
        self.__name__ = self.__view_name__
        self.static = component.queryAdapter(
            self.request, interface.Interface,
            name=self.module_info.package_dotted_name)

    def update(self):
        """Subclasses can override this method just like on regular
        grok.Views. It will be called before any form processing
        happens."""

    def updateForm(self):
        """Update the form, i.e. process form input using widgets.

        On z3c.form forms, this is what the update() method is.
        In grok views, the update() method has a different meaning.
        That's why this method is called update_form() in grok forms.
        """
        super(GrokForm, self).update()

    def _render_template(self):
        assert not (self.template is None)
        if IGrokTemplate.providedBy(self.template):
            return super(GrokForm, self)._render_template()
        return self.template(self)

    def renderForm(self):
        """People don't have to define a render method here, and we
        have to use the one provided by z3c.form (people can provide
        render method in grok), but we have to call the template
        correctly.
        """
        if self.template is None:
            self.template = component.getMultiAdapter(
                            (self, self.request), IPageTemplate)
        return self._render_template()

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            return
        self.updateForm()
        if self.request.response.getStatus() in (302, 303):
            return
        return self.render()


class PageGrokForm(GrokForm):
    """A mixin using GrokForm and providing the rendering mechanisms
    to use megrok.layout components.
    """
    def _render_template(self):
        assert not (self.template is None)
        if IGrokTemplate.providedBy(self.template):
            return super(GrokForm, self)._render_template()
        return self.template(self)

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            return
        self.updateForm()
        if self.request.response.getStatus() in (302, 303):
            return
        if self.layout is None:
            layout = component.getMultiAdapter(
                (self.request, self.context), megrok.layout.ILayout)
            return layout(self)
        return self.layout()


class Form(GrokForm, form.Form, grok.View):
    """Normal z3c form.
    """
    grok.baseclass()


class AddForm(GrokForm, form.AddForm, grok.View):
    """z3c add form.
    """
    grok.baseclass()


class EditForm(GrokForm, form.EditForm, grok.View):
    """z3c edit form.
    """
    grok.baseclass()


class DisplayForm(GrokForm, form.DisplayForm, grok.View):
    """z3c display form.
    """
    grok.baseclass()


class BaseGroupForm(group.GroupForm):
    grok.implements(IGroupForm)
    grok.baseclass()

    _groups = None

    @getproperty
    def groups(self):
        if self._groups is not None:
            return self._groups
        return list(map(itemgetter(1), component.getAdapters(
            (self.context, self.request, self), IGroup)))

    @setproperty
    def groups(self, value):
        self._groups = value


class GroupForm(GrokForm, BaseGroupForm, form.Form, grok.View):
    """Normal z3c form with grouping capabilities
    """
    grok.baseclass()


class AddGroupForm(GrokForm, BaseGroupForm, form.AddForm, grok.View):
    """z3c add form.
    """
    grok.baseclass()


class EditGroupForm(GrokForm, BaseGroupForm, form.EditForm, grok.View):
    """z3c edit form.
    """
    grok.baseclass()


class DisplayGroupForm(GrokForm, BaseGroupForm, form.DisplayForm, grok.View):
    """z3c display form.
    """
    grok.baseclass()


class PageForm(PageGrokForm, form.Form, megrok.layout.Page):
    """Normal z3c form with megrok.layout support.
    """
    grok.baseclass()


class PageAddForm(PageGrokForm, form.AddForm, megrok.layout.Page):
    """z3c add form with megrok.layout support.
    """
    grok.baseclass()

    def _render_template(self):
        assert not (self.template is None)
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        if IGrokTemplate.providedBy(self.template):
            return super(GrokForm, self)._render_template()
        return self.template(self)


class PageEditForm(PageGrokForm, form.EditForm, megrok.layout.Page):
    """z3c edit form with megrok.layout support.
    """
    grok.baseclass()


class PageDisplayForm(PageGrokForm, form.DisplayForm, megrok.layout.Page):
    """z3c display form with megrok.layout support.
    """
    grok.baseclass()


class PageGroupForm(PageGrokForm, BaseGroupForm, form.Form,
                    megrok.layout.Page):
    """Normal z3c form with megrok.layout support.
    """
    grok.baseclass()


class PageAddGroupForm(PageGrokForm, BaseGroupForm,
                       form.AddForm, megrok.layout.Page):
    """z3c add form with megrok.layout support.
    """
    grok.baseclass()

    def _render_template(self):
        assert not (self.template is None)
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        if IGrokTemplate.providedBy(self.template):
            return super(GrokForm, self)._render_template()
        return self.template(self)


class PageEditGroupForm(PageGrokForm, BaseGroupForm,
                   form.EditForm, megrok.layout.Page):
    """z3c edit form with megrok.layout support.
    """
    grok.baseclass()


class PageDisplayGroupForm(PageGrokForm, BaseGroupForm,
                           form.DisplayForm, megrok.layout.Page):
    """z3c display form with megrok.layout support.
    """
    grok.baseclass()


class WidgetTemplate(object):
    pass


class Group(group.Group):
    grok.implements(IGroup)


__all__ = ("Form", "AddForm", "EditForm", "DisplayForm",
           "GroupForm", "AddGroupForm", "EditGroupForm", "DisplayGroupForm",
           "PageForm", "PageAddForm", "PageEditForm", "PageDisplayForm",
           "PageGroupForm", "PageAddGroupForm", "PageEditGroupForm",
           "PageDisplayGroupForm", "Group", "WidgetTemplate", )
