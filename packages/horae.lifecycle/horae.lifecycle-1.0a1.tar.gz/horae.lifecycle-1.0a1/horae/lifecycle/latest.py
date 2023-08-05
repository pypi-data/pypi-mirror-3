import grok

from persistent.list import PersistentList
from persistent.dict import PersistentDict
from BTrees.IOBTree import IOBTree

from zope import interface
from zope import component
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security.interfaces import IPrincipal
from zope.annotation import IAnnotations
from zope.intid.interfaces import IIntIds
from zope.processlifetime import IDatabaseOpenedWithRoot
from zope.app.principalannotation import bootstrap

from horae.core import utils

from horae.lifecycle import interfaces


@grok.subscribe(IDatabaseOpenedWithRoot)
def register_principal_annotation_utility(event):
    bootstrap.bootStrapSubscriber(event)


class Latest(grok.Adapter):
    """ Keeps track of the latest objects modified by a user
    """
    grok.context(IPrincipal)
    grok.implements(interfaces.ILatest)

    _key = 'horae.lifecyle.latest'

    def __init__(self, context):
        super(Latest, self).__init__(context)
        self.annotations = IAnnotations(self.context)
        if self.annotations.get(self._key, None) is None:
            self.annotations[self._key] = PersistentDict()
            self.annotations[self._key]['latest'] = PersistentList()
            self.annotations[self._key]['interfaces'] = IOBTree()
        self.latest = self.annotations[self._key]['latest']
        self.interfaces = self.annotations[self._key]['interfaces']
        self.intid = component.getUtility(IIntIds)

    def add(self, obj):
        """ Add a new object to the list
        """
        intid = self.intid.queryId(obj)
        if intid is None:
            return
        if intid in self.latest:
            self.latest.remove(intid)
            del self.interfaces[intid]
        self.latest.insert(0, intid)
        self.interfaces[intid] = PersistentList()
        for iface in interface.providedBy(obj):
            self.interfaces[intid].append(iface.__identifier__)
            self.interfaces[intid].extend([base.__identifier__ for base in iface.getBases()])

    def objects(self, *interfaces):
        """ Iterator of the latest objects modified by the current user optionally
            filtered by interface
        """
        for intid in self.latest:
            match = not interfaces
            for interface in interfaces:
                if interface.__identifier__ in self.interfaces[intid]:
                    match = True
                    break
            if not match:
                continue
            obj = self.intid.queryObject(intid)
            if obj is not None:
                yield obj


@grok.implementer(interfaces.ILatest)
@grok.adapter(IBrowserRequest)
def latest_of_current(request):
    """ Returns the latest objects of the current user
    """
    return interfaces.ILatest(request.principal)


@grok.subscribe(interfaces.ILifecycleAware, grok.IObjectAddedEvent)
@grok.subscribe(interfaces.ILifecycleAware, grok.IObjectModifiedEvent)
def add_object(obj, event):
    """ Adds objects implementing
        :py:class:`horae.lifecycle.interfaces.ILifecycleAware`
        to the current users latest objects after they where
        added or modified
    """
    try:
        interfaces.ILatest(utils.getRequest().principal).add(obj)
    except:
        pass
