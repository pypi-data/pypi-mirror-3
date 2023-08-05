Introduction
============

``horae.lifecycle`` handles the lifecycle of objects for the Horae resource
planning system. It stores the ``creator``, ``creation_date``, ``modifier``
and ``modification_date`` of objects implementing
``horae.lifecycle.interfaces.ILifecycleAware``. Additionally it provides
a viewlet displaying the collected information in context and a storage
for latest objects of a user which tracks what objects were changed by a
given user.

Usage
=====

The easiest way to activate the functionality provided by ``horae.lifecycle``
is to subclass from the provided mix in class ``horae.lifecycle.lifecycle.LifecycleAwareMixin``::

    import grok
    
    from horae.lifecycle import lifecycle
    
    class SampleContent(grok.Model, lifecycle.LifecycleAwareMixin):
        """ Sample content aware of his lifecycle
        """

Latest
------

The latest storage is provided as an adapter implementing ``horae.lifecycle.interfaces.ILatest``
and adapting a principal. There is a convenience adapter adapting the ``request``
available which returns the storage for the current user::

    from horae.lifecycle import interfaces
    
    class SampleView(grok.View):
        
        def latest(self):
            latest = interfaces.ILatest(self.request)
            return latest.objects()

Dependencies
============

Horae
-----

* `horae.auth <http://pypi.python.org/pypi/horae.auth>`_
* `horae.core <http://pypi.python.org/pypi/horae.core>`_
* `horae.layout <http://pypi.python.org/pypi/horae.layout>`_
* `horae.timeaware <http://pypi.python.org/pypi/horae.timeaware>`_

Third party
-----------

* `grok <http://pypi.python.org/pypi/grok>`_
* `zope.principalannotation <http://pypi.python.org/pypi/zope.principalannotation>`_
