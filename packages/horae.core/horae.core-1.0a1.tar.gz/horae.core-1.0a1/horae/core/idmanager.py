import grok
import re
from threading import Lock

from zope.site.hooks import getSite
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

from horae.core import interfaces

INTID_ANNOTATIONS_KEY = 'horae.core.intid'
int_id_lock = Lock()


class IntIdManager(grok.LocalUtility):
    """ Handles integer IDs
    """
    grok.implements(interfaces.IIntIdManager)

    def __init__(self):
        self._storage = None

    @property
    def storage(self):
        if self._storage is None:
            storage = IAnnotations(getSite())
            if not INTID_ANNOTATIONS_KEY in storage:
                storage[INTID_ANNOTATIONS_KEY] = PersistentDict()
            self._storage = storage[INTID_ANNOTATIONS_KEY]
        return self._storage

    def nextId(self, key):
        """ Returns the next ID for the given ``key``
        """
        int_id_lock.acquire()
        if not key in self.storage:
            self.storage[key] = 0
        self.storage[key] += 1
        id = self.storage[key]
        int_id_lock.release()
        return id


class TextIdManager(grok.GlobalUtility):
    """ Handles text IDs
    """
    grok.implements(interfaces.ITextIdManager)
    re_ws = re.compile(r'\s+')
    re_chars = re.compile(r'[^a-zA-Z0-9-_\.]')

    def normalize(self, name):
        """ Returns a normalized string usable in URLs based on the ``name`` provided
        """
        return self.re_chars.sub('', self.re_ws.sub('_', name)).lower()

    def idFromName(self, container, name):
        """ Returns a valid ID for a new object to be added to the ``container``
            from the ``name`` provided
        """
        id = self.normalize(name)
        if id in container:
            i = 2
            while '%s-%s' % (id, i) in container:
                i += 1
            id = '%s-%s' % (id, i)
        return str(id)
