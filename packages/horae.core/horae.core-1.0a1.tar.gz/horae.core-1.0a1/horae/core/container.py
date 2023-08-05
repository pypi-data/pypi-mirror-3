import grok

from zope import component

from horae.core import interfaces


class Container(grok.OrderedContainer):
    """ A container for objects implementing IIntId ot ITextId (and having a name attribute)
    """
    grok.implements(interfaces.IContainer)
    grok.baseclass()

    def id_key(self):
        return 'object'

    def add_object(self, obj):
        """ Adds a new object and returns the generated id
        """
        if not hasattr(obj, 'id') or obj.id is None:
            if interfaces.ITextId.providedBy(obj):
                obj.id = component.getUtility(interfaces.ITextIdManager).idFromName(self, obj.name)
            else:
                obj.id = component.getUtility(interfaces.IIntIdManager).nextId(self.id_key())
        self._last = obj
        self[str(obj.id)] = obj
        return obj.id

    def get_object(self, id):
        """ Returns the specified object
        """
        return self[str(id)]

    def del_object(self, id):
        """ Deletes the specified object
        """
        del self[str(id)]

    def objects(self):
        """ Iterator over the contained objects
        """
        return self.values()

    def last(self):
        """ Returns the last added object
        """
        return getattr(self, '_last', None)
