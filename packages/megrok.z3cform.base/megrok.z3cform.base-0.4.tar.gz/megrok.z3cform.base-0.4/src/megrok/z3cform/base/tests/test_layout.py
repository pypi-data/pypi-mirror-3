"""
  >>> from zope.app.testing.functional import getRootFolder
  >>> manfred = Mammoth()
  >>> getRootFolder()["manfred"] = manfred 

  >>> from zope import component
  >>> from zope.interface import alsoProvides
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

Add Form

  >>> add = component.getMultiAdapter((manfred, request), name='add')
  >>> print add()
  <html>                                                                           
   <body>
     <div class="layout"><form action="http://127.0.0.1" method="post"
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
  </div>
   </body>
  </html>


Check that fields have been created on the edition page:

  >>> view = component.getMultiAdapter((manfred, request), name='edit')
  >>> view
  <megrok.z3cform.base.tests.test_layout.Edit object at ...>

  If we call the EditPage we found it in the renderd Layout
  
  >>> '<div class="layout">' in view()
  True

If we call the render method we get the edit-page without the layout

  >>> view.render().startswith('<form action="http://127.0.0.1"')
  True 

Does the handy url function works

  >>> view.url()
  'http://127.0.0.1/manfred/edit'

We set in the update method of our EditForm the property updateMaker
to true. 

  >>> view.updateMarker
  True

Now let us try to render the complete edit form

  >>> print view()
  <html>                                                                           
   <body>
     <div class="layout"><form action="http://127.0.0.1" method="post"
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
  </div>
   </body>
  </html>



"""
import megrok.layout
import grokcore.component as grok
import megrok.z3cform.base as z3cform

from z3c.form import button, field
from zope import interface, schema
from zope.app.container.contained import Contained
from zope.schema.fieldproperty import FieldProperty


class IMammoth(interface.Interface):
    name = schema.TextLine(title=u"Name")
    age = schema.Int(title=u"Age")


class Mammoth(Contained, grok.Context):
    interface.implements(IMammoth)
    name = FieldProperty(IMammoth['name'])
    age = FieldProperty(IMammoth['age'])


class MyLayout(megrok.layout.Layout):
    grok.context(Mammoth)


class Add(z3cform.PageAddForm):
    fields = field.Fields(IMammoth)


class Edit(z3cform.PageEditForm):
    fields = field.Fields(IMammoth)

    def update(self):
        self.updateMarker = True


class View(z3cform.PageDisplayForm):
    fields = field.Fields(IMammoth)



def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.base.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
          )
    suite.layer = FunctionalLayer
    return suite 

