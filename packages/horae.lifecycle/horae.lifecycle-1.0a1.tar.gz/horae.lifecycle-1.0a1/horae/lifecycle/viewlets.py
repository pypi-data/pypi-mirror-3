import grok
import re

from horae.layout import layout
from horae.layout.viewlets import ContentBeforeManager
from horae.layout.interfaces import IDisplayView
from horae.auth.utils import getUser
from horae.auth.interfaces import IUserURL
from horae.core import utils

from horae.lifecycle import interfaces

grok.templatedir('templates')


class Byline(layout.Viewlet):
    """ Renders the creator, creation date, modifier and modification date
        of an object
    """
    grok.viewletmanager(ContentBeforeManager)
    grok.context(interfaces.ILifecycleAware)
    grok.view(IDisplayView)
    grok.order(31)

    def update(self):
        self.creation_date = utils.formatDateTime(self.context.creation_date, self.request, ('dateTime', 'short'))
        self.modification_date = utils.formatDateTime(self.context.modification_date, self.request, ('dateTime', 'short'))
        creator = getUser(self.context.creator)
        self.creator = creator and creator.name or self.context.creator
        self.creator_url = creator and IUserURL(creator, lambda: None)() or None
        modifier = getUser(self.context.modifier)
        self.modifier = modifier and modifier.name or self.context.modifier
        self.modifier_url = modifier and IUserURL(modifier, lambda: None)() or None
