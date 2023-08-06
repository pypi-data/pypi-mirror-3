"""
  >>> from zope import component
  >>> from zope.interface import alsoProvides
  >>> from zope.publisher.browser import TestRequest

  >>> otto = Mammoth()

Check that fields have been created on the edition page:

  >>> request = TestRequest(form={'form.widgets.name': u'Karl'})
  >>> view = component.getMultiAdapter((otto, request), name='myform')
  >>> view.updateForm()
  >>> data, errors = view.extractData()
  >>> len(errors) is 1
  True

  >>> errors[0].error.args[0]
  u"Otto's name is otto"

  >>> request = TestRequest(form={'form.widgets.name': u'otto',})
  >>> view = component.getMultiAdapter((otto, request), name='myform')
  >>> view.updateForm()
  >>> data, errors = view.extractData()
  >>> len(errors) is 0
  True

  >>> request = TestRequest(form={'form.widgets.name': u'otto', 'form.widgets.age': '34'})
  >>> view = component.getMultiAdapter((otto, request), name='myform')
  >>> view.updateForm()
  >>> data, errors = view.extractData()
  >>> len(errors) is 1
  True

  >>> print errors[0].render()
  <div class="error">Otto is not 20.</div>


  >>> request = TestRequest()
  >>> view = component.getMultiAdapter((otto, request), name='contextless')
  >>> view.updateForm()
  >>> print view.render()
  <form...
       <input id="form-widgets-age" name="form.widgets.age"
              class="text-widget int-field" value="5"
              type="text" />
  ...
  </form>

Buttons
-------

  >>> request = TestRequest()
  >>> view = component.getMultiAdapter((otto, request), name='buttons')
  >>> view.updateForm()
  >>> print view.render()
  <form...
    <input id="form-buttons-add" name="form.buttons.add"
           class="submit-widget button-field" value="EGON"
           type="submit" />
  ...
  </form> 
"""
import grokcore.component as grok

from z3c.form import util
from zope.interface import Invalid
from zope import interface, schema
from megrok.z3cform.base import AddForm, Form, validator, invariant, default_value, button_label
from zope.schema.fieldproperty import FieldProperty


class IMammoth(interface.Interface):
    name = schema.TextLine(
        title=u"Name",
        required=False
        )

    age = schema.Int(
        title=u"Age",
        required=False,
        )


@validator(field=IMammoth['name'])
def validate_name(value):
    if value != 'otto':
        raise schema.ValidationError(u"Otto's name is otto")


@invariant(schema=util.getSpecification(IMammoth, force=True))
def validate_invariant(obj):
    if obj.age > 20:
        return (Invalid('Otto is not 20.'),)


@default_value(field=IMammoth['age'])
def get_default(data):
    return 5 


class Mammoth(grok.Context):
    interface.implements(IMammoth)

    name = FieldProperty(IMammoth['name'])
    age = FieldProperty(IMammoth['age'])


class MyForm(Form):
    pass


class ContextLess(Form):
    ignoreContext = True


class Buttons(AddForm):
    ignoreContext = True

@button_label(form=Buttons)
def get_widget(data):
    return u"EGON" 
    

def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.base.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

