import grok

from z3c.objpath.interfaces import IObjectPath
from z3c.objpath import path, resolve


class ObjectPath(grok.GlobalUtility):
    grok.provides(IObjectPath)

    def path(self, obj):
        return path(grok.getSite(), obj)

    def resolve(self, path):
        return resolve(grok.getSite(), path)
