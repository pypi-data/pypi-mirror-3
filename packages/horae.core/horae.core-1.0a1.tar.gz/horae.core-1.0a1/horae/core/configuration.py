import grok
from zope import schema
from zope.site.hooks import getSite

from horae.core import interfaces


class AppConfiguration(grok.Model):
    """ Holds application configuration
    """
    grok.implements(interfaces.IAppConfiguration)

    title = schema.fieldproperty.FieldProperty(interfaces.IAppConfiguration['title'])
    description = schema.fieldproperty.FieldProperty(interfaces.IAppConfiguration['description'])
    workdays = schema.fieldproperty.FieldProperty(interfaces.IAppConfiguration['workdays'])
    currency_format = schema.fieldproperty.FieldProperty(interfaces.IAppConfiguration['currency_format'])


@grok.adapter(interfaces.IAppConfigurationHolder)
@grok.implementer(interfaces.IAppConfiguration)
def app_configuration_of_holder(holder):
    if not 'app_configuration' in holder:
        holder['app_configuration'] = AppConfiguration()
    return holder['app_configuration']


class Workdays(grok.GlobalUtility):
    """ Workdays provider
    """
    grok.implements(interfaces.IWorkdays)

    _workdays = None

    def invalidate(self):
        """ Invalidates the cache of the provider
        """
        self._workdays = None

    def workdays(self):
        """ Returns a list of week days to be considered as work days

            0: Monday
            ...
            6: Sunday
        """
        if self._workdays is None:
            app = getSite()
            self._workdays = getattr(interfaces.IAppConfiguration(app), 'workdays', range(0, 6))
        return self._workdays
