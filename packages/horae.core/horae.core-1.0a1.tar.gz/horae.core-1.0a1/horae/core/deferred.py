import grok
import transaction

from BTrees.OOBTree import OOBTree

from zope import component
from zope.event import notify
from zope.component.interfaces import IObjectEvent, ObjectEvent

from grokcore.view.publication import GrokBrowserFactory, GrokBrowserPublication

from horae.core import utils
from horae.core import interfaces


class DeferredObjectAdded(ObjectEvent):
    """ Event fired if an object has been added to a deferred utility
    """
    grok.implements(interfaces.IDeferredObjectAdded)


class BaseQueue(object):
    """ Abstract implementation of a queue
    """

    index_factory = OOBTree
    event_factory = DeferredObjectAdded

    @property
    def _queue(self):
        try:
            request = utils.getRequest(check=False)
            if not hasattr(request, self._queue_attr):
                setattr(request, self._queue_attr, [])
            return getattr(request, self._queue_attr)
        except:
            return None

    @property
    def _index(self):
        try:
            request = utils.getRequest(check=False)
            if not hasattr(request, self._index_attr):
                setattr(request, self._index_attr, self.index_factory())
            return getattr(request, self._index_attr)
        except:
            return None

    def _key(self, obj):
        return obj

    def action(self, obj):
        raise NotImplementedError(u'concrete class must implement action()')

    def add(self, obj):
        """ Adds an object to the queue
        """
        if self._queue is not None and self._index is not None:
            key = self._key(obj)
            if key in self._index:
                if self._index[key] in self._queue:
                    self._queue.remove(self._index[key])
            self._queue.append(obj)
            self._index[key] = obj
            notify(self.event_factory(obj))
        else:
            self.action(obj)

    def clear(self):
        """ Clear the queue
        """
        try:
            request = utils.getRequest(check=False)
            setattr(request, self._queue_attr, [])
            setattr(request, self._index_attr, self.index_factory())
        except:
            pass

    def __call__(self):
        """ Processes the queue
        """
        if self._queue is None:
            return
        while len(self._queue):
            obj = self._queue.pop(0)
            self.action(obj)
            transaction.commit()


class DeferredNotifierObjectAdded(DeferredObjectAdded):
    """ Event fired if an object has been added to the deferred notifier utility
    """
    grok.implements(interfaces.IDeferredNotifierObjectAdded)


class DeferredNotifier(BaseQueue, grok.GlobalUtility):
    """ Utility handling deferred notification of events
    """
    grok.implements(interfaces.IDeferredNotifier)

    _queue_attr = '__horae_core_notifyqueue'
    _index_attr = '__horae_core_notifyindex'
    event_factory = DeferredNotifierObjectAdded

    def _key(self, obj):
        if IObjectEvent.providedBy(obj):
            if interfaces.IIntId.providedBy(obj.object):
                return (obj.__class__.__name__, obj.object.__class__.__name__, obj.object.id)
            return (obj.__class__.__name__, obj.object)
        return obj

    def action(self, obj):
        notify(obj)

    def notify_objects(self, interface):
        """ Notify object events of objects implementing the given interface
        """
        if self._queue is None:
            return
        index = 0
        while len(self._queue) > index:
            if (not IObjectEvent.providedBy(self._queue[index]) or
                not interface.providedBy(self._queue[index].object)):
                index += 1
                continue
            obj = self._queue.pop(index)
            self.action(obj)
            transaction.commit()


class BrowserPublication(GrokBrowserPublication):
    def callObject(self, request, ob):
        result = super(BrowserPublication, self).callObject(request, ob)
        for utility in component.getAllUtilitiesRegisteredFor(interfaces.IDeferred):
            utility()
        return result


class BrowserFactory(GrokBrowserFactory):
    def __call__(self):
        request_class, publication = super(BrowserFactory, self).__call__()
        return request_class, BrowserPublication
