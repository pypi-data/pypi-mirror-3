import grok

from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

from horae.core import interfaces
from horae.core import utils


class CurrencyFormatter(grok.MultiAdapter):
    """ Formats a given value using the currency format specified in the application configuration
    """
    grok.adapts(Interface, IBrowserRequest)
    grok.implements(interfaces.ICurrencyFormatter)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def format(self, value, symbol=True):
        """ Formats the given value
        """
        formatter = self.request.locale.numbers.getFormatter('decimal')
        value = formatter.format(value, '#,##0.00;-#,##0.00')
        parent = utils.findParentByInterface(self.context, interfaces.IAppConfigurationHolder)
        if not symbol or parent is None:
            return value
        try:
            return interfaces.IAppConfiguration(parent).currency_format % value
        except:
            return value
