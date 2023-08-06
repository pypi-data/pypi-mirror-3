"""
  >>> manfred = Person()

  >>> from zope import component
  >>> from zope.interface import alsoProvides
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  Check that fields have been created on the edition page:

  >>> view = component.getMultiAdapter((manfred, request), name='edit')
  >>> len(view.fields)
  2

  >>> [field.__name__ for field in view.fields.values()]
  ['name', 'age']

The widget for *name* should show it's normal widget.
Because no CustomWidget is provided for this field.

  >>> view.updateWidgets() 
  >>> print view.widgets['name'].render() 
  <input id="form-widgets-name" name="form.widgets.name"
         class="text-widget required textline-field"
         value="" type="text" /> 

The second field in the edit form *age* should get a custom widget
from the NewTemplateForIntField.

  >>> print view.widgets['age'].render()
  <span> This is custom integer widget for zope.schema.Int Fields </span>

Now let's look on a other view. Here we get a CustomWidget as a result
of the CustomStringTemplate

  >>> view = component.getMultiAdapter((manfred, request), name='view')
  >>> view.updateWidgets() 
  >>> print view.widgets['name'].render()
  <span> Extra Widget </span>

Our CustomTemplate class is configured for the IAdded interface.
Let's check if we get the right template for it.

  >>> view = component.getMultiAdapter((manfred, request), name='add')
  >>> view.updateWidgets() 
  >>> print view.widgets['name'].render()
  <span> Custom Widget </span>
  <input id="form-widgets-name" name="form.widgets.name"
         class="text-widget required textline-field"
         value="" type="text" />

  >>> print view.widgets['age'].render()
  <span> Custom Widget </span>
  <input id="form-widgets-age" name="form.widgets.age"
         class="text-widget required int-field" value=""
         type="text" />

This is an example for a more complex CustomWidget.
It uses view, widget and mode...

  >>> view = component.getMultiAdapter((manfred, request), name='view2')
  >>> view.updateWidgets() 
  >>> print view.widgets['name'].render()
  <span> Custom Text Widget </span>
"""

import megrok.layout
import grokcore.viewlet as grok

from zope import interface, schema
from zope.schema.fieldproperty import FieldProperty
from megrok.z3cform import base as z3cform

from z3c.form import field, interfaces


class IPerson(interface.Interface):
    name = schema.TextLine(title=u"Name")
    age = schema.Int(title=u"Age")


class Person(grok.Context):
    interface.implements(IPerson)

    name = FieldProperty(IPerson['name'])
    age = FieldProperty(IPerson['age'])


class MyLayout(megrok.layout.Layout):
    grok.context(Person)

### Views

class Edit(z3cform.PageEditForm):
    grok.context(Person)
    fields = field.Fields(IPerson)


class View(z3cform.PageDisplayForm):
    grok.context(Person)
    fields = field.Fields(IPerson)


class View2(z3cform.PageDisplayForm):
    grok.context(Person)
    fields = field.Fields(IPerson)


class Add(z3cform.PageAddForm):
    grok.context(Person)
    fields = field.Fields(IPerson)


### Custom Templates

class CustomStringTemplate(z3cform.WidgetTemplate):
    grok.context(Person)
    grok.template('templates/new_string.pt')
    megrok.z3cform.base.directives.mode(interfaces.DISPLAY_MODE)

class CustomTemplate(z3cform.WidgetTemplate):
    grok.context(Person)
    grok.template('templates/custom_string.pt')
    grok.view(interfaces.IAddForm)

class NewTemplateForIntField(z3cform.WidgetTemplate):
    grok.context(Person)
    grok.template('templates/custom_int.pt')
    megrok.z3cform.base.directives.field(schema.interfaces.IInt)

class NewTemplateForTextWidget(z3cform.WidgetTemplate):
    grok.context(Person)
    grok.template('templates/custom_text.pt')
    grok.view(View2)
    megrok.z3cform.base.directives.widget(interfaces.ITextWidget)
    megrok.z3cform.base.directives.mode(interfaces.DISPLAY_MODE)


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.base.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite
