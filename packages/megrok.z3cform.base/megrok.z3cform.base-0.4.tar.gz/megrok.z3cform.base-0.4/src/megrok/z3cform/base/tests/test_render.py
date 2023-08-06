"""
megrok.z3cform.base render
=====================

basic-setup
-----------

  >>> manfred = Mammoth()
  >>> from zope import component
  >>> from zope.interface import alsoProvides
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

add forms
---------

  >>> add = component.getMultiAdapter((manfred, request), name='add')
  >>> print add()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="form-add">
    <div class="errors">
    </div>
    <p class="documentDescription"></p>
    <input type="hidden" name="camefrom" />
      <div id="edition-fields">
      <div class="field ">
        <label for="form-widgets-name">
          <span>Name</span>
          <span class="fieldRequired" title="Required">
            <span class="textual-info">(Required)</span>
          </span>
        </label>
        <div class="widget"> 
      <input id="form-widgets-name" name="form.widgets.name"
             class="text-widget required textline-field"
             value="" type="text" />
  </div>
      </div>
      <div class="field ">
        <label for="form-widgets-age">
          <span>Age</span>
          <span class="fieldRequired" title="Required">
            <span class="textual-info">(Required)</span>
          </span>
        </label>
        <div class="widget"> 
      <input id="form-widgets-age" name="form.widgets.age"
             class="text-widget required int-field" value=""
             type="text" />
  </div>
      </div>
      </div>
      <div id="actionsView">
        <span class="actionButtons">
  <input id="form-buttons-add" name="form.buttons.add"
         class="submit-widget button-field" value="Add"
         type="submit" />
        </span>
      </div>
  </form>


edit-forms
----------

  >>> edit = component.getMultiAdapter((manfred, request), name='edit')
  >>> print edit() 
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="form-edit">
    <div class="errors">
    </div>
    <p class="documentDescription"></p>
    <input type="hidden" name="camefrom" />
      <div id="edition-fields">
      <div class="field ">
        <label for="form-widgets-name">
          <span>Name</span>
          <span class="fieldRequired" title="Required">
            <span class="textual-info">(Required)</span>
          </span>
        </label>
        <div class="widget"> 
      <input id="form-widgets-name" name="form.widgets.name"
             class="text-widget required textline-field"
             value="" type="text" />
  </div>
      </div>
      <div class="field ">
        <label for="form-widgets-age">
          <span>Age</span>
          <span class="fieldRequired" title="Required">
            <span class="textual-info">(Required)</span>
          </span>
        </label>
        <div class="widget"> 
      <input id="form-widgets-age" name="form.widgets.age"
             class="text-widget required int-field" value=""
             type="text" />
  </div>
      </div>
      </div>
      <div id="actionsView">
        <span class="actionButtons">
  <input id="form-buttons-apply" name="form.buttons.apply"
         class="submit-widget button-field" value="Apply"
         type="submit" />
        </span>
      </div>
  </form>


display-forms
-------------

  >>> index = component.getMultiAdapter((manfred, request), name='index')
  >>> print index()
  <html>
   <body>
     <div class="main">
        <div id="form-widgets-name-row" class="row">
            <div class="label">
              <label for="form-widgets-name">
                <span>Name</span>
              </label>
            </div>
            <div class="widget">
      <span id="form-widgets-name"
            class="text-widget required textline-field"></span>
  </div>
        </div>
        <div id="form-widgets-age-row" class="row">
            <div class="label">
              <label for="form-widgets-age">
                <span>Age</span>
              </label>
            </div>
            <div class="widget">
      <span id="form-widgets-age"
            class="text-widget required int-field"></span>
  </div>
        </div>
      </div>
   </body>
  </html>

"""
import grokcore.component as grok

from zope import interface, schema
from zope.schema.fieldproperty import FieldProperty
from megrok.z3cform import base as z3cform
from z3c.form import field


class IMammoth(interface.Interface):

    name = schema.TextLine(title=u"Name")
    age = schema.Int(title=u"Age")

class Mammoth(grok.Context):
    
    interface.implements(IMammoth)

    name = FieldProperty(IMammoth['name'])
    age = FieldProperty(IMammoth['age'])

class Add(z3cform.AddForm):
    pass

class Edit(z3cform.EditForm):
    pass

class Index(z3cform.DisplayForm):
    pass

def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.base.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

