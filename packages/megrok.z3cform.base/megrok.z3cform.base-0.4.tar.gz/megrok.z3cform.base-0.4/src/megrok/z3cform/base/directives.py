import martian
from z3c.form import interfaces


class field(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    validate = martian.validateInterfaceOrClass


class mode(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = interfaces.INPUT_MODE
    validate = martian.validateText


class widget(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    validate = martian.validateInterfaceOrClass


class cancellable(martian.Directive):
    """This directive allows to include/exlude the button cancel.
    The value must be anything that can be evaluated to True or False.
    """
    scope = martian.CLASS
    store = martian.ONCE
    default = False


__all__ = ("field", "mode", "widget", "cancellable")
