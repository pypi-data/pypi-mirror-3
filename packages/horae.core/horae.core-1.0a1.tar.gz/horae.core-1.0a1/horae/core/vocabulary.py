from zope.schema import vocabulary

from horae.cache.vocabulary import cache_global

from horae.core.utils import getRequest


@cache_global
def weekdays_vocabulary_factory(context):
    """ A vocabulary of all days of a week registered as
        **horae.core.vocabulary.weekdays**
    """
    terms = []
    try:
        request = getRequest()
        for id, names in request.locale.dates.calendars['gregorian'].days.items():
            if names[0] is not None:
                terms.append(vocabulary.SimpleTerm(id, id, names[0]))
    except:
        pass
    return vocabulary.SimpleVocabulary(terms)
vocabulary.getVocabularyRegistry().register('horae.core.vocabulary.weekdays', weekdays_vocabulary_factory)
