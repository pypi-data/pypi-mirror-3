import grok
from datetime import datetime

from zope import schema

from horae.core import utils
from horae.timeaware.timeaware import DatetimeFieldProperty

from horae.lifecycle import interfaces


class LifecycleAwareMixin(object):
    """ Mix in class for objects tracking their life cycle
    """
    grok.implements(interfaces.ILifecycleAware)

    creation_date = DatetimeFieldProperty(interfaces.ILifecycleAware['creation_date'])
    modification_date = DatetimeFieldProperty(interfaces.ILifecycleAware['modification_date'])
    creator = schema.fieldproperty.FieldProperty(interfaces.ILifecycleAware['creator'])
    modifier = schema.fieldproperty.FieldProperty(interfaces.ILifecycleAware['modifier'])


@grok.subscribe(interfaces.ILifecycleAware, grok.IObjectAddedEvent)
def creation(obj, event):
    """ Stores the current date and principal after an object
        implementing :py:class:`horae.lifecycle.interfaces.ILifecycleAware`
        was added
    """
    obj.creation_date = datetime.now()
    try:
        obj.creator = utils.getRequest().principal.id
    except:
        pass


@grok.subscribe(interfaces.ILifecycleAware, grok.IObjectModifiedEvent)
def modification(obj, event):
    """ Stores the current date and principal after an object
        implementing :py:class:`horae.lifecycle.interfaces.ILifecycleAware`
        was modified
    """
    if grok.IContainerModifiedEvent.providedBy(event):
        return
    obj.modification_date = datetime.now()
    try:
        obj.modifier = utils.getRequest().principal.id
    except:
        pass
