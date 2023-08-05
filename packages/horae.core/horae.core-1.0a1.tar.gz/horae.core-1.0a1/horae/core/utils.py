import math
from datetime import date, timedelta, datetime

from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree

from zope import security
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.i18n import translate

from horae.core import _

_marker = object()


def getRequest(default=_marker, check=True):
    """ Returns the current request implementing
        :py:class:`zope.publisher.interfaces.browser.IBrowserRequest`
        raises a RuntimeError if no request is found and no default
        value is provided
    """
    i = security.management.getInteraction() # raises NoInteraction
    for p in i.participations:
        if not check or IBrowserRequest.providedBy(p):
            return p
    if default is not _marker:
        return default
    raise RuntimeError('Could not find current request.')


def getPrincipal():
    """ Returns the currently used principal or None
    """
    try:
        return getRequest().principal
    except:
        return None


def filterItems(items, permission='horae.View'):
    """ Filters a list of objects by permission
    """
    filtered = []
    for item in items:
        if security.checkPermission(permission, item):
            filtered.append(item)
    return filtered

_cache_id = OIBTree()
_cache = IOBTree()


def findParentByInterface(context, interface, skip=0):
    """ Returns the first found parent of the context implementing the given
        interface, optionally skipping a defined number of matching parents
    """
    id = _cache_id.get((context, interface, skip), _marker)
    if id is _marker:
        id = len(_cache_id)
        _cache_id[(context, interface, skip)] = id
    cached = _cache.get(id, _marker)
    if cached is not _marker:
        return cached
    while context is not None and (not interface.providedBy(context) or skip > 0):
        if interface.providedBy(context):
            skip -= 1
        context = getattr(context, '__parent__', None)
    if interface.providedBy(context):
        _cache[id] = context
        return context
    _cache[id] = None
    return None


def formatDateTime(value, request, format=('dateTime', 'short'), html=True):
    """ Formats the datetime ``value`` using the locale provided by the ``request``
        and the ``format`` provided. HTML output may be disabled by the ``html``
        argument.
    """
    formatter = request.locale.dates.getFormatter(*format)
    if value is None:
        return u''
    formatted = None
    if format[0].startswith('date'):
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        d = value.date() if isinstance(value, datetime) else value
        if d == today:
            formatted = translate(_(u'Today'), context=request)
        elif d == yesterday:
            formatted = translate(_(u'Yesterday'), context=request)
        elif d == tomorrow:
            formatted = translate(_(u'Tomorrow'), context=request)
        if formatted is not None and format[0].lower().endswith('time'):
            timeformatter = request.locale.dates.getFormatter('time', format[1])
            formatted += ' ' + timeformatter.format(value)
    if formatted is None:
        formatted = formatter.format(value)
    if not html:
        return formatted
    formatter = request.locale.dates.getFormatter('dateTime', 'long')
    return '<time datetime="%s" title="%s">%s</time>' % (value.isoformat(), formatter.format(value), formatted)


def formatDateTimeRange(start, end, request, format=('dateTime', 'short'), html=True):
    """ Formats the datetime range (``start``, ``end``) using the locale provided
        by the ``request`` and the ``format`` provided. HTML output may be disabled
        by the ``html`` argument.
    """
    s = start.date() if isinstance(start, datetime) else start
    e = end.date() if isinstance(end, datetime) else end
    start = formatDateTime(start, request, format, html)
    if s == e:
        end = formatDateTime(end, request, ('time', format[1]), html)
    else:
        end = formatDateTime(end, request, format, html)
    return '%s - %s' % (start, end)


def formatHours(value, request):
    """ Formats the ``value`` as a decimal using the locale provided by the ``request``
    """
    if value is None:
        return u''
    formatter = request.locale.numbers.getFormatter('decimal')
    if value == math.floor(value):
        return formatter.format(value, '#,##0;-#,##0')
    return formatter.format(value, '#,##0.00;-#,##0.00')
