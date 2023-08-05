import grok

from zope.publisher.interfaces.browser import IBrowserRequest

from horae.core import interfaces

UNITS = ('B', 'KB', 'MB', 'GB',)


class SizeFormatter(grok.Adapter):
    """ Formats a given value as a size appended with the appropriate unit (B, KB, MB, GB)
    """
    grok.context(IBrowserRequest)
    grok.implements(interfaces.ISizeFormatter)

    def format(self, value):
        """ Formats the given value (in Bytes)
        """
        formatter = self.context.locale.numbers.getFormatter('decimal')
        unit = UNITS[0]
        i = 1
        while value > 1024 and i < len(UNITS):
            unit = UNITS[i]
            value /= 1024.0
            i += 1
        return ' '.join((formatter.format(value, '#'), unit))
