# -*- coding: utf-8 -*-
from zope import interface
from zope import schema
from zope.component.interfaces import IObjectEvent

from horae.core import _


class IHorae(interface.Interface):
    """ Marker interface for Horae applications
    """


class IApplicationUpgrader(interface.Interface):
    """ An adapter upgrading an application
    """

    def upgrade():
        """ Runs all registered and available :py:class:`IApplicationUpgrade`
        """


class IApplicationUpgrade(interface.Interface):
    """ An application upgrade step
    """

    def available():
        """ Whether this step is available
        """

    def upgrade():
        """ Runs the upgrade and returns a list of strings containing the result
        """


class ITextId(interface.Interface):
    """ An object having a text ID
    """

    id = schema.ASCIILine(
        title=_(u'ID'),
        required=True
    )


class IIntId(interface.Interface):
    """ An object having an integer ID
    """

    id = schema.Int(
        title=_(u'ID'),
        required=True
    )


class ITextIdManager(interface.Interface):
    """ Handles text IDs
    """

    def normalize(name):
        """ Returns a normalized string usable in URLs based on the ``name`` provided
        """

    def idFromName(container, name):
        """ Returns a valid ID for a new object to be added to the ``container``
            from the ``name`` provided
        """


class IIntIdManager(interface.Interface):
    """ Handles integer IDs
    """

    def nextId(key):
        """ Returns the next ID for the given ``key``
        """


class IContainer(interface.Interface):
    """ A container for objects implementing IIntId
    """

    def add_object(obj):
        """ Adds a new object and returns the generated ID
        """

    def get_object(id):
        """ Returns the specified object
        """

    def del_object(id):
        """ Deletes the specified object
        """

    def objects():
        """ Iterator over the contained objects
        """

    def last():
        """ Returns the last added object
        """


class IPriced(interface.Interface):
    """ A priced object
    """

    def price():
        """ The price of this object
        """


class IWorkdays(interface.Interface):
    """ Workdays provider
    """

    def invalidate():
        """ Invalidates the cache of the provider
        """

    def workdays():
        """ Returns a list of week days to be considered as work days

            0: Monday
            ...
            6: Sunday
        """


class IAppConfiguration(interface.Interface):
    """ Holds application configuration
    """

    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'The title of the application'),
        default=u'Horae',
        required=True
    )

    description = schema.TextLine(
        title=_(u'Description'),
        description=_(u'The description of the application'),
        default=u'Next generation resource planning'
    )

    workdays = schema.Set(
        title=_(u'Work days'),
        required=True,
        value_type=schema.Choice(
            vocabulary='horae.core.vocabulary.weekdays'
        ),
        default=set(range(1, 6))
    )

    currency_format = schema.TextLine(
        title=_(u'Currency format'),
        required=True,
        default=u'%s'
    )

    @interface.invariant
    def currencyFormatContainsPlaceholder(app_configuration):
        if not '%s' in app_configuration.currency_format:
            raise interface.Invalid(_(u'The currency format is invalid, please insert «%s» as a placeholder for the value'))


class IAppConfigurationHolder(interface.Interface):
    """ Marker interface for objects adaptable to :py:class:`IAppConfiguration`
    """


class ICurrencyFormatter(interface.Interface):
    """ Formats a given value using the currency format specified in the
        :py:class:`IAppConfiguration`
    """

    def format(value, symbol=True):
        """ Formats the given value
        """


class ISizeFormatter(interface.Interface):
    """ Formats a given value as a size pretended with the appropriate unit (KB, MB, GB)
    """

    def format(value):
        """ Formats the given value (in Bytes)
        """


class IDeferred(interface.Interface):
    """ Utility called after page processing
    """

    def add(obj):
        """ Adds an object to the queue
        """

    def __call__():
        """ Processes the queue
        """

    def clear():
        """ Clear the queue
        """


class IDeferredObjectAdded(IObjectEvent):
    """ Event fired if an object has been added to a :py:class:`IDeferred`
    """


class IDeferredNotifier(IDeferred):
    """ Utility handling deferred notification of events
    """

    def notify_objects(interface):
        """ Notify object events of objects implementing the given interface
        """


class IDeferredNotifierObjectAdded(IDeferredObjectAdded):
    """ Event fired if an object has been added to the :py:class:`IDeferredNotifier`
    """
