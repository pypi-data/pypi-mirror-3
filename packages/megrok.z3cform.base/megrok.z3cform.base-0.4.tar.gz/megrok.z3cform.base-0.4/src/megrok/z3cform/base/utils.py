# -*- coding: utf-8 -*-

from zope.event import notify
from z3c.form import interfaces
from zope.event import notify
from zope.component import getMultiAdapter
from zope.schema.interfaces import IObject
from zope.lifecycleevent import Attributes, ObjectModifiedEvent


def set_fields_data(fields_manager, content, data):
    """Applies the values to the fields, if a change has been made and
    if the field is present in the given fields manager. It returns a
    dictionnary describing the changes applied with the name of the field
    and the interface from where it's from.
    """
    changes = {}
    for name, field in fields_manager.items():

        if name not in data or data[name] is interfaces.NOT_CHANGED:
            continue

        dm = getMultiAdapter((content, field.field), interfaces.IDataManager)
 
        if dm.get() != data[name] or IObject.providedBy(field.field):
            dm.set(data[name])
            changes.setdefault(dm.field.interface, []).append(name)
            
    return changes


def notify_changes(content, changes):
    """Builds a list of descriptions, made of Attributes objects, defining
    the changes made on the content and the related interface.
    """
    if changes:
        descriptions = []
        for interface, names in changes.items():
            descriptions.append(Attributes(interface, *names))
        notify(ObjectModifiedEvent(content, *descriptions))
        return descriptions
    return None


def apply_data_event(fields, content, data):
    """ Updates the object with the data and sends an IObjectModifiedEvent
    """
    changes = set_fields_data(fields, content, data)
    if changes: notify_changes(content, changes)
    return changes


__all__ = ("set_fields_data", "notify_changes", "apply_data_event")
