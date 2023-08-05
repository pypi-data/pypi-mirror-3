from zope import interface
from zope import schema

from horae.lifecycle import _


class ILifecycleAware(interface.Interface):
    """ An object tracking its lifecycle
    """

    creation_date = schema.Datetime(
        title=_(u'Creation date')
    )

    modification_date = schema.Datetime(
        title=_(u'Modification date')
    )

    creator = schema.TextLine(
        title=_(u'Creator')
    )

    modifier = schema.TextLine(
        title=_(u'Modifier')
    )


class ILatest(interface.Interface):
    """ Keeps track of the latest objects modified by a user
    """

    def add(obj):
        """ Add a new object to the list
        """

    def objects(*interfaces):
        """ Iterator of the latest objects modified by the current user optionally
            filtered by interfaces
        """
