from grokcore.viewlet import view
from z3c.form.interfaces import IForm, IDisplayForm
from megrok.pagetemplate import PageTemplate

class BasicForm(PageTemplate):
    view(IForm)

class BasicDisplay(PageTemplate):
    view(IDisplayForm)
