===================
megrok.z3cform.base
===================

`megrok.z3cform.base` is a not-so-thick layer above `z3c.form`. It
provides a `Grok` way to register your forms and your widgets. In
addition, the package has a collection of base forms, useable
out-of-the box with `megrok.layout`.

The customization of the forms is also eased by the use of
`megrok.pagetemplate`, allowing you to override a template easily.


Form registration
=================

Models
------

We set up some models to serve as a form context::

  >>> import grokcore.component as grok
  >>> from zope import interface, schema

  >>> class IMammoth(interface.Interface):
  ...    name = schema.TextLine(title=u"Name")
  ...    age = schema.Int(title=u"Age")

  >>> class Mammoth(grok.Context):
  ...    grok.implements(IMammoth)
  ...    name = schema.fieldproperty.FieldProperty(IMammoth['name'])
  ...    age = schema.fieldproperty.FieldProperty(IMammoth['age'])

We declare the Form. It's very similar to a grok.View::

  >>> import megrok.z3cform.base as z3cform

  >>> class TestForm(z3cform.Form):
  ...    grok.context(Mammoth)


Grokking and querying
---------------------

We let Grok register the component::

  >>> grok.testing.grok_component('form', TestForm)
  True

Now, we can query it normally::

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> manfred = Mammoth()

  >>> from zope.component import getMultiAdapter
  >>> myform = getMultiAdapter((manfred, request), name="testform")

  >>> myform
  <TestForm object at ...>
  >>> print myform()
  <form action="http://127.0.0.1" method="post"
          enctype="multipart/form-data" class="form-testform">
  ...


Layout integration
------------------

`megrok.z3cform.base` is integrated, out-of-the-box with
`megrok.layout`, providing base classes to ease the layout integration
in your project.

Let's have a quick overview. We create a layout::

  >>> import megrok.layout

  >>> class MyLayout(megrok.layout.Layout):
  ...     grok.context(IMammoth)
  ...     def render(self):
  ...        return 'The layout content is: %s' % self.view.content()

We declare a Page Form. A Page Form is a form that will show up inside
a layout::

  >>> class PageForm(z3cform.PageForm):
  ...    grok.context(Mammoth)

We register the components with Grok::

  >>> grok.testing.grok_component('page', PageForm)
  True
  >>> grok.testing.grok_component('layout', MyLayout)
  True

Now, while rendering the form, we have it embedded in the Layout::

  >>> pageform = getMultiAdapter((manfred, request), name="pageform")
  >>> print pageform()
  The layout content is: <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="form-pageform">
  ...


.. attention:

  This is only a tiny presentation of the package features. Please,
  read the tests for a global overview.
