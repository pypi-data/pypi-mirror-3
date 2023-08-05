import grok
import logging

from zope import component

from horae.core import interfaces

logger = logging.getLogger('horae.core.upgrade')


class ApplicationUpgrader(grok.Adapter):
    """ An adapter upgrading an application
    """
    grok.context(interfaces.IHorae)
    grok.implements(interfaces.IApplicationUpgrader)

    def log(self, *msgs):
        for msg in msgs:
            self.results.append(msg)
            logger.info(msg)

    def upgrade(self):
        """ Runs all available registered upgrade steps
        """
        steps = component.getAdapters((self.context,), interfaces.IApplicationUpgrade)
        self.results = []
        self.log('*' * 50)
        self.log('STARTING APPLICATION UPGRADE %s' % self.context.__name__)
        for name, step in steps:
            if not step.available():
                continue
            self.log('-' * 50)
            self.log('starting %s' % name)
            self.log('-' * 50)
            try:
                self.log(*step.upgrade())
            except:
                self.log('-' * 50)
                self.log('%s failed' % name)
                self.log('-' * 50)
                continue
            self.log('-' * 50)
            self.log('finished %s' % name)
            self.log('-' * 50)
        self.log('FINISHED APPLICATION UPGRADE')
        self.log('*' * 50)
        return self.results
