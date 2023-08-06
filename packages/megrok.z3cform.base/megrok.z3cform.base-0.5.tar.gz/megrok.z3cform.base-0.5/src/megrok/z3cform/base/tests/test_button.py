"""
The Cancel Button
=================

We include with megrok.z3cform per default a Cancel Button.
This test will demonstrate that we will get a this Cancel
Button on our Form and how we can get rid of it.


Setup
-----

Let's start with a simple example. We create a person object:

   >>> from zope.interface import Interface, implements
   >>> from zope.schema import TextLine

The Interface of our Object:

   >>> class IPerson(Interface):
   ...     name = TextLine(title = u'Name')
   ...     age = TextLine(title = u'Age')

The class of our Object:

   >>> class Person(object):
   ...     implements(IPerson)
   ...     name = u""
   ...     age = u""


Now we create an Edit Form for the Person
-----------------------------------------

   >>> from megrok.z3cform.base import EditForm, Fields
   >>> from megrok.z3cform.base.directives import cancellable
   >>> from grokcore.component.testing import grok_component
   >>> from zope.component import getMultiAdapter
   >>> from zope.publisher.browser import TestRequest
   >>> import grokcore.component

   >>> peter = Person()
   >>> request = TestRequest()

   >>> class PersonEditForm(EditForm):
   ...     grokcore.component.context(Interface)
   ...     fields = Fields(IPerson)

   >>> grok_component('personeditform', PersonEditForm)
   True

Let's call the view and look on the buttons,
we should get two buttons.

   >>> personeditform = getMultiAdapter((peter, request), name="personeditform")
   >>> personeditform.update()
   >>> personeditform.updateForm()
   >>> cancel = personeditform.buttons.get('cancel')
   >>> cancel.condition(personeditform)
   False

   >>> personeditform.buttons.keys()
   ['apply', 'cancel'] 


If you need to explicitly remove the use of a Cancel button from a
form, you can remove it by declaring the cancellable directive set to False:

   >>> class YetAnotherForm(EditForm):
   ...     grokcore.component.context(Interface)
   ... 	   cancellable(True)
   ...     fields = Fields(IPerson)

   >>> grok_component('yetanotherform', YetAnotherForm)
   True

Again call the form and look on the buttons.
There should be no Cancel button in it.

   >>> yetanotherform = getMultiAdapter((peter, request),
   ...                                  name="yetanotherform")
   >>> yetanotherform.update()
   >>> yetanotherform.updateForm()
   >>> cancel = yetanotherform.buttons.get('cancel')
   >>> cancel.condition(yetanotherform)
   True 

"""


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.base.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

